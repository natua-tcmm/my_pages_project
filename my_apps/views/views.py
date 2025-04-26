from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q, Count
from django.utils import timezone
from django.db.models.functions import ExtractHour, ExtractWeekDay

from user_agents import parse as ua_parse

# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import os, json, datetime, jaconv, re, unicodedata
from datetime import timedelta
from django.conf import settings

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------


# トップ画面
def top(request):
    context = {"title": "△Natua♪▽のツールとか保管所", "is_beta": False, "is_app": False}
    return render(request, "top.html", context=context)


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

    now = timezone.now()

    # --- bot 判定パターン ---
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
        # …他必要に応じて
    ]
    bot_q = Q()
    for kw in BOT_KEYWORDS:
        bot_q |= Q(user_agent__icontains=kw)

    # --- 共通 filters ---
    nonbot_base = Q(path__startswith="/my_apps/") & ~bot_q
    json_base = Q(path__startswith="/my_apps/") & Q(path__iendswith=".json")

    # --- 1) bot 除く：各ページごとのアクセス数 ---
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

    # --- 2) bot 除く：/my_apps/ 配下全体の集計 ---
    all_myapps = PageView.objects.filter(nonbot_base)
    agg_all = {
        "total": all_myapps.count(),
        "last24h": all_myapps.filter(timestamp__gte=now - timedelta(hours=24)).count(),
        "last7d": all_myapps.filter(timestamp__gte=now - timedelta(days=7)).count(),
    }

    # 時間帯統計（0–23時）
    hour_stats = all_myapps.annotate(hour=ExtractHour("timestamp")).values("hour").annotate(cnt=Count("id")).order_by("hour")

    # 曜日統計（1=日曜…7=土曜）
    weekday_stats = (
        all_myapps.annotate(weekday=ExtractWeekDay("timestamp")).values("weekday").annotate(cnt=Count("id")).order_by("weekday")
    )

    # OSランキング
    os_counts = {}
    for pv in all_myapps.exclude(user_agent__isnull=True).only("user_agent"):
        ua = ua_parse(pv.user_agent)
        osn = ua.os.family or "Unknown"
        os_counts[osn] = os_counts.get(osn, 0) + 1

    top_os = sorted(os_counts.items(), key=lambda x: -x[1])

    # --- 3) bot 含む：JSON へのアクセス ---
    json_qs = PageView.objects.filter(json_base)
    agg_json = {
        "total": json_qs.count(),
        "last24h": json_qs.filter(timestamp__gte=now - timedelta(hours=24)).count(),
        "last7d": json_qs.filter(timestamp__gte=now - timedelta(days=7)).count(),
    }

    # --- コンソール出力 ---
    print("=== /my_apps/ 各ページ（bot 除く） ===")
    print("-- Total --")
    for row in per_page:
        # print(f"{row['path']}: total={row['total']}, 24h={row['last24h']}, 7d={row['last7d']}")
        print(f"{row['path'][9:]:40}: {row['total']:5} | {row['total']//20 * '#'}")

    print("\n-- 24h --")
    for row in per_page:
        print(f"{row['path'][9:]:40}: {row['last24h']:5} | {row['last24h']//1 * '#'}")

    print("\n-- 7d --")
    for row in per_page:
        print(f"{row['path'][9:]:40}: {row['last7d']:5} | {row['last7d']//5 * '#'}")

    print("\n=== /my_apps/ 配下全体（bot 除く） ===")
    print(f"Total={agg_all['total']} 24h={agg_all['last24h']} 7d={agg_all['last7d']}")

    print("\n-- 時間帯統計 --")
    for h in hour_stats:
        print(f"{h['hour']:3}h: {h['cnt']:5} | {h['cnt']//10 * '#'}")

    print("\n-- 曜日統計 (1=Sun…) --")
    for d in weekday_stats:
        print(f"{d['weekday']}: {d['cnt']:5} | {d['cnt']//10 * '#'}")

    print("\n-- OS 名ランキング --")
    for osn, cnt in top_os:
        print(f"{osn}: {cnt}")

    print("\n=== /my_apps/*.json（bot 含む） ===")
    print(f"Total={agg_json['total']} 24h={agg_json['last24h']} 7d={agg_json['last7d']}")

    stats = (
        ToolUsage.objects
        .values('tool_name')
        .annotate(
            total=Count('id'),
            last24h=Count('id', filter=Q(timestamp__gte=now - timedelta(hours=24))),
            last7d=Count('id', filter=Q(timestamp__gte=now - timedelta(days=7))),
        )
        .order_by('-total')
    )

    print("=== ToolUsage Stats ===")
    for row in stats:
        name = row['tool_name'] or '<Unknown>'
        print(f"{name}: total={row['total']}, 24h={row['last24h']}, 7d={row['last7d']}")


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
