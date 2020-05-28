from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from django.db.models.functions import Cast
from django.contrib.auth import authenticate, login
from .models import InjectionLog, GSBrand, Cats, UserGS, SelectedCat
from .models import UserExtension, RelapseDate
from django.contrib.auth.forms import UserCreationForm
from .forms import AddGS, RegisterForm
from django.db.models.fields import DateField
from django.db.models import F, DurationField, ExpressionWrapper
import re
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

import decimal

# Create your views here.

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
    
    return render(request, "registration/register.html", {"form":form})

def main_site(request):
    if not request.user.is_authenticated:
        return redirect("/information")
        
    sc = None
    relapse = None
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
           
    
    try:
        relapse = RelapseDate.objects.filter(cat_name = sc.cat_name).order_by('-relapse_start')[0]
        treatment_duration = datetime.now().date()-relapse.relapse_start
        try:
            inj_progress={}
            inj_date = InjectionLog.objects.filter(
                owner=request.user).filter(
                cat_name=sc.cat_name).filter(
                active=True).order_by("-injection_time")[0].injection_time.date() - relapse.relapse_start
            inj_progress["inj_date"] = inj_date.days

        except:
            inj_progress = None

    except:
        try:
            treatment_duration = datetime.now().date()-sc.cat_name.treatment_start
        except:
            treatment_duration = datetime.now().date()-datetime.now().date()
        try:
            inj_progress={}
            inj_date = InjectionLog.objects.filter(
                owner=request.user).filter(
                cat_name=sc.cat_name).filter(
                active=True).order_by("-injection_time")[0].injection_time.date() - sc.cat_name.treatment_start
            inj_progress["inj_date"] = inj_date.days
        except:
            inj_progress = None
    

        
                        
    template ='InjectionLog/home.html'
    page="home"
    if request.user.groups.filter(name="WarriorAdmin").exists():
        grouping="WarriorAdmin"
    else:
        grouping = None
    injections = InjectionLog.objects.filter(owner=request.user)
    return render(request, template, {"page":page, "progress":inj_progress,"sc":sc, "treatment_duration":treatment_duration.days,"grouping":grouping,"validcats":validcats})

def catinfo(request):
    if not request.user.is_authenticated:
        return redirect("/information")
    
    page="catinfo"
    relapse = None
    validcats = Cats.objects.filter(owner=request.user)
    pattern = "[0-9]{4}\-[0-9]{2}\-[0-9]{2}"
    if request.method == "POST":
        if request.POST["CatID"]:


            c = Cats.objects.get(id=request.POST["CatID"])
            
            if  "treatmentstart" in request.POST and re.match(pattern,request.POST["treatmentstart"]):
                c.treatment_start = request.POST["treatmentstart"]
            
            if  "relapse_date" in request.POST and re.match(pattern,request.POST["relapse_date"]):
                relapse = RelapseDate(cat_name = c,  relapse_start = request.POST["relapse_date"])
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
                
            c.save()
            return redirect("/?message=update")

            
        else:
            if  "treatmentstart" in request.POST and re.match(pattern,request.POST["treatmentstart"]):
                treatment_date = request.POST["treatmentstart"]
            else:
                treatment_date = None
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
            return redirect("/?message=success")
        
    else:
        if "CatID" in request.GET:
            try:
                cats = Cats.objects.filter(id=request.GET["CatID"])
                catnum=1
                try:
                    relapse = RelapseDate.objects.filter(cat_name = cats[0])
                except:
                    relapse=None
            except:
                return redirect("/catinfo")
            
        else:
            cats = Cats.objects.filter(owner = request.user).all()
            catnum = len(cats)
    
    template = "InjectionLog/catinfo.html"
    return render(request, template, {"page":page, "cats":cats, "relapse":relapse, "catnum":catnum, "validcats":validcats})
    
def information(request):
    template ='InjectionLog/information.html'
    page="information"
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

def delete_injection(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL,request.path)
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
        q = InjectionLog.objects.filter(owner=request.user).filter(cat_name=cat).filter(id=request.GET["delete_id"]).get()

    except:
        return redirect("/?error=You do not have access to this resource")
    
    q.active=False
    q.save()
    return redirect("/log/?message=update&selectedcat=%s&q=%s" % (cat.id,q.id))

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
                    price = request.POST["GSPrice"])
            else:
                user_gs = UserGS(
                    user = request.user, 
                    brand = request.POST["GSBrand"],
                    concentration = request.POST["GSConcentration"],
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
    drugs = GSBrand.objects.all().order_by('brand')
    userGS = UserGS.objects.all()
    try:
        sc = SelectedCat.objects.filter(user=request.user)[0]
        cat_name = sc.cat_name   
    except:
        try:
            cat_name = Cats.objects.filter(owner=request.user).order_by('id')[0]
        except:
            pass
            
    request.GET = request.GET.copy()
    try:
        request.GET["selectedcat"] = cat_name.id
    except:
        return redirect("/?error=Please add a cat to your account first")

    try:
        latest_data = InjectionLog.objects.filter(owner=request.user).filter(cat_name=cat_name).order_by('-injection_time')[0]
        conc = latest_data.gs_brand.concentration
        dose = round(conc*latest_data.injection_amount/latest_data.cat_weight*decimal.Decimal(2.204),0)
        request.GET = request.GET.copy()
        request.GET["selectedcat"] = cat_name.id

        request.GET["CatWeight"] = latest_data.cat_weight
        request.GET["brand_value"] = latest_data.gs_brand_id
        if latest_data.wt_units == "kg":
            request.GET["weight_units"]=True
            dose = round(conc*latest_data.injection_amount/latest_data.cat_weight*100,0)/100
            
        request.GET["GSDose"] = dose
    except:
        pass
        
    validcats = Cats.objects.filter(owner=request.user)
    if request.method == "POST":

        user   = request.user
        cat = Cats.objects.get(id=request.POST["selectedcat"])
        weight = request.POST["CatWeight"]
        print(request.POST["brand_value"])
        brand  = GSBrand.objects.get(brand=request.POST["brand_value"])
        i_date = request.POST["inj_date"]
        rating = request.POST["cat_rating"]
        amount = request.POST["calculateddose"]
        i_note = request.POST["injectionnotes"]
        o_note = request.POST["othernotes"]
        if "gabadose" in request.POST:
            gabadose = request.POST["gabadose"]
        else:
            gabadose=None
            
        unit = "lb"
        if "weight_units" in request.POST:
            unit="kg"
        
        
        q = InjectionLog.objects.filter(owner = user).filter(cat_name = cat).filter(active=True).annotate(inj_value=Cast('injection_time', DateField()),)
        for row in q:
            if i_date[:10] in row.inj_value.strftime("%Y-%m-%d"):
                request.GET = request.POST
                return render(request, template, {"page":page,"dose":True, "drugs":drugs,"userGS":userGS, "validcats":validcats,"error":"The injection date has already been recorded.  Add information for a different day."})
                
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
                other_notes = o_note,
                wt_units = unit)
        log.save()
        
        if cat.treatment_start is None:
            cat.treatment_start = i_date[:10]
            cat.save()

        return redirect("/?message=success&weight=%s&unit=%s" % (weight,unit))
        

    return render(request, template, {"page":page, "dose":True,"drugs":drugs,"userGS":userGS, "validcats":validcats})

    
def injectionlog(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL,request.path)
    validcats = Cats.objects.filter(owner=request.user)
    try:
        cat = Cats.objects.filter(owner=request.user).filter(id=request.GET["selectedcat"])[0]
    except:
        try: 
            cat = Cats.objects.filter(owner=request.user).order_by('id')[0]
        except:
            return redirect("/?error=No data has been recorded...")
    
    template ='InjectionLog/injlog.html'
    page="log"
    
    injections = InjectionLog.objects.filter(
        owner=request.user).filter(
        cat_name=cat).filter(
        active=True).annotate(
        inj_date = ExpressionWrapper(Cast(F('injection_time'), DateField())-F('cat_name__treatment_start'),output_field=DurationField())).order_by('injection_time')
    return render(request, template, {"page":page,"injections":injections,"validcats":validcats, "cat":cat})
    

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