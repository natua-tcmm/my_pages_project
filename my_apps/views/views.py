from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import os,json,datetime,jaconv,re,unicodedata
from django.conf import settings

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# トップ画面
def top(request):
    context = { "title":"△Natua♪▽のツールとか保管所" ,"is_beta":False, "is_app":False }
    return render(request, 'top.html',context=context)

# 403ページを見るためのview
def preview403(request):
    return render(request,"403.html")

# 404ページを見るためのview
def preview404(request):
    return render(request,"404.html")

# 500ページを見るためのview
def preview500(request):
    return render(request,"500.html")

# 未完成ページ
def incomplete_page(request):
    context = { "title":"未完成のページ" ,"is_beta":False, "is_app":True }
    return render(request, 'incomplete_page.html',context=context)

# --------------------------------------------------

# テンプレート こいつをコピペして作ろう
def app_template(request):
    context = { "title":f"タイトル {title_base}" ,"is_beta":True, "is_app":True }
    return render(request, 'app_template/app_template.html',context=context)

# --------------------------------------------------

# 自己紹介ページ
def about(request):
    context = { "title":f"△Natua♪▽について {title_base}" ,"is_beta":False, "is_app":False }
    return render(request, 'about/about.html',context=context)

# 更新情報ページ
def update_info(request):
    context = { "title":f"更新情報 {title_base}" ,"is_beta":False, "is_app":False }
    return render(request, 'update_info/update_info.html',context=context)

# --------------------------------------------------

# FULLBELLだったら
def fullbell(request):
    context = { "title":f"FULL BELLだったら？  {title_base}" ,"is_beta":False, "is_app":True }
    return render(request, 'fullbell/fullbell.html',context=context)

# BPMチェッカー
def bpm_checker(request):
    context = { "title":f"BPMチェッカー  {title_base}" ,"is_beta":False, "is_app":True }
    return render(request, 'bpm_checker/bpm_checker.html',context=context)

# --------------------------------------------------

# SEGA音ゲー年表
def sega_nenpyo(request):

    context = { "title":f"SEGA音ゲー年表 {title_base}" ,"is_beta":False, "is_app":True }

    return render(request, 'sega_nenpyo/sega_nenpyo.html',context=context)

# オンゲキジャンル
def ongeki_genre(request):

    context = { "title":f"オンゲキジャンル名図鑑 {title_base}" ,"is_beta":False, "is_app":True }

    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"),"r") as f:
        ongeki_genre_json = json.load(f)

    genre_data = ongeki_genre_json["genre_data"]
    updated_date = ongeki_genre_json["updated_date"]

    genre_data = sorted(genre_data.items(), key = lambda e : e[0])
    # genre_data = sorted(genre_data.items(), key = lambda e : e[1])

    context["genre_data"] = genre_data
    context["updated_date"] = updated_date

    return render(request, 'ongeki_genre/ongeki_genre.html',context=context)

# --------------------------------------------------

# 雑多なツール
def random_tools(request):

    context = { "title":f"雑多なツール集 {title_base}" ,"is_beta":False, "is_app":True }

    if request.method=="POST":

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        type = post.get("type")
        query = post.get("query")

        result = ""

        # typeによって分岐
        if type=="unicode":
            table_start = '<table class="table mb-0" id="unicode-table"><thead class="thead-light"><tr><th scope="col">#</th><th scope="col">Char</th><th scope="col">CodePoint</th><th scope="col">Name & Link</th></tr></thead><tbody class="table-hover">'
            table_end = f'</tbody></table><small class="text-muted float-right">Unicode Version: {unicodedata.unidata_version}</small>'

            # 表を生成する
            if not len(query)==0:
                result+=table_start
                for n,char in enumerate(query):
                    char = unicodedata.normalize("NFC", char)
                    codepoint = str.upper(str(hex(ord(char)))[2:]).zfill(4)
                    unicode_name = unicodedata.name(char)
                    unicode_url = f"https://www.compart.com/en/unicode/U+{codepoint}"
                    # result += f"【 {char} 】 : U+{codepoint}\n{unicodedata.name(char)}\nhttps://www.compart.com/en/unicode/U+{codepoint}\n"
                    result += f'<tr><th scope="row">{n}</th><td>{char}</td><td>U+{codepoint}</td><td><a href="{unicode_url}" target="_blank" rel="noopener noreferrer">{unicode_name}</a></td></tr>'
                result+=table_end

        # お返しする
        response = { "result":result }
        return JsonResponse(response)

    return render(request, 'random_tools/random_tools.html',context=context)

# --------------------------------------------------

# データベース
def songdata_chunithm(request):
    file_path = os.path.join(settings.BASE_DIR, 'my_apps/my_data/songdata_chunithm_for_public.json')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/json')
    else:
        raise Http404("JSONファイルが見つかりません")

def songdata_ongeki(request):
    file_path = os.path.join(settings.BASE_DIR, 'my_apps/my_data/songdata_ongeki_for_public.json')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/json')
    else:
        raise Http404("JSONファイルが見つかりません")
