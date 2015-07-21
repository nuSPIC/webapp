from django.contrib import admin

from .models import SPIC, Network


class SPICAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group',
        'local_id',
        'title',
        )
    list_filter = ['group']
admin.site.register(SPIC, SPICAdmin)

class NetworkAdmin(admin.ModelAdmin):
    """
    A childclass of VersionAdmin, its neccessary to create versions.
    Check, if 'reversion' module is in INSTALLED_APP.
    """

    def mark_deleted(modeladmin, request, queryset):
        queryset.update(deleted=True)
    mark_deleted.short_description = "Mark selected networks as deleted"

    list_display = (
        'id',
        'user',
        'user_id',
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
    actions = ['mark_deleted']


try:
    admin.site.register(Network, NetworkAdmin)
except:
    admin.site.register(Network)
