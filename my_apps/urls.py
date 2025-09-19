from django.urls import path
from django.shortcuts import redirect

app_name = "my_apps"

from .views import views
from .views import view_ongeki_op
from .views import view_ongeki_rating
from .views import view_const_search
from .views import view_chunithm_rating
from .views import view_yumesute_ocr

urlpatterns = [
    path("yumesute_ocr_ajax_upload", view_yumesute_ocr.yumesute_ocr_ajax_upload, name="yumesute_ocr_ajax_upload"),
    path("yumesute_ocr_csv_download", view_yumesute_ocr.yumesute_ocr_csv_download, name="yumesute_ocr_csv_download"),
    # システム
    path("p403", views.preview403, name="p403_page"),
    path("p404", views.preview404, name="p404_page"),
    path("p500", views.preview500, name="p500_page"),
    path("incomplete_page", views.incomplete_page, name="incomplete_page"),

    # トップ
    path("", lambda request: redirect(f"/{app_name}/top")),
    path("top", views.top, name="top_page"),
    path("about", views.about, name="about_page"),
    path("update_info", views.update_info, name="update_info_page"),

    # ツール
    path("const_search", view_const_search.ConstSearchView.as_view(), name="const_search_page"),
    path("fullbell", views.fullbell, name="fullbell_page"),
    path("bpm_checker", views.bpm_checker, name="bpm_checker_page"),
    path("ongeki_op", view_ongeki_op.ongeki_op, name="ongeki_op_page"),
    path("ongeki_rating_all", view_ongeki_rating.ongeki_rating_all, name="ongeki_rating_all_page"),
    path("chunithm_rating_all", view_chunithm_rating.chunithm_rating_all, name="chunithm_rating_all_page"),
    path("yumesute_ocr", view_yumesute_ocr.yumesute_ocr, name="yumesute_ocr_page"),

    # 資料集
    path("ongeki_genre", views.ongeki_genre, name="ongeki_genre_page"),
    path("sega_nenpyo", views.sega_nenpyo, name="sega_nenpyo_page"),

    # その他
    path("random_tools", views.random_tools, name="random_tools_page"),
    path("app_template", views.app_template, name="app_template_page"),

    # データベース
    path("songdata_chunithm.json", views.songdata_chunithm, name="songdata_chunithm_json"),
    path("songdata_ongeki.json", views.songdata_ongeki, name="songdata_ongeki_json"),
]
