from django.shortcuts import redirect
from django.urls import path, re_path

from .views import views

app_name = "my_apps"


urlpatterns = [
    path("", lambda request: redirect(f"/{app_name}/top")),
    path("top", views.top, name="top_page"),
    path("chunithm_rating_all", views.chunithm_rating_all, name="chunithm_rating_all_page"),
    path("const_search", views.const_search, name="const_search_page"),
    path("ongeki_rating_all", views.ongeki_rating_all, name="ongeki_rating_all_page"),
    path("ongeki_op", views.ongeki_op, name="ongeki_op_page"),
    path("songdata_chunithm.json", views.songdata_chunithm, name="songdata_chunithm_json"),
    path("songdata_ongeki.json", views.songdata_ongeki, name="songdata_ongeki_json"),
    re_path(r"^(?!top$|chunithm_rating_all$|const_search$|ongeki_rating_all$|ongeki_op$|songdata_chunithm\.json$|songdata_ongeki\.json$).+$", views.redirect_to_top),
]
