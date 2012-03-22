# -*- coding: utf-8 -*-
from django.contrib import admin
from reversion.admin import VersionAdmin

from network.models import SPIC, Network


class SPICAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group',
        'local_id',
        'title',
        )
    list_filter = ['group']
admin.site.register(SPIC, SPICAdmin)

def make_deleted(modeladmin, request, queryset):
    queryset.update(deleted=True)
make_deleted.short_description = "Mark selected networks as deleted"


class NetworkAdmin(admin.ModelAdmin):
    """
    A childclass of VersionAdmin, its neccessary to create versions.
    Check, if 'reversion' module is in INSTALLED_APP.    
    """
    
    def make_deleted(modeladmin, request, queryset):
        queryset.update(deleted=True)
    make_deleted.short_description = "Mark selected networks as deleted"
    
    list_display = (
        'id',
        'user',
        'SPIC',
        'local_id',
        'label',
        'date_simulated',
        'has_spike_detector',
        'has_voltmeter',
        'favorite',
        'deleted',
        )
    list_filter = ['SPIC','has_spike_detector','has_voltmeter','favorite','deleted','user_id','local_id']
    date_hierarchy = 'date_simulated'
    actions = ['make_deleted']


try:
    admin.site.register(Network, NetworkAdmin)
except:
    admin.site.register(Network)
    
