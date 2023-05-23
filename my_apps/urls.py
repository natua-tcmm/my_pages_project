from django.urls import path

app_name = "my_apps"

from . import views

urlpatterns = [
    path("top", views.top, name="toppage"),
    path("const_search", views.const_search, name="const_search_page"),
    # path("app2", views.app2, name="app2page"),
    path("p404", views.preview404, name="p404page"),
]
