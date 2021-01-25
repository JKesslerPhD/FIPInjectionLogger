from django.shortcuts import render
from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect
from django.db.models.functions import Cast
from django.contrib.auth import authenticate, login
from .models import InjectionLog, GSBrand, Cats, UserGS, SelectedCat
from .models import UserExtension, RelapseDate, ObservationLog, BloodWork, FixTimezone
from .forms import BloodWorkForm
from django.contrib.auth.forms import UserCreationForm
from .forms import AddGS, RegisterForm
from django.db.models.fields import DateField
from django.db.models import F, DurationField, ExpressionWrapper
from .models import WarriorTracker
import re
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import pytz
import hashlib
import csv
import decimal
from django.http import StreamingHttpResponse
import pandas as pd
import statsmodels.formula.api as smf
from django.db import connection
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import os
import json
import math
from cron_data import Database
from gdstorage.storage import GoogleDriveStorage
from django.core.files.base import ContentFile



class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

# Create your views here.

def selected_cat(request):

    if "sharable" in request.GET:
        try:
            cats = Cats.objects.filter(sharable=request.GET["sharable"])
            cats[0]
            return cats[0]
        except:
            return False

    if "selectedcat" not in request.GET:
        try:
            sc = SelectedCat.objects.filter(user=request.user)[0]
            cat_name = sc.cat_name
        except:
            try:
                cat_name = Cats.objects.filter(owner=request.user).order_by('id')[0]
            except:
                return False
        request.GET = request.GET.copy()
        request.GET["selectedcat"] = cat_name.id
    try:
        cat = Cats.objects.filter(owner=request.user).filter(id=request.GET["selectedcat"])[0]
    except:
        return False

    return cat

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("/")
    else:
        form = RegisterForm()

    page = "register"

    return render(request, "registration/register.html", {"form":form,"page":page})


@login_required(login_url='/information')
def main_site(request):
    sc = None
    relapse = None
    cat_quality = ""
    brand_plot = ""

    # Define a local timezone from the IP Address
    tz = get_local_timezone(request)
    timezone.activate(tz)
    local_time = pytz.timezone(tz)
    now = datetime.now(local_time)
    date_stamp = None
    
    unaware = datetime.now()
    try:
        user_defined_tz = FixTimezone.objects.get(owner=request.user).timezone
        tz_list = None
    except:
        user_defined_tz = False
        tz_list = []
        for time in pytz.all_timezones:
            tz_list.append(time)
        
    validcats = Cats.objects.filter(owner=request.user)
    if not SelectedCat.objects.filter(user=request.user).exists():
        if Cats.objects.filter(owner=request.user).exists():
            cat = Cats.objects.filter(owner=request.user).order_by('id')[0]
            sc = SelectedCat(cat_name=cat, user=request.user)
            sc.save()
    else:
        sc = SelectedCat.objects.get(user=request.user)

    if "selectedcat" in request.GET and sc:
        try:
            cat = Cats.objects.filter(owner=request.user).filter(id=request.GET["selectedcat"])[0]
        except:
            cat = Cats.objects.filter(owner=request.user).order_by('id')[0]
        sc = SelectedCat.objects.get(user=request.user)
        sc.cat_name=cat
        sc.save()
    
    brand_plot=cat_stats(sc)

    try:
        ht_val = 220
        if sc.cat_name.cured:
            ht_val=150
        quality = InjectionLog.objects.filter(cat_name=sc.cat_name).order_by("injection_time").filter(
                active=True)
        res = [x.cat_weight for x in quality]
        wt_unit = [x.wt_units for x in quality][0]
        fig = px.line(res, height=ht_val)
        fig.update_xaxes(visible=False, fixedrange=True)
    
        
        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            yaxis_title="Cat's Weight (%s)" % wt_unit,
            margin=dict(t=10,l=10,b=10,r=10)
        )
        
        fig.update_yaxes(
        visible=True, 
        fixedrange=True,
        title_text = "Cat's Weight (%s)" % wt_unit,
        title_font_size = 10)
        
        fig.update_traces(
        hoverinfo='skip',
        hovertemplate=None)
        cat_quality = plot(fig, output_type="div", include_plotlyjs="cdn")
        
    except:
        cat_quality = ""


    try:
        relapse = RelapseDate.objects.filter(cat_name = sc.cat_name).order_by('-relapse_start')[0]
        treatment_duration = now.date()-relapse.relapse_start
        try:
            inj_progress={}
            inj_date = InjectionLog.objects.filter(
                owner=request.user).filter(
                cat_name=sc.cat_name).filter(
                active=True).order_by("-injection_time")[0].injection_time
            date_stamp = local_time.fromutc(inj_date.replace(tzinfo=None))
            inj_date = date_stamp.date() - relapse.relapse_start
            inj_progress["inj_date"] = inj_date.days+1
        except:
            inj_progress = None
    except:
        try:
            treatment_duration = now.date()-sc.cat_name.treatment_start
        except:
            treatment_duration = now.date()-now.date()
        try:
            inj_progress={}
            inj_date = InjectionLog.objects.filter(
                owner=request.user).filter(
                cat_name=sc.cat_name).filter(
                active=True).order_by("-injection_time")[0].injection_time
            date_stamp = local_time.fromutc(inj_date.replace(tzinfo=None))
            inj_date = date_stamp.date() - sc.cat_name.treatment_start
            inj_progress["inj_date"] = inj_date.days+1
        except:
            inj_progress = None




    template ='InjectionLog/home.html'
    page="home"
    if request.user.groups.filter(name="WarriorAdmin").exists():
        grouping="WarriorAdmin"
    else:
        grouping = None
    injections = InjectionLog.objects.filter(owner=request.user)
    return render(request, template, {"page":page, "cat_quality":cat_quality, "brand_plot":brand_plot, "date_stamp":date_stamp, "progress":inj_progress,"sc":sc, "tz":tz, "tz_list":tz_list, "user_defined_timezone":user_defined_tz, "relapse":relapse, "treatment_duration":treatment_duration.days,"grouping":grouping,"validcats":validcats,"time_info":now.utcoffset})

def sharable_hash(cat, user):
    key1 = str(cat).encode('utf-8')
    key2 = str(user).encode('utf-8')
    md5 = hashlib.md5(b"%s-%s" %(key1, key2))
    return md5.hexdigest()

@login_required
def catinfo(request):

    page="catinfo"
    sharable = None
    relapse = None
    validcats = Cats.objects.filter(owner=request.user)
    pattern="^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"
    
    if request.method == "POST":
        if request.POST["CatID"]:

            c = Cats.objects.get(id=request.POST["CatID"])

            if "cured" in request.POST:
                c.cured = True
                c.bad = False
            else:
                c.cured = False
            
            if "bad_outcome" in request.POST:
                c.cured = False
                c.bad = True
            else:
                c.bad = False

            if  "treatmentstart" in request.POST and re.match(pattern,request.POST["treatmentstart"]):
                c.treatment_start = request.POST["treatmentstart"]

            if  "relapse_date" in request.POST and re.match(pattern,request.POST["relapse_date"]):
                c.cured = False
                relapse = RelapseDate(
                    cat_name = c,
                    relapse_start = request.POST["relapse_date"],
                    fip_type = request.POST["FIPTypeRelapse"],
                    ocular = "Ocular_Relapse" in request.POST,
                    neuro = "Neuro_Relapse" in request.POST,
                )

                relapse.save()

            if "extendedtreatment" in request.POST:
                if request.POST["extendedtreatment"]=="":
                    c.extended_treatment = 0
                else:
                    c.extended_treatment = request.POST["extendedtreatment"]



            c.relapse = "relapse" in request.POST
            c.notes = request.POST["notes"]

            if request.POST["warrioradmin"]:
                c.WarriorAdmin = request.POST["warrioradmin"]

            sharable = sharable_hash(c, request.user)
            c.sharable = sharable

            c.save()
            return redirect("/?message=update")


        else:
            if  "treatmentstart" in request.POST and re.match(pattern,request.POST["treatmentstart"]):
                treatment_date = request.POST["treatmentstart"]
            else:
                treatment_date = None
            
            if not re.match(pattern, request.POST["CatBirthday"]):
                return redirect("/catinfo?error=Cat's birthday not entered. Please enter a value.&CatID=0")

            cats = Cats(
                owner = request.user,
                name = request.POST["CatName"],
                birthday = request.POST["CatBirthday"],
                fip_type = request.POST["FIP Type"],
                ocular = "Ocular" in request.POST,
                neuro = "Neuro" in request.POST,
                treatment_start = treatment_date,
                relapse = "realpse" in request.POST,
                WarriorAdmin = request.POST["warrioradmin"],
                notes = request.POST["notes"]
                )
            cats.save()
            sharable = sharable_hash(cats, request.user)
            cats.sharable = sharable
            cats.save()
            return redirect("/?message=success")


    else:
        if "CatID" in request.GET or "sharable" in request.GET:
            try:
                if "CatID" in request.GET and request.GET["CatID"] != "0":
                    cats = Cats.objects.filter(id=request.GET["CatID"]).filter(owner=request.user)

                if  request.GET["CatID"] == "0":
                    cats = [None]

                if "sharable" in request.GET:
                    shared = True
                    cats = Cats.objects.filter(sharable=request.GET["sharable"])
                    try:
                        cats[0]
                    except:
                        return redirect("/?error=Invalid Share Link")

                catnum=1

                try:
                    bw_data = BloodWork.objects.filter(cat_name=cats[0]).filter(active=True)
                    bloodwork = []
                    for result in bw_data:
                        bloodwork.append(result)

                except:
                    bloodwork = None

                try:
                    relapse = RelapseDate.objects.filter(cat_name = cats[0])
                except:
                    relapse=None
            except:
                # Do Cat Sharable Logic to get the cat information
                return redirect("/catinfo")

        else:
            cats = Cats.objects.filter(owner = request.user).all()
            catnum = len(cats)
            bloodwork = None
    try:
        cats[0]
    except:
        return redirect("/catinfo?CatID=0")
    sharable = sharable_hash(cats[0], request.user)
    form = BloodWorkForm(request.POST, request.FILES)
    template = "InjectionLog/catinfo.html"
    return render(request, template, {"page":page, "cats":cats, "relapse":relapse, "sharable":sharable, "catnum":catnum,'form':form,"bloodwork":bloodwork, "validcats":validcats})

def information(request):
    template ='InjectionLog/information.html'
    page="information"
    return render(request, template,{"page":page})

def about(request):
    template ='InjectionLog/about.html'
    page="about"
    return render(request, template,{"page":page})

@login_required
def make_test(request):
    try:
        account = UserExtension.objects.filter(user=request.user).get()
    except:
        account = UserExtension(user = request.user)

    if request.method=="POST":
        if "activate_test" in request.POST:
            account.test_account = True
            account.save()
        else:
            account.test_account = False
            account.save()



    return render(request, "InjectionLog/test_account.html", {"enabled":account})


@login_required
def calculatedosage(request):

    template ='InjectionLog/dosecalc.html'
    page="dose"
    drugs = GSBrand.objects.all().order_by('brand')
    return render(request, template, {"page":page, "dose":True, "drugs":drugs})

def logout_view(request):
    logout(request)
    return redirect("/")

@login_required
def delete_injection(request):
    if "delete_id" not in request.GET:
        return redirect("/?error=No record ID was specified")

    try:
        cat = Cats.objects.filter(owner=request.user).filter(id=request.GET["selectedcat"])[0]
    except:
        try:
            cat = Cats.objects.filter(owner=request.user).order_by('id')[0]
        except:
            return redirect("/?error=Problem finding cat for your account")

    try:
        log_type = request.GET["log"]
    except:
        return redirect("/?error=No log specified")

    try:
        if log_type == "observationlog":
            q = ObservationLog.objects.filter(owner=request.user).filter(cat_name=cat).filter(id=request.GET["delete_id"]).get()

        if log_type == "log":
            q = InjectionLog.objects.filter(owner=request.user).filter(cat_name=cat).filter(id=request.GET["delete_id"]).get()

        if log_type == "bloodwork":
            q = BloodWork.objects.filter(cat_name=cat).filter(id=request.GET["delete_id"]).get()
            q.bloodwork.delete()


        if log_type == "tracker":
            q = WarriorTracker.objects.filter(user=request.user).filter(id=request.GET["delete_id"]).delete()
            return redirect("/trackwarrior")

    except:
        return redirect("/?error=You do not have access to this resource")

    q.active=False
    q.save()

    if log_type == "bloodwork":
        return redirect("/catinfo/?message=update&CatID=%s" % (cat.id))

    return redirect("/%s/?message=update&selectedcat=%s&q=%s" % (log_type, cat.id,q.id))

@login_required
def add_gs(request):

    page="add_gs"

    if request.method == "POST":
        form = AddGS(request.POST)
        if form.is_valid():
            if request.user.groups.filter(name="WarriorAdmin").exists():
                user_gs = GSBrand(
                    brand = request.POST["GSBrand"],
                    concentration = request.POST["GSConcentration"],
                    admin_method = request.POST["GSAdmin"],
                    price = request.POST["GSPrice"])
            else:
                user_gs = UserGS(
                    user = request.user,
                    brand = request.POST["GSBrand"],
                    concentration = request.POST["GSConcentration"],
                    admin_method = request.POST["GSAdmin"],
                    price = request.POST["GSPrice"])
            user_gs.save()
            return redirect("/?message=success")

    else:
        form = AddGS()
        template ='InjectionLog/injlog.html'

    return render(request, 'InjectionLog/add_gs.html',{'page':page,'form':form})

@login_required
def recordinjection(request):


    template ='InjectionLog/dosecalc.html'
    page="injection"
    ns=False
    drugs = GSBrand.objects.all().order_by('brand')
    userGS = UserGS.objects.filter(user=request.user)
    local_time = get_local_timezone(request)
    tz = pytz.timezone(local_time)
    cat_name = selected_cat(request)
    if not cat_name:
        return redirect("/?error=Please add a cat to your account first")

    try:
        latest_data = InjectionLog.objects.filter(owner=request.user).filter(cat_name=cat_name).order_by('-injection_time')[0]
        try:
            gs_brand = GSBrand.objects.get(brand=latest_data.gs_brand)
        except:
            gs_brand = UserGS.objects.get(brand=latest_data.gs_brand, user=request.user)

        conc = gs_brand.concentration
        dose = round(conc*latest_data.injection_amount/latest_data.cat_weight*decimal.Decimal(2.204),0)
        request.GET = request.GET.copy()
        request.GET["selectedcat"] = cat_name.id

        request.GET["CatWeight"] = latest_data.cat_weight
        request.GET["brand_value"] = gs_brand.brand
        if latest_data.wt_units == "kg":
            request.GET["weight_units"]=True
            dose = int(round(conc*latest_data.injection_amount/latest_data.cat_weight,0))

        request.GET["GSDose"] = dose
    except:
        pass

    validcats = Cats.objects.filter(owner=request.user)
    if request.method == "POST":

        user   = request.user
        cat = Cats.objects.get(id=request.POST["selectedcat"])
        weight = request.POST["CatWeight"]
        brand  = request.POST["brand_value"]
        date = request.POST["inj_date"]
        try:
            i_date = tz.localize(datetime.strptime(date,"%Y-%m-%d %I:%M %p"))
        except:
            return render(request, template, {"page":page,"dose":True,"local_time":local_time, "drugs":drugs,"userGS":userGS, "validcats":validcats,"error":"Invalid Date Time Format Entered. Must be YYYY-MM-DD HH:MM AM/PM"})
        rating = request.POST["cat_rating"]
        amount = request.POST["calculateddose"]
        i_note = request.POST["injectionnotes"]
        o_note = request.POST["othernotes"]
        
        if float(weight) > 30:
            return render(request, template, {"page":page,"dose":True,"local_time":local_time, "drugs":drugs,"userGS":userGS, "validcats":validcats,"error":"You entered a weight for your cat that appears unrealistic.  Please check your weight and units, and try again"})
            
        
        if float(amount) > 30:
            return render(request, template, {"page":page,"dose":True,"local_time":local_time, "drugs":drugs,"userGS":userGS, "validcats":validcats,"error":"The calculated dose appears to be too large or incorrect.  Please check that you have entered a correct weight, and press 'calculate'.  If this problem persists, report a bug."})
            
            
        if "new_symptom" in request.POST:
            newsymptom = request.POST["symptom_details"]
            if newsymptom!="":
                ns = True
        else:
            newsymptom = ""
            ns = False

        if "gabadose" in request.POST:
            gabadose = request.POST["gabadose"]
        else:
            gabadose = None

        unit = "lb"
        if "weight_units" in request.POST:
            unit="kg"


        q = InjectionLog.objects.filter(owner = user).filter(cat_name = cat).filter(active=True)
        for row in q:
            difference = i_date - row.injection_time
            if difference.total_seconds() < 12*60*60 and difference.total_seconds() > 0 and "multi_entry" not in request.POST:
                request.GET = request.POST
                return render(request, template, {"page":page,"dose":True,"local_time":local_time, "drugs":drugs,"userGS":userGS, "validcats":validcats,"error":"The injection date and time entered is too close to a previous injection. Select 'allow multiplie entires' if this is correct"})

        log = InjectionLog(
                owner = user,
                gs_brand = brand,
                cat_name = cat,
                cat_weight= weight,
                injection_time = i_date,
                injection_amount = amount,
                cat_behavior_today = rating,
                injection_notes = i_note,
                gaba_dose = gabadose,
                new_symptom=newsymptom,
                other_notes = o_note,
                wt_units = unit)
        log.save()

        if cat.treatment_start is None:
            cat.treatment_start = i_date.date()
            cat.save()

        return redirect("/?message=success&weight=%s&unit=%s&ns=%s" % (weight,unit,ns))


    return render(request, template, {"page":page, "local_time":local_time, "dose":True,"drugs":drugs,"userGS":userGS, "validcats":validcats})

@login_required
def injectionlog(request):
    validcats = Cats.objects.filter(owner=request.user)
    cat = selected_cat(request)
    local_time = get_local_timezone(request)

    if not cat:
        return redirect("/?error=No data has been recorded...")

    template ='InjectionLog/injlog.html'
    page="log"
    
    treatment_start = cat.treatment_start
    if "sharable" not in request.GET:
        sharable = False

        injections = InjectionLog.objects.filter(
            owner=request.user).filter(
            cat_name=cat).filter(
            active=True).annotate(
            inj_date = ExpressionWrapper(Cast(F('injection_time'), DateField())-F('cat_name__treatment_start'),output_field=DurationField())).order_by('injection_time')
    else:
        sharable = True
        injections = InjectionLog.objects.filter(
            cat_name=cat).filter(
            active=True).annotate(
            inj_date = ExpressionWrapper(Cast(F('injection_time'), DateField())-F('cat_name__treatment_start'),output_field=DurationField())).order_by('injection_time')

    if "export" in request.GET:
        """
        Export the log files as a csv
        """

        # Generate a sequence of rows. The range is based on the maximum number of
        # rows that can be handled by a single sheet in most spreadsheet
        # applications.
        csv_file = [[
            "GS Brand",
            "Cat Weight",
            "Units",
            "Injection Date",
            "Injection Amount (mL or pills)",
            "Cat Behavior (1-5)",
            "Injection Notes",
            "Gaba Dose (mL)",
            "Other Notes",
            "New Symptoms"]]

        for row in injections:
            csv_file.append([
                row.gs_brand,
                row.cat_weight,
                row.wt_units,
                row.injection_time,
                row.injection_amount,
                row.cat_behavior_today,
                row.injection_notes,
                row.gaba_dose,
                row.other_notes,
                row.new_symptom
            ])

        date_format = datetime.now()
        filename="InjectionLog_%s_%s.csv" % (cat.name, date_format.strftime("%Y-%m-%d"))
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in csv_file),
                                        content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


    return render(request, template, {"page":page, "treatment_start":treatment_start, "injections":injections, "local_time":local_time, "validcats":validcats, "cat":cat, "sharable":sharable})

def change_record(request):
    if request.method == "POST":
        local_time = get_local_timezone(request)
        tz = pytz.timezone(local_time)
        i_date = request.POST["inj_date"]
        try:
            i_date = datetime.strptime(i_date,"%Y-%m-%d %I:%M %p")
        except:
            return redirect("/log/?error=Invalid Date Format Entered&selectedcat=%s" % request.POST["cat_name"])
        record = InjectionLog.objects.get(id=request.POST["inj_id"])
        record.injection_time = timezone.make_aware(i_date,tz,True)
        record.cat_behavior_today = request.POST["cat_rating"]
        record.injection_amount = request.POST["injection_amount"]
        record.new_symptom = request.POST["new_symptom"]
        record.injection_notes = request.POST["injection_notes"]
        record.other_notes = request.POST["other_notes"]
        record.gaba_dose = request.POST["gaba_dose"]

        record.save()
        return redirect("/log/?message=update&selectedcat=%s" % request.POST["cat_name"])


@login_required
def observation_log(request):

    # Define a local timezone from the IP Address
    tz = get_local_timezone(request)
    timezone.activate(tz)
    now = timezone.make_aware(datetime.now())

    validcats = Cats.objects.filter(owner=request.user).filter(treatment_start__lte=(now-timedelta(days=84)))
    cat = selected_cat(request)

    if not cat:
        return redirect("/?error=No data has been recorded...")



    template ='InjectionLog/observation_log.html'
    page="log"

    try:
        relapse = RelapseDate.objects.filter(cat_name = cat).order_by('-relapse_start')[0]
        treatment_duration = now.date()-relapse.relapse_start
        relapse = relapse.relapse_start
    except:
        relapse = cat.treatment_start
        treatment_duration = now.date()-cat.treatment_start



    observations = ObservationLog.objects.filter(
        owner=request.user).filter(
        cat_name=cat).filter(
        active=True)



    return render(request, template, {"page":page,"relapse":relapse, "treatment_duration":treatment_duration, "observations":observations,"validcats":validcats, "cat":cat})



@login_required
def record_observation(request):
    validcats = Cats.objects.filter(owner=request.user)
    template = "InjectionLog/record_observation.html"

    if request.method == "POST":

        user   = request.user
        cat = Cats.objects.get(id=request.POST["selectedcat"])
        weight = request.POST["CatWeight"]
        wt_units = request.POST["weight_units"]
        obs_date = request.POST["observation_date"]
        rating = request.POST["cat_rating"]
        temperature = request.POST["temperature"]
        temp_units = request.POST["temp_units"]
        notes = request.POST["notes"]

        if temperature == "":
            temperature = None
        if weight == "":
            weight = None


        log = ObservationLog(
                owner = user,
                cat_name = cat,
                cat_weight= weight,
                wt_units = wt_units,
                observation_date = obs_date,
                temperature = temperature,
                temp_units = temp_units,
                cat_behavior_today = rating,
                notes = notes)
        log.save()
        return redirect("/?message=success")

    cat = selected_cat(request)

    if not cat:
        return redirect("/?error=Please add a cat to your account first")

    request.GET = request.GET.copy()
    request.GET["selectedcat"] = cat.id


    return render(request,template, {"validcats":validcats})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def upload_file(request):
    if request.method == 'POST':
        targetDir = "/var/www/fip/SlayFIP/temporary_uploads/"+request.user.username
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        
        if 'ajax_call' in request.POST:  
            fileName = request.POST['fileName']     # you receive the file name as a separate post data
            fileSize = request.POST['fileSize']          # you receive the file size as a separate post data
            fileId = request.POST['fileId']              # you receive the file identifier as a separate post data
            index =  request.POST['chunkIndex']          # the current file chunk index
            totalChunks = int(request.POST['chunkCount'])     # the total number of chunks for this file
            file_chunk = request.FILES['fileBlob']
            target_file = targetDir +"/"+fileName
            outfile = targetDir+"/"+fileName
        
            target_file = target_file + "_" +str(index)
            
            if(chunk_handler(file_chunk,target_file)):
                chunks = get_chunk_list(targetDir,fileName+"_")
                allChunksUploaded = len(chunks) == totalChunks
                if allChunksUploaded:
                    combineChunks(chunks, outfile, cleanup=True)
                    request.session['fileName'] = fileName
    
            return_values = {
                'chunkIndex': index,
                'initialPreviewConfig':
                    {
                        'type':'other',
                        'caption': fileName,
                        'key':fileId, 
                        'fileId': fileId,
                        'size': fileSize,
                    },
                'append': True}
    
            return StreamingHttpResponse(json.dumps(return_values))
    if "google_drive_upload" in request.POST:
        if not request.session["fileName"]:
            return redirect("/catinfo/?error=Unable to find file to upload")
        fileName = request.session["fileName"]
        outfile = targetDir+"/"+fileName
        file_blob = ContentFile(open(outfile,'rb').read())
        storage = GoogleDriveStorage()
        path = storage.save('FIPlog/'+fileName,file_blob)
        cat = Cats.objects.get(id=request.POST["cat_name"])
        foo = BloodWork(
        bloodname = request.POST["bloodname"],
        cat_name = cat,
        bloodwork_date = request.POST["bloodwork_date"],
        notes = request.POST["notes"],
        bloodwork = path,
        
        )
        foo.save()
        # Cleanup Temp Files in User's upload folder
        for filename in os.listdir(targetDir):
            file_path = os.path.join(targetDir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        
        return redirect("/catinfo/?message=success&CatID="+request.POST["cat_name"])
    else:
        form = BloodWorkForm()

    return redirect('/catinfo')

def get_chunk_list(mypath, slug):
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return [mypath+"/"+x for x in onlyfiles if slug in x]
    
def chunk_handler(data,targetfile):
    with open(targetfile, 'wb+') as destination:
        for chunk in data.chunks():
            destination.write(chunk)
    return True

def combineChunks(chunk_list, outFile, cleanup=False):
    with open(outFile, 'wb+') as destination:
        for chunk in chunk_list:
            content = open(chunk,'rb').read()
            destination.write(content)
            
    if cleanup:
        for chunk in chunk_list:
            os.remove(chunk)
        
            

def load_file(request):
    cat = Cats.objects.get(id=8)
    data = BloodWork.objects.filter(cat_name=cat)
    bloodwork = []
    for result in data:
        bloodwork.append(result)
    django_file = bloodwork[0]


    t ='InjectionLog/view_file.html'
    gd_storage = None
    return render(request, t, {'file':django_file, "data": bloodwork, 'storage':gd_storage})

def parse_sharable_url(url):
    pattern = "^(.*)([a-z0-9]{32})$"
    try:
        share_hash = re.match(pattern, url).groups()[1]
        cat = Cats.objects.get(sharable = share_hash)
        return share_hash
    except:
        return False

@login_required
def track_warrior(request):
    if request.method == "POST":
        share_hash = parse_sharable_url(request.POST["share_link"])
        share_name = request.POST["identifier"]
        
        exist = WarriorTracker.objects.filter(user = request.user).filter(md5hash=share_hash).count()
        if exist > 0:
            return redirect("/trackwarrior/?error=You already following this cat")
            

        if len(share_name)<=1:
            return redirect("/trackwarrior/?error=Please enter a longer name to identify this cat")

        if share_hash:
            sh = WarriorTracker(
            user = request.user,
            md5hash = share_hash,
            identifier = share_name)
            sh.save()
            return redirect("/trackwarrior/?message=success")
        else:
            return redirect("/trackwarrior/?error=Invalid Sharing Link")

    tracking = WarriorTracker.objects.filter(user = request.user)


    return render(request, "InjectionLog/tracker.html",{"tracking":tracking})

def data_analysis(request):
    """
    Generate weight and dosing tables for cats
    """

    filename = os.path.dirname(settings.DATABASES['default']['NAME'])+"/data_output.txt"
    with open(filename) as json_file:
        data = json.load(json_file)

    fip_div = data["fip_stats"]["graph"]
    total_cats = data["fip_stats"]["total_cats"]
    wt_div = data["weight"]["graph"]
    age_div = data["summary"]["graph"]
    duration_div = data["distribution"]["graph"]
    past_initial_treatment = data["distribution"]["total_cats"]
    cured_cats = data["distribution"]["cured_cats"]
    cat_quality = data["quality"]["graph"]
    brand_div = data["brands"]["graph"]


    return render(request, "InjectionLog/data_analysis.html",{"page":"data","brand_stats":brand_div, "duration_fig":duration_div, "cat_quality":cat_quality, "cured_cats":cured_cats, "84_cats":past_initial_treatment,"age_fig":age_div,"fip_fig":fip_div,"wt_fig":wt_div, "dry_cases":total_cats["0"],"wet_cases":total_cats["1"]})

def vet_info(request):
    return render(request,"InjectionLog/vet_info.html",{"page":"vetinfo"})

def brands(request):
    return render(request,"InjectionLog/brands.html",{"page":"brands"})

def error_create(requests):
    return render(requests, "InjectionLog/error_create.html")

def costs(request):
    """
    View to do the number crunching
    """
    filename = os.path.dirname(settings.DATABASES['default']['NAME'])+"/data_output.txt"
    with open(filename) as json_file:
        data = json.load(json_file)

    model = data["weight"]["model"]

    ints = model["ints"]
    daily_price = model["daily_price"]
    stwt = model["stwt"]
    mult = model["mult"]
    age  = model["age"]

    total_cost = 0
    total_vol  = 0

    table = []

    if "CatWeight" in request.GET and "FIPType" in request.GET and "CatAge" in request.GET:
        
        if request.GET["FIPType"]=="dry":
            dosage=10
        else:
            dosage=6
        try:
            wt = float(request.GET["CatWeight"])
            ct_age = float(request.GET["CatAge"])
        except:
            return redirect("/costs/?error=Error: Please enter a Cat's Weight and Age")
        for i in range(85):
            calc_wt = round((mult*i+stwt*wt+ints+1+age*ct_age)*wt,1)
            if calc_wt>wt:
                use_wt = calc_wt
            else:
                use_wt = wt
            if i>0:
                amount = round(use_wt/2.2*dosage/15,2)
                price = round(daily_price*use_wt/2.2*dosage,0)
            else:
                price  = 0
                amount = 0

            total_vol  = total_vol + amount
            total_cost = total_cost + price
            table.append(
                {"price": "$%.2f" % price,
                "weight":use_wt,
                "amount":"%.2f mL" % amount
                })

    params = "Percent Change from Start = %f x [treatment day] + %f x [starting weight] + %f [cat age]" % (mult,stwt, age)

    return render(request, "InjectionLog/costs.html",{"page":"costs", "model":mult, "amount":math.ceil(total_vol/5/.96), "loop":table,"total_cost":"${:.2f}".format(round(total_cost/100,0)*100), "params":params})

def get_local_timezone(request):
    import requests
    if "tz" in request.session:
        return request.session["tz"]
    
    try:
        user_defined_tz = FixTimezone.objects.get(owner=request.user).timezone
        request.session["tz"] = user_defined_tz
        return request.session["tz"]
    except:
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip == "127.0.0.1":
            ip = "72.105.141.28"
        try:
            ipinfo = requests.get('http://ip-api.com/json/%s' % ip)
            ipinfo = ipinfo.json()
            tz = ipinfo["timezone"]
        except:
            tz = "UTC"
        request.session["tz"] = tz
        return tz

def cat_stats(sc):
    import numpy as np
    
    data = Database()
    quality     = data.get_cat_quality()
    this_cat = pd.DataFrame()
    
    results = quality.groupby(['week']).agg(
        behavior = pd.NamedAgg(column='cat_behavior_today', aggfunc=np.mean),
        stdev = pd.NamedAgg(column='cat_behavior_today',aggfunc=np.std),
        be_max = pd.NamedAgg(column='cat_behavior_today',aggfunc=np.max),
        be_min = pd.NamedAgg(column='cat_behavior_today',aggfunc=np.min),
        records=pd.NamedAgg(column='cat_behavior_today', aggfunc='count')
        )
    results.reset_index(inplace=True)
    sem  = results["stdev"]
    x=results["week"].tolist()
    y=results["behavior"].to_list()
    upper = y+sem.fillna(0)
    lower = y-sem.fillna(0)
    upper = upper.tolist()
    lower = lower.tolist()
    try:
        treatment = sc.cat_name.treatment_start
    except:
        return None
    quality = InjectionLog.objects.filter(cat_name=sc.cat_name).order_by("injection_time").filter(
                active=True)
    res = [x.cat_behavior_today for x in quality]
    res_x = [x.injection_time.date() - treatment for x in quality]
    res_x = [np.ceil(x.days/7) for x in res_x]
    try:
        max(res_x)
    except:
        return None
    if max(res_x) == 1:
        return None
    this_cat["x"] = res_x
    this_cat["y"] = res
    this_cat = this_cat.groupby(["x"]).agg(
        quality=pd.NamedAgg(column="y", aggfunc=np.mean))
    this_cat.reset_index(inplace=True)
    
    fig = go.Figure([
        go.Scatter(
            x=x,
            y=y,
            showlegend=False,
            line=dict(color='rgb(0,100,80,.4)'),
            hoverinfo='skip',
            mode='lines' 
            
        ),
        go.Scatter(
            x=this_cat["x"],
            y=this_cat["quality"],
            line=dict(color='rgb(100,100,80)'),

            hoverinfo='skip',
            mode='markers',
            name=sc.cat_name.name,
        ),
        go.Scatter(
            x=x+x[::-1], # x, then x reversed
            y=upper+lower[::-1], # upper, then lower reversed
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name="Average Cat"
        )
    ])
    
    
    fig.update_layout( 
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01),
    margin=dict(l=0, r=0, t=0, b=0),
    yaxis_title="Cat Quality (1-5)", xaxis_title="Week Number",
    xaxis=dict(range=[1,max(res_x)+.2]))
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    
    quality_plot = plot(fig, output_type="div", include_plotlyjs="cdn")

    return quality_plot
    
def fix_timezone(request):
    if request.method != "POST":
        return redirect("/?error=Action Unavailable")
        
    objects = []
    try:
        timezone = FixTimezone.objects.get(owner = request.user)
        return redirect("/?error=User timezone already set as %s" % timezone)
    except:
        time_string = request.POST["user_tz"]
        tz = pytz.timezone(time_string)
        cutoff = datetime.strptime("10/25/2020 23:59", "%m/%d/%Y %H:%M")
        for cat in Cats.objects.filter(owner = request.user):
            objects.append(cat.id)
            logs = InjectionLog.objects.filter(cat_name=cat.id)
            for log in logs:
                injection_time = log.injection_time.replace(tzinfo=None)
                if injection_time > cutoff:
                    continue
                log.injection_time=tz.localize(injection_time)
                log.save()
                
        user_time = FixTimezone(
            owner = request.user,
            fixed = True,
            timezone = time_string)
        user_time.save()
                
        return redirect("/?message=success")
            
        

    
