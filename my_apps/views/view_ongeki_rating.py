from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from ..models import *

from ..my_script.fetch_osl import get_ongeki_score_log_player_data

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# テンプレート こいつをコピペして作ろう
def ongeki_rating_all(request):
    context = { "title":f"オンゲキベスト枠計算(全曲対象) {title_base}" ,"is_beta":False, "is_app":True }


    # Ajax処理
    if request.method=="POST":

        # メタ情報を取得
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        osl_id = post.get("osl_id")
        music_rate_type = post.get("music_rate_type")

        # OngekiScoreLogにrequest送る
        player_data,records_data_list,_ = get_ongeki_score_log_player_data(osl_id)
        response = {"player_data":player_data,"records":records_data_list}

        # ベスト枠を算出
        rating_all_best_songs_raw = sorted(response["records"], key=lambda x:x[music_rate_type], reverse=True )[:30]
        music_rate_list = []
        music_rate_max = 0
        rating_all_best_songs_str = []
        for i,d in enumerate(rating_all_best_songs_raw):
            music_rate_list.append(d[music_rate_type])
            a_song_dict = {
                "n":f"{i+1:3n}",
                "const":f'{d["const"]:2.1f}',
                "score":f'{d["t-score"]:7n}',
                "diff":f'{d["difficulty"][:3]}',
                "title":f'{d["title"]}',
            }
            if music_rate_type=="music_rate":
                a_song_dict["music_rate"] = f'{d["music_rate"]:2.3f}'
            elif music_rate_type=="music_rate_old":
                a_song_dict["music_rate"] = f'{d["music_rate_old"]:2.2f}'
            rating_all_best_songs_str.append(a_song_dict)
            if d["difficulty"] != "LUNATIC":
                music_rate_max = max(music_rate_max,d[music_rate_type])

        if music_rate_type=="music_rate":
            result_best = int(sum(music_rate_list)*1000/30)/1000
            result_range = int((music_rate_list[0]-music_rate_list[-1])*1000)/1000
        elif music_rate_type=="music_rate_old":
            result_best = int(sum(music_rate_list)*100/30)/100
            result_range = int((music_rate_list[0]-music_rate_list[-1])*100)/100
        # result_reachable = int(( sum(music_rate_list)*3/120 + music_rate_max/4 )*100)/100

        # 情報収集
        ToolUsageManager.add_usage(
            request, "ongeki_rating_all", ""
        )

        # プレイヤー情報を描画
        c = {
            "name":player_data["name"],
            "rating":player_data["rating"],
            "max_rating":player_data["max_rating"],
            "result_best":result_best,
            # "result_reachable":result_reachable,
            "result_range":result_range,
        }
        or_player_info_table_html = render_to_string("ongeki_rating_all/or_player_info_table.html",context=c)

        # ベスト枠を描画
        c = {
            "rating_all_best_songs_str":rating_all_best_songs_str
        }
        or_rating_table_html = render_to_string("ongeki_rating_all/or_rating_table.html",context=c)


        # お返しする
        ajax_response = { "summary":or_player_info_table_html ,"result":or_rating_table_html }
        return JsonResponse(ajax_response)

    return render(request, 'ongeki_rating_all/ongeki_rating_all.html',context=context)
