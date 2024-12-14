from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q

# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import requests, urllib, requests
from bs4 import BeautifulSoup
from django.conf import settings

# from .view_chunithm_rating import get_chunithm_score_log_player_data

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(verbose=True)
dotenv_path = os.path.join(BASE_DIR.parent, ".env")
load_dotenv(dotenv_path)

title_base = "| △Natua♪▽のツールとか保管所"
API_TOKEN = os.environ.get("CHUNIREC_API_TOKEN")

# --------------------------------------------------


# テンプレート こいつをコピペして作ろう
def chunithm_rating_all(request):

    context = {"title": f"CHUNITHMベスト枠計算(全曲対象) {title_base}", "is_beta": False, "is_app": True}

    # Ajax処理
    if request.method == "POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        rec_id = post.get("rec_id")

        # chunirecにrequest送る
        player_data = get_chunirec_player_info(rec_id)
        records_data_list = get_chunirec_player_all_records(rec_id)["records"]
        # player_data,records_data_list = get_chunithm_score_log_player_data(rec_id)
        response = {"player_data": player_data, "records": records_data_list}

        # ベスト枠を算出
        rating_all_best_songs_raw = sorted(response["records"], key=lambda x: x["rating"], reverse=True)[:50]
        music_rate_list = []
        music_rate_old_list = []
        rating_all_best_songs_str = []
        for i, d in enumerate(rating_all_best_songs_raw):
            a_song_dict = {
                "n": f"{i+1:3n}",
                "const": f'{d["const"]:2.1f}',
                "const_old": f'{new2old_const(d["const"]):2.1f}',
                "music_rate": f'{calculate_rating(d["score"],d["const"]):2.2f}',
                "music_rate_old": f'{calculate_rating(d["score"],new2old_const(d["const"])):2.2f}',
                "score": f'{d["score"]:7n}',
                "diff": f'{d["diff"]}',
                "title": f'{d["title"]}',
            }
            music_rate_list.append(float(a_song_dict["music_rate"]))
            music_rate_old_list.append(float(a_song_dict["music_rate_old"]))
            rating_all_best_songs_str.append(a_song_dict)

        result_best_30 = f"{sum(music_rate_list[:30]) / 30:2.4f}"
        result_best_50 = f"{sum(music_rate_list) / 50:2.4f}"
        result_best_old_30 = f"{sum(music_rate_old_list[:30]) / 30:2.4f}"
        result_best_old_50 = f"{sum(music_rate_old_list) / 50:2.4f}"

        # プレイヤー情報を描画
        c = {
            "name": player_data["player_name"],
            "rating": player_data["rating"],
            "result_best_30": result_best_30,
            "result_best_50": result_best_50,
            "result_best_old_30": result_best_old_30,
            "result_best_old_50": result_best_old_50,
        }
        c["tweet_text"] = f'{c["name"]}さんのCHUNITHM全曲対象ベスト枠\n\nベスト枠平均(30枠/50枠)\n{c["result_best_30"]} / {c["result_best_50"]}\nベスト枠平均(旧基準)(30枠/50枠)\n{c["result_best_old_30"]} / {c["result_best_old_50"]}\n\n'
        cr_player_info_table_html = render_to_string("chunithm_rating_all/cr_player_info_table.html", context=c)

        # ベスト枠を描画
        c = {"rating_all_best_songs_str": rating_all_best_songs_str}
        cr_rating_table_html = render_to_string("chunithm_rating_all/cr_rating_table.html", context=c)

        # お返しする
        ajax_response = {"summary": cr_player_info_table_html, "result": cr_rating_table_html}
        return JsonResponse(ajax_response)

    return render(request, "chunithm_rating_all/chunithm_rating_all.html", context=context)


# ユーザー情報の取得
def get_chunirec_player_info(user_name):
    endpoint_url = "https://api.chunirec.net/2.0/records/profile.json"
    q = {"token": API_TOKEN, "region": "jp2", "user_name": user_name}
    q = urllib.parse.urlencode(q)
    r = requests.get(f"{endpoint_url}?{q}")
    if r.ok:
        player_data = r.json()
        # pprint.pprint(player_data)
        return player_data


# 全曲スコアの取得
def get_chunirec_player_all_records(user_name):
    endpoint_url = "https://api.chunirec.net/2.0/records/showall.json"
    q = {"token": API_TOKEN, "region": "jp2", "user_name": user_name}
    q = urllib.parse.urlencode(q)
    r = requests.get(f"{endpoint_url}?{q}")

    if int(r.headers["X-Rate-Limit-Remaining"]) < 10:
        print(f"残り{r.headers['X-Rate-Limit-Remaining']}回")

    if r.ok:
        score_data = r.json()
        return score_data
    else:
        return None


# レート値計算
def calculate_rating(score, const):
    if score >= 1009000:
        rating = const + 2.15
    elif score >= 1007500:
        rating = const + 2.0 + (score - 1007500) * 0.01 / 100
    elif score >= 1005000:
        rating = const + 1.5 + (score - 1005000) * 0.01 / 50
    elif score >= 1000000:
        rating = const + 1.0 + (score - 1000000) * 0.01 / 100
    elif score >= 990000:
        rating = const + 0.6 + (score - 990000) * 0.01 / 250
    elif score >= 975000:
        rating = const + (score - 975000) * 0.01 / 250
    else:
        rating = None

    return rating

# 定数変換
def new2old_const(new_const: float) -> float:
    if new_const <= 14.6:
        return new_const
    if 14.7 <= new_const <= 14.9:
        return new_const - 0.1
    if 15.0 <= new_const:
        return new_const - 0.2
    return None
