from django.contrib import admin
from .models import SongDataC,SongDataO,GameDataB2023
from import_export import resources
from import_export.admin import ImportMixin

admin.site.register(SongDataC)
admin.site.register(SongDataO)
# admin.site.register(GameDataB2023)

class GameDataB2023Resource(resources.ModelResource):
    class Meta:
        model = GameDataB2023

@admin.register(GameDataB2023)
class GameDataB2023Admin(ImportMixin, admin.ModelAdmin):
    resource_class = GameDataB2023Resource
