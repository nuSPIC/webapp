# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Result

class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_id',
        'SPIC_id',
        'has_spike_detector', 
        'has_voltmeter'
    )
    list_filter = ['has_spike_detector', 'has_voltmeter']
admin.site.register(Result, ResultAdmin)
