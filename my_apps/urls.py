from django.urls import path

app_name = "my_apps"

from . import views

urlpatterns = [
    path("p403", views.preview403, name="p403_page"),
    path("p404", views.preview404, name="p404_page"),
    path("p500", views.preview500, name="p500_page"),
    path("incomplete_page", views.incomplete_page, name="incomplete_page"),

    path("top", views.top, name="top_page"),
    path("about", views.about, name="about_page"),

    path("const_search", views.const_search, name="const_search_page"),

    path("ongeki_genre", views.ongeki_genre, name="ongeki_genre_page"),

    path("app_template", views.app_template, name="app_template_page"),
]
