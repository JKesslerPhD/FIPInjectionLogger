from django.contrib import admin
from InjectionLog.models import Cats, GSBrand, ObservationLog, InjectionLog
from InjectionLog.models import RelapseDate,UserExtension, SelectedCat, BloodWork
from InjectionLog.models import WarriorTracker

# Register your models here.
admin.site.register(Cats)
admin.site.register(GSBrand)
admin.site.register(ObservationLog)
admin.site.register(InjectionLog)
admin.site.register(RelapseDate)
admin.site.register(UserExtension)
admin.site.register(SelectedCat)
admin.site.register(BloodWork)
admin.site.register(WarriorTracker)
