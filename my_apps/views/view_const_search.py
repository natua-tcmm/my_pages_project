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

    template_name = "const_search/const_search.html"

    songdata_manager = SongDataCNManager
    type_game = "c"
    display_type = "s"
    search_settings = {
        "is_use_name": True,
        "is_use_artists": False,
        "is_use_nd": False,
        "is_use_bpm": False,
        "bpm_from": None,
        "bpm_to": None,
        "is_use_notes": False,
        "notes_from": None,
        "notes_to": None,
        "is_disp_bonus": False,
        "is_use_lunatic_option": False,
        "lunatic_option": None,
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
            if key in ["bpm_from", "bpm_to", "notes_from", "notes_to", "lunatic_option"]:
                self.search_settings[key] = post.get(f"search_settings[{key}]")
            else:
                self.search_settings[key] = post.get(f"search_settings[{key}]") == "true"
        self.type_game = post.get("type")
        self.display_type = post.get("display_type")
        request_time = post.get("request_time")

        # レスポンス初期化
        response = {"query": query, "request_time": request_time}
        search_hit_count = 0
        search_results_html = ""

        # IP情報の取得
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")
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
        if query == "" and self.display_type == "s":
            # 2週間以内の新曲を取得
            date_before_2_weekly = (datetime.date.today() - datetime.timedelta(days=15)).strftime("%Y-%m-%d")
            search_results_song_list = self.songdata_manager.get_new_songs(date_before_2_weekly)
            search_hit_count = f"[新曲] {len(search_results_song_list)}"

            # 検索結果のレンダリング
            search_results_html = [
                render_to_string(f"const_search/song_info_{self.type_game}_{self.display_type}.html", context={"song": song})
                for song in search_results_song_list[:30]
            ]
            search_results_html.append(
                render_to_string(
                    "const_search/result_info.html", context={"info_text": "新曲を表示しています。検索ワードを入力してね！"}
                )
            )

        # 検索ワードがある場合
        else:
            # 検索ワード処理
            search_results_song_list = self.songdata_manager.search_song_by_query(query, self.search_settings)
            search_hit_count = len(search_results_song_list)

            # 検索結果のレンダリング
            search_results_html = self._render_search_result(search_results_song_list, self.type_game, self.display_type)

        # --------------------------------------------------
        # レスポンスの生成
        # --------------------------------------------------
        response |= {
            "search_response": search_results_html[::-1],
            "search_hit_count": search_hit_count,
            # "search_query_list": sorted(query_list).__str__(),
            "query_input": query,
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

    # 結果のレンダリング
    def _render_search_result(self, search_results_song_list, type_game, display_type):
        search_hit_count = len(search_results_song_list)
        search_results_html = [
            render_to_string(f"const_search/song_info_{type_game}_{display_type}.html", context={"song": song})
            for song in search_results_song_list[:30]
        ]

        # 多すぎたら注意メッセージ
        if search_hit_count > 30:
            search_results_html.append(
                render_to_string(
                    "const_search/result_info.html",
                    context={"info_text": "検索結果が多すぎだよ〜 もう少しワードを絞ってみてね"},
                )
            )
        # 0件ならその旨メッセージ
        if search_hit_count == 0:
            search_results_html.append(
                render_to_string(
                    "const_search/result_info.html", context={"info_text": "検索結果が0件だよ〜 検索ワードや設定を確認してみてね"}
                )
            )
        return search_results_html
