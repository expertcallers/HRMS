from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# Register your models here.
class profileSearchResource(resources.ModelResource):
    class Meta:
        model = Campaign

class Search(ImportExportModelAdmin):
    search_fields = ("campaignid", "campaign", 'user')
    list_display = ('campaignid', "campaign", 'campaign_type', 'user', 'campaign_status')
    list_filter = ['campaign_type']
    resource_class = profileSearchResource

class MappingSearch(admin.ModelAdmin):
    search_fields = ("campaign", "user")
    list_display = ('user', "campaign")

class CampaignLinksSearch(admin.ModelAdmin):
    search_fields = ("campaign", "link")
    list_display = ("campaign", "link")

admin.site.register(Campaign, Search)
admin.site.register(Mapping, MappingSearch)
admin.site.register(CampaignLinks, CampaignLinksSearch)
