#!/usr/bin/env python
import json
import re
import html
import copy
import datetime
import os
import time
import logging

# import tqdm.auto as tqdm
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

import requests
from bs4 import BeautifulSoup
import dateutil.parser
import linebot.v3.messaging as bot  # type: ignore

from pathlib import Path
from dotenv import load_dotenv

# --- ログ設定 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# --- 定数 ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, "my_apps/my_data")
JSON_FILE_PATH = os.path.join(DATA_DIR, "songdata_c_dict.json")
JSON_FILE_FOR_PUBLIC_PATH = os.path.join(DATA_DIR, "songdata_chunithm_for_public.json")
OFFICIAL_JSON_URL = "https://chunithm.sega.jp/storage/json/music.json"
REIWAF5_JSON_URL = "https://reiwa.f5.si/chunirec_all.json"

# 環境変数のロード
load_dotenv(verbose=True)
dotenv_path = os.path.join(BASE_DIR.parent, ".env")
load_dotenv(dotenv_path)
LINE_BOT_ACCESS_TOKEN = os.environ.get("LINE_BOT_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

# --- HTTPセッション ---
session = requests.Session()
session.headers.update({"User-Agent": "RefactoredSongDataManager/1.0"})


# --- ユーティリティ ---
def date_to_chunithmversion(date_str: str) -> str:
    """
    日付文字列（YYYY-MM-DD）からオンゲキのバージョン文字列に変換する。
    """
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    d = dateutil.parser.parse(date_str).astimezone(JST).date()
    chunithm_versions = [
        "CHUNITHM",
        "CHUNITHM PLUS",
        "CHUNITHM AIR",
        "CHUNITHM AIR PLUS",
        "CHUNITHM STAR",
        "CHUNITHM STAR PLUS",
        "CHUNITHM AMAZON",
        "CHUNITHM AMAZON PLUS",
        "CHUNITHM CRYSTAL",
        "CHUNITHM CRYSTAL PLUS",
        "CHUNITHM PARADISE",
        "CHUNITHM PARADISE PLUS",
        "CHUNITHM NEW",
        "CHUNITHM NEW PLUS",
        "CHUNITHM SUN",
        "CHUNITHM SUN PLUS",
        "CHUNITHM LUMINOUS",
        "CHUNITHM LUMINOUS PLUS",
        "CHUNITHM VERSE",
    ]
    chunithm_versions_date = [
        datetime.date(2015, 7, 16),
        datetime.date(2016, 2, 4),
        datetime.date(2016, 8, 25),
        datetime.date(2017, 2, 9),
        datetime.date(2017, 8, 24),
        datetime.date(2018, 3, 8),
        datetime.date(2018, 10, 25),
        datetime.date(2019, 4, 11),
        datetime.date(2019, 10, 24),
        datetime.date(2020, 7, 16),
        datetime.date(2021, 1, 21),
        datetime.date(2021, 5, 13),
        datetime.date(2021, 11, 4),
        datetime.date(2022, 4, 14),
        datetime.date(2022, 10, 13),
        datetime.date(2023, 5, 11),
        datetime.date(2023, 12, 14),
        datetime.date(2024, 6, 20),
        datetime.date(2024, 12, 12),
        datetime.date(9999, 12, 31),
    ]
    for i in range(len(chunithm_versions)):
        if chunithm_versions_date[i] <= d < chunithm_versions_date[i + 1]:
            return chunithm_versions[i]
    return "不明"


def decode_unicode_json_file(file_path: str) -> None:
    """
    JSONファイルのUnicodeエスケープを文字列にして上書きする。
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# --- LINE通知 ---
class LineNotification:
    messages: List[str] = []

    @classmethod
    def add_message_by_list(cls, messages: list) -> None:
        """
        通知メッセージを追加する。
        """
        messages[-1] += "\n"
        cls.messages += messages

    @classmethod
    def send_notification(cls) -> None:
        """
        通知メッセージを送信する。
        """
        msg = "\n".join(cls.messages)
        configuration = bot.Configuration(access_token=LINE_BOT_ACCESS_TOKEN)
        message_dict = {"to": LINE_USER_ID, "messages": [{"type": "text", "text": msg}]}
        with bot.ApiClient(configuration) as api:
            api_instance = bot.MessagingApi(api)
            push_message_request = bot.PushMessageRequest.from_dict(message_dict)
            try:
                api_instance.push_message(push_message_request)
                logging.info("LINE通知送信成功↓")
                print(msg)
            except Exception as e:
                logging.error("LINE通知送信失敗↓: %s", e)
                print(msg)


# --- データクラス ---
@dataclass
class SongData:
    song_official_id: str = None
    song_name: str = None
    song_reading: str = None
    song_artist: str = None
    song_genre: str = None
    song_bpm: Optional[int] = None
    song_bpm_nodata: bool = True
    song_release: str = None
    song_release_version: str = None
    song_image_url: str = None
    song_fumen_id: Optional[str] = None  # 文字列5ケタ 01234みたいに
    song_namefolder_name: str = None
    song_namefolder_index: int = None
    is_worldsend: bool = False
    has_ultima: bool = False
    only_ultima: bool = False
    bas_const: Optional[float] = None
    bas_const_nodata: bool = True
    adv_const: Optional[float] = None
    adv_const_nodata: bool = True
    exp_const: Optional[float] = None
    exp_const_nodata: bool = True
    exp_notes: Optional[int] = None
    exp_notes_nodata: bool = True
    exp_notesdesigner: Optional[str] = None
    exp_notesdesigner_nodata: bool = True
    mas_const: Optional[float] = None
    mas_const_nodata: bool = True
    mas_notes: Optional[int] = None
    mas_notes_nodata: bool = True
    mas_notesdesigner: Optional[str] = None
    mas_notesdesigner_nodata: bool = True
    ult_const: Optional[float] = None
    ult_const_nodata: bool = True
    ult_notes: Optional[int] = None
    ult_notes_nodata: bool = True
    ult_notesdesigner: Optional[str] = None
    ult_notesdesigner_nodata: bool = True
    we_star: str = None
    we_kanji: str = None

    @classmethod
    def from_official_data(cls, data: Dict[str, Any]) -> "SongData":
        """
        公式サイトのデータから SongData を生成する。
        ※ WE（worldsend）の場合は we_kanji の有無で判定する
        """
        song = cls()
        song.song_official_id = data.get("id")
        song.song_name = data.get("title")
        song.song_reading = data.get("reading")
        song.song_artist = data.get("artist")
        song.song_genre = data.get("catname")
        song.song_image_url = data.get("image")
        song.is_worldsend = len(data.get("we_kanji", "")) > 0
        song.has_ultima = len(data.get("lev_ult", "")) > 0
        song.only_ultima = False
        if song.is_worldsend:
            song.we_star = data.get("we_star")
            song.we_kanji = data.get("we_kanji")
        return song

    def apply_reiwaf5_data(self, reiwa_data: Dict[str, Any]) -> None:
        """
        reiwaf5のデータから定数情報などを適用する。
        """

        # リリース日
        self.song_release = reiwa_data["meta"]["release"]
        self.song_release_version = date_to_chunithmversion(self.song_release)

        # BASIC
        self.bas_const = reiwa_data["data"]["BAS"]["const"]
        self.bas_const_nodata = False

        # ADVANCED
        # レベルが10未満ならレベルと定数が一致
        if reiwa_data["data"]["ADV"]["level"] < 10:
            self.adv_const = reiwa_data["data"]["ADV"]["level"]
            self.adv_const_nodata = False
        elif reiwa_data["data"]["ADV"]["is_const_unknown"] or reiwa_data["data"]["ADV"]["const"] == 0:
            self.adv_const = reiwa_data["data"]["ADV"]["level"]
            self.adv_const_nodata = True
        else:
            self.adv_const = reiwa_data["data"]["ADV"]["const"]
            self.adv_const_nodata = False

        # EXPERT
        # レベルが10未満ならレベルと定数が一致
        if reiwa_data["data"]["EXP"]["level"] < 10:
            self.exp_const = reiwa_data["data"]["EXP"]["level"]
            self.exp_const_nodata = False
        elif reiwa_data["data"]["EXP"]["is_const_unknown"] or reiwa_data["data"]["EXP"]["const"] == 0:
            self.exp_const = reiwa_data["data"]["EXP"]["level"]
            self.exp_const_nodata = True
        else:
            self.exp_const = reiwa_data["data"]["EXP"]["const"]
            self.exp_const_nodata = False

        # MASTER
        if reiwa_data["data"]["MAS"]["is_const_unknown"] or reiwa_data["data"]["MAS"]["const"] == 0:
            self.mas_const = reiwa_data["data"]["MAS"]["level"]
            self.mas_const_nodata = True
        else:
            self.mas_const = reiwa_data["data"]["MAS"]["const"]
            self.mas_const_nodata = False

        # ULTIMA(存在する場合のみ)
        if self.has_ultima:
            if reiwa_data["data"]["ULT"]["is_const_unknown"] or reiwa_data["data"]["ULT"]["const"] == 0:
                self.ult_const = reiwa_data["data"]["ULT"]["level"]
                self.ult_const_nodata = True
            else:
                self.ult_const = reiwa_data["data"]["ULT"]["const"]
                self.ult_const_nodata = False

    def to_dict(self) -> Dict[str, Any]:
        """
        JSON保存用にSongDataを辞書に変換する。
        """
        return asdict(self)


# --- マネージャークラス ---
class SongDataManager:
    def __init__(self, data_file: str = JSON_FILE_PATH):
        self.data_file = data_file
        self.songs: List[SongData] = []
        self.new_song_offi_ids: List[str] = []
        self.new_ultima_song_offi_ids: List[str] = []
        self.update_song_offi_ids: List[str] = []
        self.delete_song_offi_ids: List[str] = []

    def load_data(self) -> None:
        """
        JSONファイルから既存の楽曲データをロードする。
        """
        if not os.path.exists(self.data_file):
            self.songs = []
            return
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.songs = [SongData(**song) for song in data.get("songs", [])]
        logging.info("既存データロード完了: %d件", len(self.songs))

    def save_data(self) -> None:
        """
        楽曲データをJSONファイルに保存する。
        """
        data = {
            "songs": [song.to_dict() for song in self.songs],
            "new_song_offi_ids": list(set(self.new_song_offi_ids)),
            "update_song_offi_ids": list(set(self.update_song_offi_ids)),
            "delete_song_offi_ids": list(set(self.delete_song_offi_ids)),
            "update_at": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        decode_unicode_json_file(self.data_file)
        logging.info("データ保存完了")

    def save_public_data(self) -> None:
        """
        公開用のJSONファイルを出力する。
        """
        sorted_songs = sorted(self.songs, key=lambda song: int(song.song_official_id))
        public_data = {"songs": []}
        for song in sorted_songs:
            data = song.to_dict()
            public_song = {
                "meta": {
                    "official_id": data.get("song_official_id"),
                    "name": data.get("song_name"),
                    "reading": data.get("song_reading"),
                    "artist": data.get("song_artist"),
                    "genre": data.get("song_genre"),
                    "bpm": data.get("song_bpm"),
                    "bpm_nodata": data.get("song_bpm_nodata"),
                    "release": data.get("song_release"),
                    "release_version": data.get("song_release_version"),
                    "image_url": data.get("song_image_url"),
                    "fumen_id": data.get("song_fumen_id"),
                    "is_worldsend": data.get("is_worldsend"),
                    "has_ultima": data.get("has_ultima"),
                    "only_ultima": data.get("only_ultima"),
                    "we_star": data.get("we_star"),
                    "we_kanji": data.get("we_kanji"),
                },
                "basic": {
                    "const": data.get("bas_const"),
                    "const_nodata": data.get("bas_const_nodata"),
                },
                "advanced": {
                    "const": data.get("adv_const"),
                    "const_nodata": data.get("adv_const_nodata"),
                },
                "expert": {
                    "const": data.get("exp_const"),
                    "const_nodata": data.get("exp_const_nodata"),
                    "notes": data.get("exp_notes"),
                    "notes_nodata": data.get("exp_notes_nodata"),
                    "notesdesigner": data.get("exp_notesdesigner"),
                    "notesdesigner_nodata": data.get("exp_notesdesigner_nodata"),
                },
                "master": {
                    "const": data.get("mas_const"),
                    "const_nodata": data.get("mas_const_nodata"),
                    "notes": data.get("mas_notes"),
                    "notes_nodata": data.get("mas_notes_nodata"),
                    "notesdesigner": data.get("mas_notesdesigner"),
                    "notesdesigner_nodata": data.get("mas_notesdesigner_nodata"),
                },
                "ultima": {
                    "const": data.get("ult_const"),
                    "const_nodata": data.get("ult_const_nodata"),
                    "notes": data.get("ult_notes"),
                    "notes_nodata": data.get("ult_notes_nodata"),
                    "notesdesigner": data.get("ult_notesdesigner"),
                    "notesdesigner_nodata": data.get("ult_notesdesigner_nodata"),
                },
            }
            public_data["songs"].append(public_song)

        # 更新日時の追加
        public_data["update_at"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

        # 指定ファイル名でJSON出力
        with open(JSON_FILE_FOR_PUBLIC_PATH, "w", encoding="utf-8") as f:
            json.dump(public_data, f, indent=4, ensure_ascii=False)

    def _fetch_official_json(self) -> List[Dict[str, Any]]:
        """
        公式サイトから楽曲JSONを取得する。
        """
        try:
            resp = session.get(OFFICIAL_JSON_URL, timeout=10)
            resp.encoding = resp.apparent_encoding
            data = resp.json()
            logging.info("公式データ取得完了: %d件", len(data))
            return data
        except Exception as e:
            logging.error("公式データ取得失敗: %s", e)
            return []

    def _fetch_reiwaf5_json(self) -> List[Dict[str, Any]]:
        """
        reiwaf5から楽曲JSONを取得する。
        """
        try:
            resp = session.get(REIWAF5_JSON_URL, timeout=10)
            resp.encoding = resp.apparent_encoding
            data = resp.json()
            logging.info("reiwaf5データ取得完了: %d件", len(data))
            return data
        except Exception as e:
            logging.error("reiwaf5データ取得失敗: %s", e)
            return []

    def _create_fumen_ids_all(self) -> List[str]:
        """
        譜面保管所の全保管所IDを取得する。
        """
        fumen_ids_all = []
        urls = [
            f"https://www.sdvx.in/chunithm/sort/{g}.htm"
            for g in ["pops", "niconico", "toho", "variety", "irodorimidori", "gekimai", "original"]
        ]
        for url in urls:
            try:
                resp = session.get(url, timeout=10)
                if not resp.ok:
                    logging.error("Failed to get URL: %s", url)
                    continue
                soup = BeautifulSoup(resp.content, "html.parser")
                for line in str(soup).split("\n"):
                    try:
                        m = re.search(r'<script src="/chunithm/.*?/.*?/([0-9]+)sort\.js">', line)
                        if m:
                            fumen_ids_all.append(m.group(1))
                    except Exception:
                        pass
            except Exception as e:
                logging.error("Error fetching URL %s: %s", url, e)
        return fumen_ids_all

    def _search_song_by_official_id(self, offi_id: str) -> Optional[SongData]:
        for song in self.songs:
            if song.song_official_id == offi_id:
                return song
        return None

    def update_new_songs(self) -> None:
        """
        公式データと既存データを比較し、新規楽曲を追加する。
        ※WE楽曲は除外する
        """
        messages = ["----- CHUNITHM -----", "【新曲登録処理】"]
        official_data = self._fetch_official_json()
        reiwa_data_list = self._fetch_reiwaf5_json()

        # 新曲候補を抽出
        new_song_ids = []
        for s_offi in official_data:
            # WE楽曲は除外
            if not len(s_offi.get("we_kanji", "")) > 0:
                if self._search_song_by_official_id(s_offi["id"]) is None:
                    new_song_ids.append(s_offi["id"])

        messages.append(f"新曲候補数: {len(new_song_ids)}")

        # 新曲データ作成
        for s_offi in official_data:
            if s_offi["id"] in new_song_ids:

                # 公式から
                song = SongData.from_official_data(s_offi)
                messages.append(f"- 新曲登録: {song.song_name} (ID: {song.song_official_id})")

                # reiwaf5から
                # WEを除外
                if not song.is_worldsend:
                    matching_reiwa = None
                    for reiwa in reiwa_data_list:
                        if song.song_name in reiwa.get("meta", {}).get("title", ""):
                            matching_reiwa = reiwa
                            song.apply_reiwaf5_data(matching_reiwa)
                            break
                    if matching_reiwa is None:
                        messages.append(f"-- reiwaf5内にデータがありません。song_name: {song.song_name}")

                    # 譜面保管所からの情報はNoDataとする
                    song.song_bpm_nodata = True
                    song.exp_notesdesigner_nodata = True
                    song.mas_notesdesigner_nodata = True
                    song.exp_notes_nodata = True
                    song.mas_notes_nodata = True
                    if song.has_ultima:
                        song.ult_notesdesigner_nodata = True
                        song.ult_notes_nodata = True

                self.songs.append(song)
                self.new_song_offi_ids.append(s_offi["id"])

        messages.append("新曲登録処理完了。")
        LineNotification.add_message_by_list(messages)

    def update_existing_songs(self) -> None:
        """
        定数情報の更新・ULTIMA追加処理・削除曲処理を行う。
        """
        messages = ["【公式・定数データ更新処理】"]
        official_data = self._fetch_official_json()
        reiwa_data_list = self._fetch_reiwaf5_json()

        # 公式データに存在しない楽曲を削除
        current_official_ids = {s.get("id") for s in official_data}
        songs_to_remove = [song for song in self.songs if song.song_official_id not in current_official_ids]
        for song in songs_to_remove:
            messages.append(f"削除曲: {song.song_name}")
            self.songs.remove(song)
            self.delete_song_offi_ids.append(song.song_official_id)

        # ULTIMA追加処理
        for s_offi in official_data:
            # 公式にULTIMAが存在するもので...
            if bool(len(s_offi["lev_ult"]) > 0):
                song = self._search_song_by_official_id(s_offi["id"])
                if not song.is_worldsend:
                    # ULTIMAが存在しないと登録されていたら更新
                    if not song.has_ultima and bool(len(s_offi["lev_ult"]) > 0):
                        self.new_ultima_song_offi_ids.append(s_offi["id"])
                        messages.append(f"ULTIMA追加: {song.song_name}")

                        # 情報更新
                        song.has_ultima = True
                        song.only_ultima = False

                        # 公式から(なし)

                        # reiwaf5から
                        matching_reiwa = None
                        for reiwa in reiwa_data_list:
                            if song.song_name in reiwa.get("meta", {}).get("title", ""):
                                matching_reiwa = reiwa

                                # まだreiwaf5に反映されていないならスキップ
                                if "ULT" not in matching_reiwa["data"]:
                                    self.ult_const_nodata = True

                                elif matching_reiwa["data"]["ULT"]["is_const_unknown"] or matching_reiwa["data"]["ULT"]["const"] == 0:
                                    self.ult_const = matching_reiwa["data"]["ULT"]["level"]
                                    self.ult_const_nodata = True
                                else:
                                    self.ult_const = matching_reiwa["data"]["ULT"]["const"]
                                    self.ult_const_nodata = False

                                break

                        if matching_reiwa is None:
                            messages.append(f"[ULTIMA追加] reiwaf5内にデータがありません。song_name: {song.song_name}")

                        # 譜面保管所からの情報はNoDataとする
                        song.ult_notesdesigner_nodata = True
                        song.ult_notes_nodata = True

        # 日付と定数情報の更新（EXP/MAS/ULT）
        for song in self.songs:
            # worldsend 楽曲は除外
            if song.is_worldsend:
                continue
            # reiwaf5 から定数情報を取得
            matching_reiwa = None
            for reiwa in reiwa_data_list:
                if song.song_name == reiwa.get("meta").get("title"):
                    matching_reiwa = reiwa
                    break
            if not matching_reiwa:
                continue

            # 日付
            if song.song_release != matching_reiwa["meta"]["release"]:
                song.song_release = matching_reiwa["meta"]["release"]
                song.song_release_version = date_to_chunithmversion(song.song_release)
                messages.append(f"リリース日更新: {song.song_name} {song.song_release}")
                self.update_song_offi_ids.append(song.song_official_id)

            # BASIC
            # あと10年くらいはやらなくてもいいと思う

            # ADVANCED
            if (
                song.adv_const_nodata
                and not (matching_reiwa["data"]["ADV"]["is_const_unknown"] or matching_reiwa["data"]["ADV"]["const"] == 0)
                and matching_reiwa["data"]["ADV"]["level"] >= 10
            ):
                messages.append(
                    f"定数更新: {song.song_name} ADVANCED {song.adv_const} -> {matching_reiwa['data']['ADV']['const']}"
                )
                song.adv_const = matching_reiwa["data"]["ADV"]["const"]
                song.adv_const_nodata = False
                self.update_song_offi_ids.append(song.song_official_id)
            # EXPERT
            if (
                song.exp_const_nodata
                and not (matching_reiwa["data"]["EXP"]["is_const_unknown"] or matching_reiwa["data"]["EXP"]["const"] == 0)
                and matching_reiwa["data"]["EXP"]["level"] >= 10
            ):
                messages.append(
                    f"定数更新: {song.song_name} EXPERT {song.exp_const} -> {matching_reiwa['data']['EXP']['const']}"
                )
                song.exp_const = matching_reiwa["data"]["EXP"]["const"]
                song.exp_const_nodata = False
                self.update_song_offi_ids.append(song.song_official_id)
            # MASTER
            if song.mas_const_nodata and not (
                matching_reiwa["data"]["MAS"]["is_const_unknown"] or matching_reiwa["data"]["MAS"]["const"] == 0
            ):
                messages.append(
                    f"定数更新: {song.song_name} MASTER {song.mas_const} -> {matching_reiwa['data']['MAS']['const']}"
                )
                song.mas_const = matching_reiwa["data"]["MAS"]["const"]
                song.mas_const_nodata = False
                self.update_song_offi_ids.append(song.song_official_id)
            # ULTIMA
            if song.has_ultima:

                # まだreiwaf5に反映されていないならスキップ
                if "ULT" not in matching_reiwa["data"]:
                    pass

                elif song.ult_const_nodata and not (
                    matching_reiwa["data"]["ULT"]["is_const_unknown"] or matching_reiwa["data"]["ULT"]["const"] == 0
                ):
                    messages.append(
                        f"定数更新: {song.song_name} ULTIMA {song.ult_const} -> {matching_reiwa['data']['ULT']['const']}"
                    )
                    song.ult_const = matching_reiwa["data"]["ULT"]["const"]
                    song.ult_const_nodata = False
                    self.update_song_offi_ids.append(song.song_official_id)

        # 定数不明曲一覧
        # messages.append("-----\n定数不明曲一覧")
        print("-----\n定数不明曲一覧")
        for song in self.songs:
            if song.adv_const_nodata or song.exp_const_nodata or song.mas_const_nodata or (song.has_ultima and song.ult_const_nodata):
                # messages.append(
                #     f"- {song.song_name} {'[EXPERT]'*song.exp_const_nodata}{'[MASTER]'*song.mas_const_nodata}{'[ULTIMA]'*( song.has_ultima and song.ult_const_nodata)}"
                # )
                print(
                    f"- {song.song_name} {'[EXPERT]'*song.exp_const_nodata}{'[MASTER]'*song.mas_const_nodata}{'[ULTIMA]'*( song.has_ultima and song.ult_const_nodata)}"
                )

        messages.append("公式・定数データ更新処理完了。")
        LineNotification.add_message_by_list(messages)

    def link_fumen_ids(self) -> None:
        """
        譜面保管所の全保管所IDを取得し、既存楽曲データと曲名で突合してリンクする。
        ボーナストラックの場合、元楽曲のリンク先を引き継ぐ処理も行う。
        """
        messages = ["【リンク処理】"]
        fumen_ids_all = self._create_fumen_ids_all()
        known_fumen_ids = [song.song_fumen_id for song in self.songs if song.song_fumen_id and len(song.song_fumen_id) > 1]
        fumen_ids_new = list(set(fumen_ids_all) - set(known_fumen_ids))
        messages.append(f"譜面保管所 新曲候補数: {len(fumen_ids_new)}")
        messages.append("-----\nリンク処理")

        for fumen_id in fumen_ids_new:

            # 新曲候補IDから保管所の登録曲名を取得
            try:
                url = f"https://www.sdvx.in/chunithm/{fumen_id[:2]}/js/{fumen_id}sort.js"
                time.sleep(0.5)
                resp = session.get(url, timeout=10)
                if resp.ok:
                    data = html.unescape(resp.text).replace("\r\n", "").split(";")
                    m = re.search(r"<div class=f\d>(.*?)</div>", data[0])
                    if m:
                        song_name_fumen = re.sub(r"<.*?>", "", m.group(1))
                    else:
                        messages.append(f"- 譜面ID: {fumen_id} の曲名パース失敗")
                        continue
                else:
                    messages.append(f"- 譜面ID: {fumen_id} の取得失敗")
                    continue
            except Exception as e:
                messages.append(f"- 譜面ID: {fumen_id} の取得中エラー: {e}")
                continue

            # 既存楽曲データと突合してリンク
            for song in self.songs:
                # worldsend 楽曲は除外
                if song.is_worldsend:
                    continue
                if song.song_name == song_name_fumen:
                    if song.song_fumen_id is None:
                        song.song_fumen_id = fumen_id
                        messages.append(f"- リンク成功: 『{song.song_name}』 ID:{song.song_official_id}-{song.song_fumen_id}")
                        self.update_song_offi_ids.append(song.song_official_id)
                    else:
                        messages.append(f"- 『{song.song_name}』はリンク済: ID:{song.song_official_id}-{song.song_fumen_id}")
                    break
            else:
                messages.append(f"- 『{song_name_fumen}』のリンクに失敗。ID: None - {fumen_id}")

        # 未リンク楽曲一覧
        # messages.append("-----\n未リンク曲一覧")
        print("-----\n未リンク曲一覧")
        for song in self.songs:
            if song.song_fumen_id is None and not song.is_worldsend:
                # messages.append(f"- {song.song_name}")
                print(f"- {song.song_name}")

        messages.append("リンク処理完了。")
        LineNotification.add_message_by_list(messages)

    def update_fumen_data(self) -> None:
        """
        譜面保管所から各楽曲の譜面情報をスクレイピングして更新する。
        新曲および新ULTIMA・nodataがある楽曲について、BPM、ノーツ数、NOTES DESIGNERを更新する。
        """

        messages = ["【保管所データ更新】"]
        logging.info("譜面保管所データ更新処理開始")

        # 取得対象の楽曲インデックスを収集
        target_index = []
        for i, song in enumerate(self.songs):
            if song.song_fumen_id is None:
                continue

            is_nodata = (
                (
                    (not song.only_ultima)
                    and (
                        song.exp_notes_nodata
                        or song.exp_notesdesigner_nodata
                        or song.mas_notes_nodata
                        or song.mas_notesdesigner_nodata
                    )
                )
                or (song.has_ultima and (song.ult_notes_nodata or song.ult_notesdesigner_nodata))
                or song.song_bpm_nodata
            )

            # 新曲の場合は必ず更新対象、それ以外はULTIMA追加曲とnodataがあるものを対象とする
            if song.song_official_id in self.new_song_offi_ids:
                is_new_song = True
            elif (song.song_official_id in self.new_ultima_song_offi_ids) or is_nodata:
                is_new_song = False
            else:
                continue
            target_index.append(i)

        logging.info("更新対象楽曲数: %d", len(target_index))

        # 対象楽曲ごとに更新処理
        for i in target_index:
            song: SongData = self.songs[i]
            updated = False  # この楽曲で変更があったかどうか

            url = f"https://www.sdvx.in/chunithm/{song.song_fumen_id[:2]}/js/{song.song_fumen_id}sort.js"
            try:
                time.sleep(0.5)
                resp = session.get(url, timeout=10)
                if resp.ok:
                    data_parts = html.unescape(resp.text).replace("\r\n", "").split(";")
                    # WE楽曲は除外
                    if not song.is_worldsend:
                        # BPM 更新
                        bpm_match = re.search(r"<td class=f\d>(.*?)</table>", data_parts[2])
                        if bpm_match:
                            try:
                                new_bpm = int(bpm_match.group(1))
                                if song.song_bpm_nodata or song.song_bpm != new_bpm:
                                    messages.append(f"『{song.song_name}』: BPM updated to {new_bpm}")
                                    song.song_bpm = new_bpm
                                    song.song_bpm_nodata = False
                                    updated = True
                            except Exception as e:
                                song.song_bpm_nodata = True
                        else:
                            song.song_bpm_nodata = True

                        # EXPERT / MASTER NOTES DESIGNER 更新
                        nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[3])
                        new_exp_notesdesigner = nd_match.group(1) if nd_match and nd_match.group(1) else None
                        if song.exp_notesdesigner != new_exp_notesdesigner or song.exp_notesdesigner_nodata != (not (bool(nd_match) and bool(nd_match.group(1)))):
                            song.exp_notesdesigner = new_exp_notesdesigner
                            song.exp_notesdesigner_nodata = not bool(nd_match)
                            messages.append(f"『{song.song_name}』: EXP NOTES DESIGNER updated to {new_exp_notesdesigner}")
                            updated = True

                        nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[4])
                        new_mas_notesdesigner = nd_match.group(1) if nd_match and nd_match.group(1) else None
                        if song.mas_notesdesigner != new_mas_notesdesigner or song.mas_notesdesigner_nodata != (not (bool(nd_match) and bool(nd_match.group(1)))):
                            song.mas_notesdesigner = new_mas_notesdesigner
                            song.mas_notesdesigner_nodata = not bool(nd_match)
                            messages.append(f"『{song.song_name}』: MASTER NOTES DESIGNER updated to {new_mas_notesdesigner}")
                            updated = True

                        # EXPERT NOTES 更新
                        notes_match = re.search(r"<td class=exp1>(.*?)</table>", data_parts[11])
                        if notes_match:
                            try:
                                new_exp_notes = int(notes_match.group(1))
                                if song.exp_notes_nodata or song.exp_notes != new_exp_notes:
                                    messages.append(f"『{song.song_name}』: EXP NOTES updated to {new_exp_notes}")
                                    song.exp_notes = new_exp_notes
                                    song.exp_notes_nodata = False
                                    updated = True
                            except Exception as e:
                                song.exp_notes_nodata = True
                        else:
                            song.exp_notes_nodata = True

                        # MASTER NOTES 更新
                        notes_match = re.search(r"<td class=mst1>(.*?)</table>", data_parts[12])
                        if notes_match:
                            try:
                                new_mas_notes = int(notes_match.group(1))
                                if song.mas_notes_nodata or song.mas_notes != new_mas_notes:
                                    messages.append(f"『{song.song_name}』: MASTER NOTES updated to {new_mas_notes}")
                                    song.mas_notes = new_mas_notes
                                    song.mas_notes_nodata = False
                                    updated = True
                            except Exception as e:
                                song.mas_notes_nodata = True
                        else:
                            song.mas_notes_nodata = True
                else:
                    messages.append(f"[fumen] 取得失敗 {song.song_fumen_id}")
                    # 新曲の場合は、request failed時に各項目をnodataにする
                    if is_new_song:
                        if not song.is_worldsend:
                            song.song_bpm_nodata = True
                            song.exp_notesdesigner_nodata = True
                            song.mas_notesdesigner_nodata = True
                            song.exp_notes_nodata = True
                            song.mas_notes_nodata = True

                # ULTIMA 更新
                if song.has_ultima:
                    ult_url = f"https://www.sdvx.in/chunithm/ult/js/{song.song_fumen_id}ult.js"
                    resp_ult = session.get(ult_url, timeout=10)
                    if resp_ult.ok:
                        data_parts = html.unescape(resp_ult.text).replace("\r\n", "").split(";")

                        # ULTIMA NOTES DESIGNER
                        nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[3])
                        new_ult_notesdesigner = nd_match.group(1) if nd_match and nd_match.group(1) else None
                        if song.ult_notesdesigner != new_ult_notesdesigner or song.ult_notesdesigner_nodata != (not (bool(nd_match) and bool(nd_match.group(1)))):
                            song.ult_notesdesigner = new_ult_notesdesigner
                            song.ult_notesdesigner_nodata = not bool(nd_match)
                            messages.append(f"『{song.song_name}』: ULT NOTES DESIGNER updated to {new_ult_notesdesigner}")
                            updated = True

                        # ULTIMA NOTES
                        notes_match = re.search(r"<td class=ult1>(.*?)</table>", data_parts[5])
                        if notes_match:
                            try:
                                new_ult_notes = int(notes_match.group(1))
                                if song.ult_notes_nodata or song.ult_notes != new_ult_notes:
                                    messages.append(f"『{song.song_name}』: ULT NOTES updated to {new_ult_notes}")
                                    song.ult_notes = new_ult_notes
                                    song.ult_notes_nodata = False
                                    updated = True
                            except Exception as e:
                                song.ult_notes_nodata = True
                        else:
                            song.ult_notes_nodata = True
                    else:
                        messages.append(f"[fumen] 取得失敗 (ULT) {song.song_fumen_id}")
                        # 新曲の場合は、request failed時に各項目をnodataにする
                        if is_new_song:
                            song.ult_notesdesigner_nodata = True
                            song.ult_notes_nodata = True
            except Exception as e:
                messages.append(f"[fumen] エラー: {song.song_name} {song.song_fumen_id} - {e}")
            if updated:
                self.update_song_offi_ids.append(song.song_official_id)
        messages.append("保管所データ更新完了。")
        LineNotification.add_message_by_list(messages)

    def update_namefolder_index(self) -> None:
        """
        楽曲名順フォルダ用のインデックスを更新する。
        """

        # フォルダに振り分ける
        for song in self.songs:
            c = song.song_reading[0]
            if "A" <= c <= "G":
                song.song_namefolder_name = "A-G"
            elif "H" <= c <= "N":
                song.song_namefolder_name = "H-N"
            elif "O" <= c <= "U":
                song.song_namefolder_name = "O-U"
            elif "V" <= c <= "Z":
                song.song_namefolder_name = "V-Z"
            elif "ア" <= c <= "オ":
                song.song_namefolder_name = "あ行"
            elif "カ" <= c <= "コ":
                song.song_namefolder_name = "か行"
            elif "サ" <= c <= "ソ":
                song.song_namefolder_name = "さ行"
            elif "タ" <= c <= "ト":
                song.song_namefolder_name = "た行"
            elif "ナ" <= c <= "ノ":
                song.song_namefolder_name = "な行"
            elif "ハ" <= c <= "ホ":
                song.song_namefolder_name = "は行"
            elif "マ" <= c <= "モ":
                song.song_namefolder_name = "ま行"
            elif "ヤ" <= c <= "ヨ":
                song.song_namefolder_name = "や行"
            elif "ラ" <= c <= "ロ":
                song.song_namefolder_name = "ら行"
            elif "ワ" <= c <= "ン":
                song.song_namefolder_name = "わ行"
            else:
                song.song_namefolder_name = "数字"

        # インデックスを求める
        foldered_songs = {}
        for song in self.songs:
            foldered_songs.setdefault(song.song_namefolder_name, []).append(song)

        for folder_name, songs in foldered_songs.items():
            sorted_songs = sorted(songs, key=lambda s: s.song_reading)
            for index, song in enumerate(sorted_songs, start=1):
                song.song_namefolder_index = index

def main() -> None:

    # 準備
    manager = SongDataManager()
    manager.load_data()

    # 新曲登録処理
    manager.update_new_songs()

    # 既存曲更新処理
    manager.update_existing_songs()

    # 保管所IDリンク処理
    manager.link_fumen_ids()

    # 譜面データの更新
    manager.update_fumen_data()

    # 楽曲名順フォルダ用のインデックス更新
    manager.update_namefolder_index()

    # データ保存
    manager.save_data()
    manager.save_public_data()
    LineNotification.send_notification()


if __name__ == "__main__":
    main()
