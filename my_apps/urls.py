from django.urls import path

app_name = "my_apps"

from . import views

urlpatterns = [
    path("top", views.top, name="top_page"),
    path("p404", views.preview404, name="p404_page"),
    path("incomplete_page", views.incomplete_page, name="incomplete_page"),
    path("const_search", views.const_search, name="const_search_page"),
    path("app_template", views.app_template, name="app_template_page"),
]
