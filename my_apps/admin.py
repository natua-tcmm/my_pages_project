from django.contrib import admin
from .models import SongDataCN
from .models import SongDataC,SongDataO,GameDataB2023
from import_export import resources
from import_export.admin import ImportExportMixin

# admin.site.register(SongDataC)
# admin.site.register(SongDataO)
# admin.site.register(GameDataB2023)

# class GameDataB2023Resource(resources.ModelResource):
#     class Meta:
#         model = GameDataB2023

# @admin.register(GameDataB2023)
# class GameDataB2023Admin(ImportExportMixin, admin.ModelAdmin):
#     resource_class = GameDataB2023Resource

class SongDataCNResource(resources.ModelResource):
    class Meta:
        model = SongDataCN

@admin.register(SongDataCN)
class SongDataCAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SongDataCNResource

class SongDataCResource(resources.ModelResource):
    class Meta:
        model = SongDataC

@admin.register(SongDataC)
class SongDataCAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SongDataCResource

class SongDataOResource(resources.ModelResource):
    class Meta:
        model = SongDataO

@admin.register(SongDataO)
class SongDataOAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = SongDataOResource
