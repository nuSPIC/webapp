from django.contrib import admin
from models import Result

class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'revision', 'revision_date_created', 'has_spike_detector', 'has_voltmeter')
admin.site.register(Result, ResultAdmin)
