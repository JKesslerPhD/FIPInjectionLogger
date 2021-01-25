from django.db import models
from django.contrib.auth.models import User
from datetime import date
from gdstorage.storage import GoogleDriveStorage


gd_storage = GoogleDriveStorage()

class WarriorAdmin(models.Model):
    warrior_admin = models.CharField(max_length=200)
    
    
class UserExtension(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, null=True)
    test_account = models.BooleanField(default=False)
    facebook = models.CharField(max_length = 200, null=True)


    
class Cats(models.Model):
    owner = models.ForeignKey(User, on_delete = models.PROTECT)
    name = models.CharField(max_length = 200)
    birthday = models.DateField()
    fip_type = models.CharField(max_length=32)
    ocular = models.BooleanField(default=False)
    neuro  = models.BooleanField(default=False)
    treatment_start = models.DateField(null=True)
    relapse = models.BooleanField(default=False)
    WarriorAdmin = models.CharField(max_length=200, null=True)
    notes = models.TextField(null=True)
    extended_treatment = models.IntegerField(default=0, null=False)
    test_cat = models.BooleanField(default=False)
    sharable = models.CharField(max_length=32, null=True)
    cured = models.BooleanField(default=False)
    bad = models.BooleanField(default=False)

class FixTimezone(models.Model):
    owner = models.ForeignKey(User, on_delete = models.PROTECT)
    fixed = models.BooleanField(default=False)
    timezone = models.CharField(max_length=64, default="UTC")
    


class GSBrand(models.Model):
    brand = models.CharField(primary_key=True, max_length = 100)
    concentration = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    admin_method = models.CharField(max_length=10, default="Injectable")

class UserGS(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    brand = models.CharField(max_length = 100, null=False)
    concentration = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    admin_method = models.CharField(max_length=10, default="Injectable")

class InjectionLog(models.Model):
    owner = models.ForeignKey(User, on_delete = models.PROTECT)
    gs_brand = models.CharField(max_length = 100, null=True)
    date_added = models.DateField(default = date.today, editable=False)
    cat_name = models.ForeignKey(Cats, on_delete = models.PROTECT)
    cat_weight = models.DecimalField(max_digits=4, decimal_places=2, null=False)
    wt_units   = models.CharField(max_length=2, default='lb')
    injection_time = models.DateTimeField(null=False)
    injection_amount = models.DecimalField(max_digits=3, decimal_places=1, null=False)
    cat_behavior_today = models.IntegerField(default=3, null=False)
    injection_notes = models.TextField(null=True)
    gaba_dose = models.IntegerField(null=True)
    other_notes = models.TextField(null=True)
    new_symptom = models.TextField(null=True)
    active = models.BooleanField(default=True)

class SelectedCat(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete = models.CASCADE)
    cat_name = models.ForeignKey(Cats, on_delete = models.PROTECT)
    
class ObservationLog(models.Model):
    owner = models.ForeignKey(User, on_delete = models.PROTECT)
    date_added = models.DateField(default = date.today, editable=False)
    cat_name = models.ForeignKey(Cats, on_delete = models.PROTECT)
    cat_weight = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    wt_units   = models.CharField(max_length=2, default='lb', null=True)
    observation_date = models.DateField(null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=1, null=True)
    temp_units  = models.CharField(max_length=1, default='F', null=True)
    cat_behavior_today = models.IntegerField(default=3, null=False)
    notes = models.TextField(null=True)
    active = models.BooleanField(default=True)
    
class RelapseDate(models.Model):
    cat_name = models.ForeignKey(Cats, on_delete = models.PROTECT)
    relapse_start = models.DateField(null=True)
    fip_type = models.CharField(max_length=32)
    active = models.BooleanField(default=True)
    ocular = models.BooleanField(default=False)
    neuro  = models.BooleanField(default=False)
    notes = models.TextField(null=True)

        
class BloodWork(models.Model):
    bloodname = models.CharField(max_length=200)
    cat_name = models.ForeignKey(Cats, on_delete = models.CASCADE, null=True)
    bloodwork_date = models.DateField(default = date.today)
    url_link = models.CharField(max_length=500, null=True, blank=True)
    bloodwork = models.FileField(upload_to = 'FIPlog/', storage=gd_storage, null=True) 
    notes = models.TextField(null=True, blank=True)   
    active = models.BooleanField(default=True)
    

class WarriorTracker(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    md5hash = models.CharField(max_length=32, null=True)
    identifier = models.CharField(max_length=200, null=True)
    
class BloodSummary(models.Model):
    cat_name = models.ForeignKey(Cats, on_delete = models.CASCADE, null=False)
    bt_date  = models.DateField(default = date.today)
    rbc = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    hct = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    hgb = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    wbc = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    pct_lym = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    pct_neu = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    lym = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    neu = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    tp = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    alb = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    glob = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    a_g = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    tbil = models.DecimalField(null=True, max_digits=4, decimal_places=2)
    