from django.contrib import admin
from InjectionLog.models import Cats, GSBrand, ObservationLog, InjectionLog, RelapseDate,UserExtension

# Register your models here.
admin.site.register(Cats)
admin.site.register(GSBrand)
admin.site.register(ObservationLog)
admin.site.register(InjectionLog)
admin.site.register(RelapseDate)
admin.site.register(UserExtension)
