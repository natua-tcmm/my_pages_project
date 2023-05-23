from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q

from .models import SongData,SongDataManager


# --------------------------------------------------

# トップ画面
def top(request):
    context = { "title":"△Natua♪▽のツールとか保管所" ,"is_beta":True, "is_app":False }
    return render(request, 'top.html',context=context)

# 404ページを見るためのview
def preview404(request):
    return render(request,"404.html")

# --------------------------------------------------

# 定数検索ページ
def const_search(request):

    song_data = SongData.objects.all()
    context = { "title":"クイック定数検索", "is_beta":True, "is_app":True, "song_data":song_data, "song_data_len":len(song_data) }

    if request.POST:

        # POSTから検索queryを取得
        post = request.POST
        query = post.get("query")
        is_use_name = True if post.get("is_use_name")=="true" else False
        is_use_reading = True if post.get("is_use_reading")=="true" else False
        is_use_artists = True if post.get("is_use_artists")=="true" else False


        # 文字が入力されてないなら全部返す
        # 入力されているなら検索して返す
        if query=="":
            song_search = [ e for e in SongData.objects.all() ]
        else:
            # 検索設定に沿って絞り込む
            # 検索
            song_search_by_name = SongData.objects.filter(song_name__icontains=query)
            # song_search_by_reading = SongData.objects.filter(...)
            song_search_by_artists = SongData.objects.filter(song_auther__icontains=query)

            # 必要に合わせて結合
            song_search_tmp = SongData.objects.none()
            if is_use_name:
                song_search_tmp = song_search_tmp|song_search_by_name
            # if is_use_reading:
            #     song_search_tmp = song_search_tmp|song_search_by_reading
            if is_use_artists:
                song_search_tmp = song_search_tmp|song_search_by_artists

            # リストにして完成
            song_search = [ e for e in song_search_tmp]

        # 整える
        search_hit_count = len(song_search)
        song_response = [ render_to_string("const_search/song_info.html",context={"song":song}) for song in song_search[:30] ]

        # 多すぎたらこうすうる
        if search_hit_count  > 30:
            song_response.append(render_to_string("const_search/result_info.html",context={}))
        # 少なすぎたらこうする
        if search_hit_count  == 0:
            song_response.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が0件だよ〜 ワードや設定を確認してみてね"}))

        # Jsonとして返す
        d = {
                "query":query,
                "search_response":song_response[::-1],
                "search_hit_count":search_hit_count,
            }

        # time.sleep(1)

        return JsonResponse(d)

    # 著作権表示を取得
    context["rights"]  = SongDataManager.get_rights_data()

    # renderする
    return render(request, 'const_search.html',context=context)

# app2
def app2(request):
    context = { "title":"アプリ2(仮)" ,"is_beta":True, "is_app":True }
    return render(request, 'app2.html',context=context)
