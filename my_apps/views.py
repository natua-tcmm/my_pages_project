from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q

from .models import *

import pandas as pd

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
    context = { "title":"タイトル" ,"is_beta":True, "is_app":True }
    return render(request, 'app_template/app_template.html',context=context)

# --------------------------------------------------

# 自己紹介ページ
def about(request):
    context = { "title":"△Natua♪▽について" ,"is_beta":False, "is_app":False }
    return render(request, 'about/about.html',context=context)

# --------------------------------------------------

# 定数検索ページ
def const_search(request):

    song_data = SongDataC.objects.all()
    context = { "title":"クイック定数検索", "is_beta":True, "is_app":True, "song_data":song_data, "song_data_len":len(song_data) }

    if request.POST:

        # POSTから検索queryを取得
        post = request.POST
        query = post.get("query")
        is_use_name = True if post.get("is_use_name")=="true" else False
        is_use_reading = True if post.get("is_use_reading")=="true" else False
        is_use_artists = True if post.get("is_use_artists")=="true" else False
        type_game = post.get("type")

        response = { "query":query, "update_log":" " }

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

        # 文字が入力されてないなら全部返す
        # 入力されているなら検索して返す
        if query=="/update":
            update_log = SDM.update_song_data()
            response["update_log"] = update_log

        else:
            if query=="":
                song_search = [ e for e in SD.objects.all() ]
            else:
                # 検索設定に沿って絞り込む
                # 検索
                song_search_by_name = SD.objects.filter(song_name__icontains=query)
                # song_search_by_reading = SD.objects.filter(...)
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
                song_search = [ e for e in song_search_tmp]

            # 整える
            search_hit_count = len(song_search)
            song_response = [ render_to_string(f"const_search/song_info_{type_game}.html",context={"song":song}) for song in song_search[:30] ]

            # 多すぎたらこうすうる
            if search_hit_count  > 30:
                song_response.append(render_to_string("const_search/result_info.html",context={}))
            # 少なすぎたらこうする
            if search_hit_count  == 0:
                song_response.append(render_to_string("const_search/result_info.html",context={"info_text":"検索結果が0件だよ〜 ワードや設定を確認してみてね"}))

            # Jsonとして返す
            response |= {
                "search_response":song_response[::-1],
                "search_hit_count":search_hit_count,
                "type":type_game,
            }

        # time.sleep(1)

        return JsonResponse(response)

    # 著作権表示を取得
    context["rights"] = SongDataCManager.get_rights_data() + SongDataOManager.get_rights_data()

    # renderする
    return render(request, 'const_search/const_search.html',context=context)

# FULLBELLだったら
def fullbell(request):
    context = { "title":"FULL BELLだったら？" ,"is_beta":False, "is_app":True }
    return render(request, 'fullbell/fullbell.html',context=context)

# BPMチェッカー
def bpm_checker(request):
    context = { "title":"BPMチェッカー" ,"is_beta":False, "is_app":True }
    return render(request, 'bpm_checker/bpm_checker.html',context=context)

# --------------------------------------------------

# SEGA音ゲー年表
def sega_nenpyo(request):

    context = { "title":"SEGA音ゲー年表" ,"is_beta":False, "is_app":True }

    return render(request, 'sega_nenpyo/sega_nenpyo.html',context=context)

# オンゲキジャンル
def ongeki_genre(request):

    context = { "title":"オンゲキジャンル名図鑑" ,"is_beta":False, "is_app":True }

    genre_data = {

        "Tomahawk":"Lostwizz",
        "Wダイスケ":"脳天直撃",
        "探偵ポップス":"キミは“見ていたね”？",
        "Life":"心",
        "いっぱい":"Don't Fight The Music",
        "Hi-EnergeTech Trance":"Falsum Atlantis.",
        "Starry Chip Rock":"AstrøNotes.",
        "プリンセスナイトロック":"GranFatalité",
        "Sugar core":"Pastel Sprinkles",
        "Hard Musette":"ジャンヌ・ダルクの慟哭",
        "ふんわりディスコ":"SWEET SHAKE!!",
        "PANDORA FOX":"エータ・ベータ・イータ",
        "HARD RENAISSANCE":"LAMIA",
        "progressive/regressive":"Apollo",
        "Meter hardcore":"Dazzle hop",
        "僕らが紡ぐRPG":"おやすみのうた",
        "KizunaEmotions":"絆はずっとGrowing Up!!!",
        "Magical Panic Adventure":"Magical Panic Adventure",
        "TITANOMAKHIA":"Op.I《fear-TITΛN-》",
        "SUPER CORE":"SUPER AMBULANCE",
        "Fluffy Pop":"White Magic Night!",
        "ファンタスティックスペクタクル":"Transcend Lights",
        "BULLET HELL GABBA":"怨撃",
        "Dramatical":"Selenadia",
        "Symphonic Hard Psy":"μ3",
        "MEMORY":"HEADLINER",
        "ChipOrchestra":"Recollect Lines",
        "CYBER PANIC FUSION":"ゲーミングポーラーベア",
        "Girl's House":"Princesses Holiday",
        "BRIGHT":"光焔のラテラルアーク",
        "Lucid Hardcore":"Lazy Addiction",
        "Everlasting Blue":"MarbleBlue.",
        "picopico pop":"Skip & Smile!!",
        "NEOEDOBTZ":"ブツメツビーターズ",
        "Helzh Out":"Ai Nov",
        "Feline Groove":"Sword of Secret",
        "Nightmare":"YURUSHITE",
        "symphonic":"Opfer",
        "LIFE STREAM":"Titania",
        "Classical Hardcore":"Viyella’s Tears",
        "mythology":"Aenbharr",
        "Neuro Opera":"ω4",
        "owl＊samba":"Baqeela",
        "Progressive Fusion":"GEOMETRIC DANCE",
        "Dissociative Identity Disorder":"A Man In The Mirror",
        "220":"R'N'R Monsta",
        "OTAKU HAPPYCORE":"まっすぐ→→→ストリーム！",
        "Amusement Hardcore":"Good bye, Merry-Go-Round.",

    }

    genre_data = sorted(genre_data.items(), key = lambda e : e[0])
    # genre_data = sorted(genre_data.items(), key = lambda e : e[1])

    context["genre_data"] = genre_data

    return render(request, 'ongeki_genre/ongeki_genre.html',context=context)

# --------------------------------------------------

# 課題曲選択
def kadaikyoku(request):
    context = { "title":"課題曲セレクト" ,"is_beta":False, "is_app":False }

    # 試合情報を読み込む
    gamedata = GameDataB2023


    if request.POST:

        # POSTから機種を取得
        post = request.POST
        kisyu = post.get("kisyu")
        game = post.get("game")

        response = { "kisyu":kisyu, "test":f"{kisyu}の{game}が選択されました！", }

        # 機種名から試合名を読み込む
        if len(game)==0:
            if not kisyu.startswith("("):

                # 試合名を読み込む
                game_list = [ o for o in gamedata.objects.filter(game_kisyu=kisyu)]
                games = [ f"{o.game_no} {o.game_player}" for o in game_list ]

                # 試合一覧を整えて返す
                games_response = [ f'<option class="games">{g}</option>' for g in games ]
                response["games_response"]=games_response[::-1]

        # 試合名から試合情報を返す
        else:
            if not game.startswith("("):

                # 試合情報を読み込む
                game_selected = gamedata.objects.filter(game_kisyu=kisyu,game_no=game.split()[0])[0]

                # 試合情報を整形する
                games_info = {

                    "vs_game":game_selected.game_kisyu,
                    "vs_name":game_selected.game_no,
                    "vs_player":game_selected.game_player,

                    "kadai":[

                        game_selected.game_kadai1,
                        game_selected.game_kadai2,
                        game_selected.game_kadai3,

                    ],

                }

                # 課題曲数を数える
                games_info["kadai_count"] =  len([ s for s in games_info["kadai"] if len(s)>0])

                # 試合情報を返す
                response["games_info"]=games_info

        return JsonResponse(response)

    return render(request, 'kadaikyoku/kadaikyoku.html',context=context)
