from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import requests,urllib,requests
from bs4 import BeautifulSoup
from django.conf import settings

# from .view_chunithm_rating import get_chunithm_score_log_player_data

from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(verbose=True)
dotenv_path = os.path.join(BASE_DIR.parent, '.env')
load_dotenv(dotenv_path)

title_base = "| △Natua♪▽のツールとか保管所"
API_TOKEN = os.environ.get("CHUNIREC_API_TOKEN")

# --------------------------------------------------

# テンプレート こいつをコピペして作ろう
def chunithm_rating_all(request):

    context = { "title":f"CHUNITHMベスト枠計算(全曲対象) {title_base}" ,"is_beta":False, "is_app":True }

    # Ajax処理
    if request.method=="POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        rec_id = post.get("rec_id")


        # chunirecにrequest送る
        player_data = get_chunirec_player_info(rec_id)
        records_data_list = get_chunirec_player_all_records(rec_id)["records"]
        # player_data,records_data_list = get_chunithm_score_log_player_data(rec_id)
        response = {"player_data":player_data,"records":records_data_list}


        # ベスト枠を算出
        rating_all_best_songs_raw = sorted(response["records"], key=lambda x:x["rating"], reverse=True )[:30]
        music_rate_list = []
        music_rate_max = 0
        rating_all_best_songs_str = []
        for i,d in enumerate(rating_all_best_songs_raw):
            music_rate_list.append(d["rating"])
            a_song_dict = {
                "n":f"{i+1:3n}",
                "const":f'{d["const"]:2.1f}',
                "music_rate":f'{d["rating"]:2.2f}',
                "score":f'{d["score"]:7n}',
                "diff":f'{d["diff"]}',
                "title":f'{d["title"]}',
            }
            rating_all_best_songs_str.append(a_song_dict)
            if True:
                music_rate_max = max(music_rate_max,d["rating"])

        result_best = int(sum(music_rate_list)*100/30)/100
        result_reachable = int(( sum(music_rate_list)*3/120 + music_rate_max/4 )*100)/100
        result_range = int((music_rate_list[0]-music_rate_list[-1])*100)/100


        # プレイヤー情報を描画
        c = {
            "name":player_data["player_name"],
            "rating":player_data["rating"],
            "result_best":result_best,
            "result_reachable":result_reachable,
            "result_range":result_range,
        }
        cr_player_info_table_html = render_to_string("chunithm_rating_all/cr_player_info_table.html",context=c)

        # ベスト枠を描画
        c = {
            "rating_all_best_songs_str":rating_all_best_songs_str
        }
        cr_rating_table_html = render_to_string("chunithm_rating_all/cr_rating_table.html",context=c)


        # お返しする
        ajax_response = { "summary":cr_player_info_table_html ,"result":cr_rating_table_html }
        return JsonResponse(ajax_response)

    return render(request, 'chunithm_rating_all/chunithm_rating_all.html',context=context)

# def chunithm_rating_act2(request):
#     context = { "title":f"オンゲキ brightMEMORY Act.2基準レーティング {title_base}" ,"is_beta":False, "is_app":True }
#     return render(request, 'chunithm_rating_act2/chunithm_rating_act2.html',context=context)

# ユーザー情報の取得
def get_chunirec_player_info(user_name):
    endpoint_url = "https://api.chunirec.net/2.0/records/profile.json"
    q = { "token" : API_TOKEN, "region":"jp2", "user_name" : user_name }
    q = urllib.parse.urlencode(q)
    r = requests.get(f"{endpoint_url}?{q}")
    if r.ok:
        player_data = r.json()
        # pprint.pprint(player_data)
        return player_data

# 全曲スコアの取得
def get_chunirec_player_all_records(user_name):
    endpoint_url = "https://api.chunirec.net/2.0/records/showall.json"
    q = { "token" : API_TOKEN, "region":"jp2", "user_name" : user_name }
    q = urllib.parse.urlencode(q)
    r = requests.get(f"{endpoint_url}?{q}")

    if int(r.headers["X-Rate-Limit-Remaining"]) < 10:
        print(f"残り{r.headers['X-Rate-Limit-Remaining']}回")

    if r.ok:
        score_data = r.json()
        return score_data
    else:
        return None
