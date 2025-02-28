from django.contrib import admin
from .models import SongDataCN, SongDataON
from import_export import resources
from import_export.admin import ImportExportMixin

class SongDataCNResource(resources.ModelResource):
    class Meta:
        model = SongDataCN

@admin.register(SongDataCN)
class SongDataCAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SongDataCNResource

class SongDataONResource(resources.ModelResource):
    class Meta:
        model = SongDataON

@admin.register(SongDataON)
class SongDataOAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SongDataONResource
