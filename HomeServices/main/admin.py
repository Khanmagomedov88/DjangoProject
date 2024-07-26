from django.contrib import admin
from .models import Apartment, Tariff, WaterMeter, House, Payment, WaterMeterReading

class WaterMeterReadingInline(admin.TabularInline):
    model = WaterMeterReading
    extra = 1

class WaterMeterAdmin(admin.ModelAdmin):
    inlines = [WaterMeterReadingInline]

admin.site.register(Apartment)
admin.site.register(Tariff)
admin.site.register(WaterMeter, WaterMeterAdmin)
admin.site.register(House)
admin.site.register(Payment)