from django.views import View
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpRequest
from django.db.models import Q
from django.forms.models import model_to_dict

from ..models import *

import os, json, datetime, jaconv, re, unicodedata
from django.conf import settings

# --------------------------------------------------
title_base = "| △Natua♪▽のツールとか保管所"
# --------------------------------------------------

class ConstSearchView(View):

    template_name = 'const_search/const_search.html'

    songdata_manager = SongDataCNManager
    type_game = "c"
    search_settings = {
        "is_use_name": True,
        "is_use_reading": True,
        "is_use_artists": False,
        # TODO search_settingsの設定を追加・調整
    }

    def get(self, request, *args, **kwargs):
        context = {
            "title": f"クイック定数検索+ {title_base}",
            "is_beta": False,
            "is_app": True,
            "song_data_len": "-",
            "const_update_time": self._get_update_time_str(),
            "rights": self._get_rights_data(),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        post = request.POST

        # 入力情報の取得
        query = post.get("query")
        for key in self.search_settings.keys():
            self.search_settings[key] = (post.get(key) == "true")
        self.type_game = post.get("type")
        request_time = post.get("request_time")

        # レスポンス初期化
        response = {"query": query, "request_time": request_time}
        query_list = []
        search_hit_count = 0
        search_results_html = ""

        # IP情報の取得
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        print(f"[{ip}][{self.type_game}] q:{query}")

        # 機種選択
        if self.type_game == "c":
            self.songdata_manager = SongDataCNManager
        elif self.type_game == "o":
            self.songdata_manager = SongDataONManager
        else:
            raise ValueError

        # --------------------------------------------------
        # 検索処理
        # --------------------------------------------------

        # 検索ワードがない場合
        # 初期状態：新曲表示
        if query == "":
            # 2週間以内の新曲を取得
            date_before_2_weekly = (datetime.date.today() - datetime.timedelta(days=15)).strftime("%Y-%m-%d")
            search_results_song_list = self.songdata_manager.get_new_songs(date_before_2_weekly)
            search_hit_count = f"[新曲] {len(search_results_song_list)}"

            # 検索結果のレンダリング
            search_results_html = [
                render_to_string(f"const_search/song_info_{self.type_game}.html", context={"song": song})
                for song in search_results_song_list[:30]
            ]
            search_results_html.append(
                render_to_string("const_search/result_info.html", context={"info_text": "新曲を表示しています。検索ワードを入力してね！"})
            )

        # 検索ワードがある場合
        else:
            # 検索ワード処理
            query_list = self._create_query_list(query)
            search_results_song_list = self.songdata_manager.search_song_by_query_list(query_list, self.search_settings)
            search_hit_count = len(search_results_song_list)

            # 検索結果のレンダリング
            search_results_html = self._render_search_result(search_results_song_list, self.type_game)

        # --------------------------------------------------
        # レスポンスの生成
        # --------------------------------------------------
        response |= {
            "search_response": search_results_html[::-1],
            "search_hit_count": search_hit_count,
            "search_query_list": sorted(query_list).__str__(),
            "type": self.type_game,
        }
        return JsonResponse(response)


    # 更新日を取得
    def _get_update_time_str(self):
        return f"最終更新: {SongDataCNManager.get_update_time()} | {SongDataONManager.get_update_time()}"

    # 著作権データの取得
    def _get_rights_data(self):
        rights_list = []
        rights_list += ["【CHUNITHM】"]
        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"), "r") as f:
            rights_list += f.readlines()
        rights_list += ["", "【オンゲキ】"]
        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"), "r") as f:
            rights_list += f.readlines()
        return rights_list

    # query_listの生成
    def _create_query_list(self,query):
        query_list = [query]

        # 末尾にアルファベットがあれば消す
        if re.match(r".*^[\u3040-\u309F]+[a-zA-Z]{1}$", query):
            query_list += [query[:-1]]
        if re.match(r".*^[\u3040-\u309F]+[a-zA-Z]{2}$", query):
            query_list += [query[:-2]]

        # ひらがな・カタカナ変換
        for q in query_list[:]:
            query_list += [jaconv.kata2hira(q), jaconv.hira2kata(q)]

        # 重複削除
        query_list = list(set(query_list))
        return query_list

    # 結果のレンダリング
    def _render_search_result(self,search_results_song_list, type_game):
        search_hit_count = len(search_results_song_list)
        search_results_html = [
            render_to_string(f"const_search/song_info_{type_game}.html", context={"song": song})
            for song in search_results_song_list[:30]
        ]

        # 多すぎたら注意メッセージ
        if search_hit_count > 30:
            search_results_html.append(
                render_to_string("const_search/result_info.html", context={"info_text": "検索結果が多すぎだよ〜 もう少しワードを絞ってみてね"})
            )
        # 0件ならその旨メッセージ
        if search_hit_count == 0:
            search_results_html.append(
                render_to_string("const_search/result_info.html", context={"info_text": "検索結果が0件だよ〜 ワードや設定を確認してみてね"})
            )
        return search_results_html
