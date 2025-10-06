from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q, Count
from django.utils import timezone
from user_agents import parse as ua_parse
from django.views.decorators.http import require_GET
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------


# トップ画面
def top(request):
    context = {"title": "△Natua♪▽のツールとか保管所", "is_beta": False, "is_app": False}
    return render(request, "top.html", context=context)

# ---- 統計API共通処理 ----
def get_nonbot_base_query():
    BOT_KEYWORDS = [
        "bot",
        "crawl",
        "spider",
        "slurp",
        "python-requests",
        "curl",
        "wget",
        "facebookexternalhit",
        "ahrefs",
        "semrush",
        "yandex",
        "duckduck",
        "dotbot",
    ]
    bot_q = Q()
    for kw in BOT_KEYWORDS:
        bot_q |= Q(user_agent__icontains=kw)
    # IPアドレス127.0.0.1も除外
    bot_q |= Q(ip="127.0.0.1")
    return Q(path__startswith="/my_apps/") & ~bot_q


def get_total_stats(nonbot_base):
    total_access = PageView.objects.filter(nonbot_base).count()
    total_access_str = str(total_access).translate(str.maketrans("1234567890", "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎"))
    return {"total_access": total_access_str}


def get_pages_stats(nonbot_base):
    now = timezone.now()
    per_page = (
        PageView.objects.filter(nonbot_base)
        .values("path")
        .annotate(
            total=Count("id"),
            last24h=Count("id", filter=Q(timestamp__gte=now - timedelta(hours=24))),
            last7d=Count("id", filter=Q(timestamp__gte=now - timedelta(days=7))),
        )
        .order_by("-total")
    )
    labels = []
    data = []
    other_total = 0
    for i, row in enumerate(per_page):
        if i >= 5:
            other_total += row["total"]
            continue
        labels.append(row["path"][9:])
        data.append(row["total"])
    if other_total > 0:
        labels.append("others")
        data.append(other_total)
    return {"labels": labels, "data": data}


def get_os_stats(nonbot_base):
    all_myapps = PageView.objects.filter(nonbot_base)
    os_counts = {}
    for pv in all_myapps.exclude(user_agent__isnull=True).only("user_agent"):
        ua = ua_parse(pv.user_agent)
        osn = ua.os.family or "Unknown"
        os_counts[osn] = os_counts.get(osn, 0) + 1
    top_os = sorted(os_counts.items(), key=lambda x: -x[1])
    labels = []
    data = []
    other_total = 0
    for i, row in enumerate(top_os):
        if i >= 4:
            other_total += row[1]
            continue
        labels.append(row[0])
        data.append(row[1])
    if other_total > 0:
        labels.append("others")
        data.append(other_total)
    return {"labels": labels, "data": data}


def get_daily_stats(nonbot_base):
    now = timezone.now()
    from django.db.models.functions import TruncDate

    daily_stats = (
        PageView.objects.filter(nonbot_base, timestamp__gte=now - timedelta(days=10))
        .annotate(date=TruncDate("timestamp"))
        .values("date")
        .annotate(cnt=Count("id"))
        .order_by("date")
    )
    labels = []
    data = []
    for row in daily_stats:
        labels.append(row["date"].strftime("%Y-%m-%d"))
        data.append(row["cnt"])
    return {"labels": labels, "data": data}


def get_tools_stats():
    now = timezone.now()
    from django.db.models.functions import TruncDate

    tool_usage_daily = (
        ToolUsage.objects.filter(timestamp__gte=now - timedelta(days=10))
        .exclude(ip="127.0.0.1")
        .annotate(date=TruncDate("timestamp"))
        .values("date", "tool_name")
        .annotate(count=Count("id"))
        .order_by("date", "tool_name")
    )
    tool_data = {}
    for row in tool_usage_daily:
        date = row["date"].strftime("%Y-%m-%d")
        tool_name = row["tool_name"]
        count = row["count"]
        if date not in tool_data:
            tool_data[date] = {}
        tool_data[date][tool_name] = count
    labels = sorted(tool_data.keys())
    tools = set()
    for daily_data in tool_data.values():
        tools.update(daily_data.keys())
    tools = sorted(tools)
    datasets = []
    for tool in tools:
        data = [tool_data[date].get(tool, 0) for date in labels]
        datasets.append({"label": tool, "data": data})
    return {"labels": labels, "datasets": datasets}


@require_GET
def api_stats(request):
    stat_type = request.GET.get("type", "total")
    nonbot_base = get_nonbot_base_query()
    if stat_type == "total":
        return JsonResponse(get_total_stats(nonbot_base))
    elif stat_type == "pages":
        return JsonResponse(get_pages_stats(nonbot_base))
    elif stat_type == "os":
        return JsonResponse(get_os_stats(nonbot_base))
    elif stat_type == "daily":
        return JsonResponse(get_daily_stats(nonbot_base))
    elif stat_type == "tools":
        return JsonResponse(get_tools_stats())
    else:
        return JsonResponse({"error": "Invalid type"}, status=400)


import os, json, unicodedata
from datetime import timedelta
from django.conf import settings


# 403ページを見るためのview
def preview403(request):
    return render(request, "403.html")


# 404ページを見るためのview
def preview404(request):
    return render(request, "404.html")


# 500ページを見るためのview
def preview500(request):
    return render(request, "500.html")


# 未完成ページ
def incomplete_page(request):
    context = {"title": "未完成のページ", "is_beta": False, "is_app": True}
    return render(request, "incomplete_page.html", context=context)


# --------------------------------------------------


# テンプレート こいつをコピペして作ろう
def app_template(request):
    context = {"title": f"タイトル {title_base}", "is_beta": True, "is_app": True}
    return render(request, "app_template/app_template.html", context=context)


# --------------------------------------------------


# 自己紹介ページ
def about(request):

    context = {"title": f"△Natua♪▽について {title_base}", "is_beta": False, "is_app": False}
    return render(request, "about/about.html", context=context)


# 更新情報ページ
def update_info(request):
    context = {"title": f"更新情報 {title_base}", "is_beta": False, "is_app": False}
    return render(request, "update_info/update_info.html", context=context)


# --------------------------------------------------


# FULLBELLだったら
def fullbell(request):
    context = {"title": f"FULL BELLだったら？  {title_base}", "is_beta": False, "is_app": True}
    return render(request, "fullbell/fullbell.html", context=context)


# BPMチェッカー
def bpm_checker(request):
    context = {"title": f"BPMチェッカー  {title_base}", "is_beta": False, "is_app": True}
    return render(request, "bpm_checker/bpm_checker.html", context=context)


# --------------------------------------------------


# SEGA音ゲー年表
def sega_nenpyo(request):

    context = {"title": f"SEGA音ゲー年表 {title_base}", "is_beta": False, "is_app": True}

    return render(request, "sega_nenpyo/sega_nenpyo.html", context=context)


# オンゲキジャンル
def ongeki_genre(request):

    context = {"title": f"オンゲキジャンル名図鑑 {title_base}", "is_beta": False, "is_app": True}

    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"), "r") as f:
        ongeki_genre_json = json.load(f)

    genre_data = ongeki_genre_json["genre_data"]
    updated_date = ongeki_genre_json["updated_date"]

    genre_data = sorted(genre_data.items(), key=lambda e: e[0])
    # genre_data = sorted(genre_data.items(), key = lambda e : e[1])

    context["genre_data"] = genre_data
    context["updated_date"] = updated_date

    return render(request, "ongeki_genre/ongeki_genre.html", context=context)


# --------------------------------------------------


# 雑多なツール
def random_tools(request):

    context = {"title": f"雑多なツール集 {title_base}", "is_beta": False, "is_app": True}

    if request.method == "POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        type = post.get("type")
        query = post.get("query")

        result = ""

        # typeによって分岐
        if type == "unicode":
            table_start = '<table class="table mb-0" id="unicode-table"><thead class="thead-light"><tr><th scope="col">#</th><th scope="col">Char</th><th scope="col">CodePoint</th><th scope="col">Name & Link</th></tr></thead><tbody class="table-hover">'
            table_end = (
                f'</tbody></table><small class="text-muted float-right">Unicode Version: {unicodedata.unidata_version}</small>'
            )

            # 表を生成する
            if not len(query) == 0:
                result += table_start
                for n, char in enumerate(query):
                    char = unicodedata.normalize("NFC", char)
                    codepoint = str.upper(str(hex(ord(char)))[2:]).zfill(4)
                    unicode_name = unicodedata.name(char)
                    unicode_url = f"https://www.compart.com/en/unicode/U+{codepoint}"
                    # result += f"【 {char} 】 : U+{codepoint}\n{unicodedata.name(char)}\nhttps://www.compart.com/en/unicode/U+{codepoint}\n"
                    result += f'<tr><th scope="row">{n}</th><td>{char}</td><td>U+{codepoint}</td><td><a href="{unicode_url}" target="_blank" rel="noopener noreferrer">{unicode_name}</a></td></tr>'
                result += table_end

        # お返しする
        response = {"result": result}
        return JsonResponse(response)

    return render(request, "random_tools/random_tools.html", context=context)


# --------------------------------------------------


# データベース
def songdata_chunithm(request):
    file_path = os.path.join(settings.BASE_DIR, "my_apps/my_data/songdata_chunithm_for_public.json")
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), content_type="application/json")
    else:
        raise Http404("JSONファイルが見つかりません")


def songdata_ongeki(request):
    file_path = os.path.join(settings.BASE_DIR, "my_apps/my_data/songdata_ongeki_for_public.json")
    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), content_type="application/json")
    else:
        raise Http404("JSONファイルが見つかりません")
