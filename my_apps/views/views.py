from django.shortcuts import redirect, render


TOP_TARGET_URL = "https://www.st1027.org"
MIGRATION_TARGETS = {
    "chunithm_rating_all": "https://www.st1027.org/tools/chunithm_rating_all",
    "const_search": "https://www.st1027.org/tools/const_search",
    "ongeki_rating_all": "https://www.st1027.org/tools/ongeki_rating_all",
    "ongeki_op": "https://www.st1027.org/tools/ongeki_op",
    "songdata_chunithm_json": "https://ntools.st1027.org/json/songdata_chunithm.json",
    "songdata_ongeki_json": "https://ntools.st1027.org/json/songdata_ongeki.json",
}


def render_migration_page(request, page_name: str, target_url: str, *, is_top_page: bool = False):
    context = {
        "title": f"{page_name} | サイト移行のお知らせ",
        "page_name": page_name,
        "target_url": target_url,
        "is_top_page": is_top_page,
        "message": "このページは新サイトへ移行しました。以下のリンクから移動してください。",
    }
    return render(request, "simple_redirect.html", context=context)


def top(request):
    return render_migration_page(request, "トップページ", TOP_TARGET_URL, is_top_page=True)


def chunithm_rating_all(request):
    return render_migration_page(request, "CHUNITHMベスト枠計算(全曲対象)", MIGRATION_TARGETS["chunithm_rating_all"])


def const_search(request):
    return render_migration_page(request, "クイック定数検索+", MIGRATION_TARGETS["const_search"])


def ongeki_rating_all(request):
    return render_migration_page(request, "オンゲキベスト枠計算(全曲対象)", MIGRATION_TARGETS["ongeki_rating_all"])


def ongeki_op(request):
    return render_migration_page(request, "オンゲキ版OVERPOWER", MIGRATION_TARGETS["ongeki_op"])


def songdata_chunithm(request):
    return redirect(MIGRATION_TARGETS["songdata_chunithm_json"], permanent=True)


def songdata_ongeki(request):
    return redirect(MIGRATION_TARGETS["songdata_ongeki_json"], permanent=True)


def redirect_to_top(request, *_args, **_kwargs):
    return redirect("my_apps:top_page")
