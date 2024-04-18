from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import os,json,datetime,jaconv,re,unicodedata
from django.conf import settings

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# 定数検索ページ
def const_search(request):


    context = {

        "title":f"クイック定数検索 {title_base}",
        "is_beta":True,
        "is_app":True,
        "song_data_len":"-",

    }

    # 更新日を取得
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_time.txt"),"r") as f:
        context["const_update_time"] = f.readline()

    # 著作権表示を取得
    context["rights"] = []
    context["rights"] += ["【CHUNITHM】"]
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"),"r") as f:
        context["rights"] += f.readlines()
    context["rights"] += ["","【オンゲキ】"]
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"),"r") as f:
        context["rights"] += f.readlines()

    # アクセス時にエージェント表示
    if request.method=="GET":
        print(request.META.get('HTTP_USER_AGENT', None))

    # 検索情報が送られてきたら……
    if request.method=="POST":

        # POSTから検索queryを取得
        post = request.POST

        # メタ情報を取得
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # 入力情報を取得
        query = post.get("query")
        query_list = [query]
        is_use_name = True if post.get("is_use_name")=="true" else False
        is_use_reading = True if post.get("is_use_reading")=="true" else False
        is_use_artists = True if post.get("is_use_artists")=="true" else False
        type_game = post.get("type")
        request_time = post.get("request_time")

        response = { "query":query, "request_time":request_time, "update_log":" " }

        print(f"[{ip}][{type_game}] q:{query}")

        # 機種選択
        if type_game=="c":
            SD = SongDataC
            SDM = SongDataCManager
        elif type_game=="o":
            SD = SongDataO
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
            song_new = SD.objects.filter(song_release__gt=date_before_2_weekly)
            song_search = [ e for e in song_new ]

            search_hit_count = f"[新曲] {len(song_search)}"
            song_response = [ render_to_string(f"const_search/song_info_{type_game}.html",context={"song":song}) for song in song_search[:30] ]
            song_response.append(render_to_string("const_search/result_info.html",context={"info_text":"新曲を表示しています。検索ワードを入力してね！"}))

        # 検索ワードの処理
        else:

            # 検索

            # 曲名
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

            song_search_by_name = SD.objects.none()
            for q in query_list:
                song_search_by_name = song_search_by_name|SD.objects.filter(song_name__icontains=q)
                # song_search_by_reading = SD.objects.filter(...)

            # アーティスト名
            song_search_by_artists = SD.objects.filter(song_auther__icontains=query)

            # 必要に合わせて結合
            song_search_tmp = SD.objects.none()
            if is_use_name:
                song_search_tmp = song_search_tmp|song_search_by_name
            # if is_use_reading:
            #     song_search_tmp = song_search_tmp|song_search_by_reading
            if is_use_artists:
                song_search_tmp = song_search_tmp|song_search_by_artists

            # リストにして完成
            song_search = [ e for e in song_search_tmp ]

            # 整える
            search_hit_count = len(song_search)
            song_response = [ render_to_string(f"const_search/song_info_{type_game}.html",context={"song":song}) for song in song_search[:30] ]

            # 多すぎたらこうすうる
            if search_hit_count  > 30:
                song_response.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が多すぎだよ〜 もう少しワードを絞ってみてね"}))
            # 少なすぎたらこうする
            if search_hit_count  == 0:
                song_response.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が0件だよ〜 ワードや設定を確認してみてね"}))

        # Jsonとして返す
        response |= {
            "search_response":song_response[::-1],
            "search_hit_count":search_hit_count,
            "search_query_list":sorted(query_list).__str__(),
            "type":type_game,
        }

        return JsonResponse(response)

    # renderする
    return render(request, 'const_search/const_search.html',context=context)
