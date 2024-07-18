from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpRequest
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import os,json,datetime,jaconv,re,unicodedata
from django.conf import settings

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# 定数検索ページ
def const_search(request:HttpRequest):

    context = {

        "title":f"クイック定数検索 {title_base}",
        "is_beta":True,
        "is_app":True,
        "song_data_len":"-",

    }

    # 更新日を取得
    context["const_update_time"] = get_update_time()

    # 著作権表示を取得
    context["rights"] = get_rights_data()

    # 検索情報が送られてきたら……
    if request.method=="POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        query = post.get("query")
        search_settings = {
            "is_use_name":( post.get("is_use_name")=="true" ),
            "is_use_reading":( post.get("is_use_reading")=="true" ),
            "is_use_artists":( post.get("is_use_artists")=="true" ),
        }
        type_game = post.get("type")
        request_time = post.get("request_time")

        # responseの初期化
        response = { "query":query, "request_time":request_time, "update_log":" " }
        query_list = []
        search_hit_count = 0
        search_results_html = ""

        # メタ情報を取得・出力
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        print(f"[{ip}][{type_game}] q:{query}")

        # 機種選択
        if type_game=="c":
            SDM = SongDataCNManager
        elif type_game=="o":
            SDM = SongDataOManager
        else:
            print(type_game)
            raise ValueError

        # 検索結果の処理
        # updateのとき
        if query=="/update":
            from my_apps.schedule_run import periodic_execution
            update_log = periodic_execution()
            response["update_log"] = update_log

        # 初期状態
        elif query=="":

            # 新曲を表示
            date_before_2_weekly = (datetime.date.today()-datetime.timedelta(days=14)).strftime("%Y-%m-%d")
            search_results_song_list = SDM.get_new_songs(date_before_2_weekly)

            search_hit_count = f"[新曲] {len(search_results_song_list)}"
            search_results_html = [ render_to_string(f"const_search/song_info_{type_game}.html",context={"song":song}) for song in search_results_song_list[:30] ]
            search_results_html.append(render_to_string("const_search/result_info.html",context={"info_text":"新曲を表示しています。検索ワードを入力してね！"}))

        # 検索ワードの処理
        else:

            # query_listの生成
            query_list = create_query_list(query)

            # 検索
            search_results_song_list = SDM.search_song_by_query_list(query_list,search_settings)
            search_hit_count = len(search_results_song_list)

            # 整える
            search_results_html = render_search_result(search_results_song_list,type_game)

        # Jsonとして返す
        response |= {
            "search_response":search_results_html[::-1],
            "search_hit_count":search_hit_count,
            "search_query_list":sorted(query_list).__str__(),
            "type":type_game,
        }

        return JsonResponse(response)

    # renderする
    return render(request, 'const_search/const_search.html',context=context)

# 更新日を取得
def get_update_time():
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_time.txt"),"r") as f:
        update_time = f.readline()
    return update_time

# 著作権データの取得
def get_rights_data():
    rights_list = []
    rights_list += ["【CHUNITHM】"]
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"),"r") as f:
        rights_list += f.readlines()
    rights_list += ["","【オンゲキ】"]
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"),"r") as f:
        rights_list += f.readlines()

    return rights_list

# query_listの生成
def create_query_list(query):

    query_list = [query]

    # 末尾にアルファベットがあれば消す
    if re.match(r".*^[\u3040-\u309F]+[a-zA-Z]{1}$",query) :
        query_list += [query[:-1]]
    if re.match(r".*^[\u3040-\u309F]+[a-zA-Z]{2}$",query) :
        query_list += [query[:-2]]

    # ひらがな・カタカナ変換
    for q in query_list[:]:
        query_list += [jaconv.kata2hira(q),jaconv.hira2kata(q)]

    # 重複削除
    query_list = list(set(query_list))

    return query_list

# 結果のレンダリング
def render_search_result(search_results_song_list,type_game):

    search_hit_count = len(search_results_song_list)
    search_results_html = [ render_to_string(f"const_search/song_info_{type_game}.html",context={"song":song}) for song in search_results_song_list[:30] ]

    # 多すぎたらこうすうる
    if search_hit_count  > 30:
        search_results_html.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が多すぎだよ〜 もう少しワードを絞ってみてね"}))
    # 少なすぎたらこうする
    if search_hit_count  == 0:
        search_results_html.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が0件だよ〜 ワードや設定を確認してみてね"}))

    return search_results_html
