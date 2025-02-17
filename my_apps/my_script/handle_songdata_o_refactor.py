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
JSON_FILE_PATH = os.path.join(BASE_DIR,"my_apps/my_data/songdata_o_dict.json")
ONGEKI_GENRE_JSON_FILE_PATH = os.path.join(BASE_DIR,"my_apps/my_data/ongeki_genre_data.json")

# 環境変数のロード
load_dotenv(verbose=True)
dotenv_path = os.path.join(BASE_DIR.parent, '.env')
load_dotenv(dotenv_path)
LINE_BOT_ACCESS_TOKEN = os.environ.get("LINE_BOT_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

OFFICIAL_JSON_URL = "https://ongeki.sega.jp/assets/json/music/music.json"
REIWAF5_JSON_URL = "https://reiwa.f5.si/ongeki_const_all.json"

# --- HTTPセッション ---
session = requests.Session()
session.headers.update({"User-Agent": "RefactoredSongDataManager/1.0"})


# --- ユーティリティ ---
def date_to_ongekiversion(date_str: str) -> str:
    """
    日付文字列（YYYY-MM-DD）からオンゲキのバージョン文字列に変換する。
    """
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    d = dateutil.parser.parse(date_str).astimezone(JST).date()
    ongeki_versions = [
        "無印",
        "PLUS",
        "SUMMER",
        "SUMMER PLUS",
        "R.E.D.",
        "R.E.D. PLUS",
        "bright",
        "bright MEMORY Act.1",
        "bright MEMORY Act.2",
        "bright MEMORY Act.3",
    ]
    ongeki_versions_date = [
        datetime.date(2018, 7, 26),
        datetime.date(2019, 2, 7),
        datetime.date(2019, 8, 22),
        datetime.date(2020, 2, 20),
        datetime.date(2020, 9, 30),
        datetime.date(2021, 3, 31),
        datetime.date(2021, 10, 21),
        datetime.date(2022, 3, 3),
        datetime.date(2022, 8, 4),
        datetime.date(2024, 3, 7),
        datetime.date(9999, 12, 31),
    ]
    for i in range(len(ongeki_versions)):
        if ongeki_versions_date[i] <= d < ongeki_versions_date[i + 1]:
            return ongeki_versions[i]
    return "不明"


def string_level_to_float(level_str: str) -> float:
    """
    レベル文字列（末尾に"+"がある場合は0.5を加算）を数値に変換する。
    """
    if level_str.endswith("+"):
        return float(int(level_str[:-1])) + 0.5
    return float(int(level_str))


def format_date(date_raw: str) -> str:
    """
    日付文字列（例："20200101"）を"YYYY-MM-DD"形式に変換する。
    """
    if len(date_raw) == 8:
        return f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
    return date_raw


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
    song_official_id_lunatic: Optional[str] = None
    song_name: str = None
    song_reading: str = None
    song_subname: Optional[str] = None
    song_subname_nodata: bool = True
    song_artist: str = None
    song_genre: str = None
    song_bpm: Optional[int] = None
    song_bpm_nodata: bool = True
    song_release: str = None
    song_release_version: str = None
    song_release_lunatic: Optional[str] = None
    song_release_lunatic_version: Optional[str] = None
    song_image_url: str = None
    song_fumen_id: Optional[str] = None
    character: str = None
    character_lunatic: Optional[str] = None
    is_bonus: bool = False
    has_lunatic: bool = False
    only_lunatic: bool = False
    is_remaster: Optional[bool] = None
    is_remaster_nodata: bool = True
    exp_const: Optional[float] = None
    exp_const_nodata: bool = True
    exp_notes: Optional[int] = None
    exp_notes_nodata: bool = True
    exp_bell: Optional[int] = None
    exp_bell_nodata: bool = True
    exp_notesdesigner: Optional[str] = None
    exp_notesdesigner_nodata: bool = True
    mas_const: Optional[float] = None
    mas_const_nodata: bool = True
    mas_notes: Optional[int] = None
    mas_notes_nodata: bool = True
    mas_bell: Optional[int] = None
    mas_bell_nodata: bool = True
    mas_notesdesigner: Optional[str] = None
    mas_notesdesigner_nodata: bool = True
    lun_const: Optional[float] = None
    lun_const_nodata: bool = True
    lun_notes: Optional[int] = None
    lun_notes_nodata: bool = True
    lun_bell: Optional[int] = None
    lun_bell_nodata: bool = True
    lun_notesdesigner: Optional[str] = None
    lun_notesdesigner_nodata: bool = True

    @classmethod
    def from_official_data(cls, data: Dict[str, Any], is_only_lunatic: bool = False) -> "SongData":
        """
        公式サイトのデータからSongDataを生成する。
        """
        song = cls()
        song.song_official_id = data.get("id")
        song.song_name = data.get("title")
        song.song_reading = data.get("title_sort")
        song.song_artist = data.get("artist")
        song.song_genre = data.get("category")
        song.song_image_url = data.get("image_url")
        song.is_bonus = data.get("bonus") == "1"

        # LUNATIC用のID・キャラ設定
        if is_only_lunatic:
            song.song_official_id_lunatic = data.get("id")
            song.character_lunatic = data.get("character")
            song.character = data.get("character")
        else:
            song.character = data.get("character")

        raw_date = data.get("date")
        date_str = format_date(raw_date)
        song.song_release = date_str
        song.song_release_version = date_to_ongekiversion(date_str)

        # LUNATICならリリース日を通常と同一にする
        if is_only_lunatic:
            song.song_release_lunatic = date_str
            song.song_release_lunatic_version = date_to_ongekiversion(date_str)
        return song

    def apply_reiwaf5_data(self, reiwa_data: Dict[str, Any], is_lunatic: bool = False, is_only_lunatic: bool = False) -> None:
        """
        reiwaf5のデータから定数情報などを適用する。
        """
        if is_lunatic:
            # LUNATIC
            lun_info = reiwa_data.get("lunatic", {})
            if bool(lun_info.get("is_unknown")) and lun_info.get("level") != "0":
                self.lun_const = string_level_to_float(lun_info.get("level"))
                self.lun_const_nodata = True
            else:
                self.lun_const = lun_info.get("const")
                self.lun_const_nodata = False

            if is_only_lunatic:
                self.exp_const_nodata = True
                self.exp_notes_nodata = True
                self.exp_bell_nodata = True
                self.exp_notesdesigner_nodata = True
                self.mas_const_nodata = True
                self.mas_notes_nodata = True
                self.mas_bell_nodata = True
                self.mas_notesdesigner_nodata = True

        else:
            # EXPERT / MASTER
            expert_info = reiwa_data.get("expert", {})
            master_info = reiwa_data.get("master", {})
            level_expert = string_level_to_float(expert_info.get("level"))
            # レベル10未満はレベルと定数が一致する
            if level_expert < 10:
                self.exp_const = level_expert
                self.exp_const_nodata = False
            elif bool(expert_info.get("is_unknown")):
                self.exp_const = string_level_to_float(expert_info.get("level"))
                self.exp_const_nodata = True
            else:
                self.exp_const = expert_info.get("const")
                self.exp_const_nodata = False

            if bool(master_info.get("is_unknown")):
                self.mas_const = string_level_to_float(master_info.get("level"))
                self.mas_const_nodata = True
            else:
                self.mas_const = master_info.get("const")
                self.mas_const_nodata = False

    def to_dict(self) -> Dict[str, Any]:
        """
        JSON保存用にSongDataを辞書に変換する。
        """
        return asdict(self)


# --- マネージャークラス ---
class SongDataManager:
    def __init__(self, data_file: str = JSON_FILE_PATH, genre_file: str = ONGEKI_GENRE_JSON_FILE_PATH):
        self.data_file = data_file
        self.genre_file = genre_file
        self.songs: List[SongData] = []
        self.new_song_offi_ids: List[str] = []
        self.new_lunatic_song_offi_ids: List[str] = []
        self.update_song_offi_ids: List[str] = []
        self.delete_song_offi_ids: List[str] = []
        self.update_at: Optional[str] = None
        self.genre_dict: Dict[str, str] = self._load_genre_data()

    def _load_genre_data(self) -> Dict[str, str]:
        """
        ジャンルデータをロードする。
        """
        try:
            with open(self.genre_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 公式コードと同様、キーと値を反転
            return {str(v): str(k) for k, v in data.get("genre_data", {}).items()}
        except Exception as e:
            logging.error("ジャンルファイル読み込み失敗: %s", e)
            return {}

    def load_data(self) -> None:
        """
        JSONファイルから既存の楽曲データをロードする。
        """
        if not os.path.exists(self.data_file):
            self.songs = []
            return
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # self.new_song_offi_ids = data.get("new_song_offi_ids", [])
        # self.new_lunatic_song_offi_ids = data.get("new_lunatic_song_offi_ids", [])
        # self.update_song_offi_ids = data.get("update_song_offi_ids", [])
        # self.delete_song_offi_ids = data.get("delete_song_offi_ids", [])
        # self.update_at = data.get("update_at")
        self.songs = [SongData(**song) for song in data.get("songs", [])]
        logging.info("既存データロード完了: %d件", len(self.songs))

    def save_data(self) -> None:
        """
        楽曲データをJSONファイルに保存する。
        """
        data = {
            "songs": [song.to_dict() for song in self.songs],
            "new_song_offi_ids": self.new_song_offi_ids,
            "new_lunatic_song_offi_ids": self.new_lunatic_song_offi_ids,
            "update_song_offi_ids": self.update_song_offi_ids,
            "delete_song_offi_ids": self.delete_song_offi_ids,
            "update_at": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        decode_unicode_json_file(self.data_file)
        logging.info("データ保存完了")

    def _fetch_official_json(self) -> List[Dict[str, Any]]:
        """
        公式サイトから楽曲JSONを取得する。
        """
        try:
            resp = session.get(OFFICIAL_JSON_URL, timeout=10)
            resp.encoding = resp.apparent_encoding
            data = resp.json()
            # Perfect Shining!![LUN0]を除外
            data = [s for s in data if s.get("id") != "948700"]
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

    def _fetch_fumen_remaster(self) -> List[str]:
        """
        譜面保管所からReMASTER楽曲の保管所ID一覧を取得する。
        """
        remaster_fumen_ids = []
        html_ = requests.get(f"https://www.sdvx.in/ongeki/sort/remaster.htm")
        soup = BeautifulSoup(html_.content, "html.parser")
        for l in str(soup).split("\n"):
            remaster_match = re.search(r'<script src="/ongeki/.*?/.*?/([0-9]+)luna\.js">', l)
            if remaster_match:
                remaster_fumen_ids.append(remaster_match.group(1))
        return remaster_fumen_ids

    def _search_song_by_official_id(self, offi_id: str) -> Optional[SongData]:
        """
        楽曲リストから公式IDで楽曲を検索する。
        """
        for song in self.songs:
            if song.song_official_id == offi_id or song.song_official_id_lunatic == offi_id:
                return song
        return None

    def _create_fumen_ids_all(self) -> List[str]:
        """
        譜面保管所の全保管所IDを取得する。
        """
        fumen_ids_all = []
        urls = [
            f"https://www.sdvx.in/ongeki/sort/{g}.htm"
            for g in ["pops", "niconico", "toho", "variety", "chumai", "ongeki", "remaster", "lunatic"]
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
                        m = re.search(r'<script src="/ongeki/.*?/.*?/([0-9]+)sort\.js">', line)
                        if m:
                            fumen_ids_all.append(m.group(1))
                    except Exception:
                        pass
                    try:
                        m = re.search(r'<script src="/ongeki/.*?/.*?/([0-9]+)luna\.js">', line)
                        if m:
                            fumen_ids_all.append(m.group(1))
                    except Exception:
                        pass
            except Exception as e:
                logging.error("Error fetching URL %s: %s", url, e)
        return fumen_ids_all

    # ----------------------------------

    def update_new_songs(self) -> None:
        """
        公式データと既存データを比較し、新規楽曲を追加する。
        """
        messages = ["【新曲登録処理 オンゲキ】"]
        official_data = self._fetch_official_json()
        reiwa_data_list = self._fetch_reiwaf5_json()

        # 新曲候補の抽出
        new_normal_official = []
        new_lunatic_official = []
        for s in official_data:
            if self._search_song_by_official_id(s.get("id")) is None:
                if s.get("lunatic") == "1":
                    new_lunatic_official.append(s)
                else:
                    new_normal_official.append(s)

        messages.append(f"新曲候補数: {len(new_normal_official)}")
        messages.append(f"新曲候補数(LUNATIC): {len(new_lunatic_official)}")

        # 通常楽曲の追加
        for s in new_normal_official:
            # 公式から取得したデータを元に新規楽曲データを作成
            song = SongData.from_official_data(s)

            # reiwaf5のデータを参照して定数情報などを適用
            target_name = song.song_name
            if song.is_bonus and target_name:
                target_name = target_name[:-16]  # ボーナスの場合は末尾を除去
            matching_reiwa = None
            for reiwa in reiwa_data_list:
                if target_name in reiwa.get("title", ""):
                    matching_reiwa = reiwa
                    break
            if matching_reiwa is None:
                messages.append(f"[新曲登録] reiwaf5内にデータがありません。song_name: {song.song_name}")
                continue
            song.apply_reiwaf5_data(matching_reiwa)

            # ジャンル名の付与
            if song.song_name in self.genre_dict:
                song.song_subname = self.genre_dict[song.song_name]
                song.song_subname_nodata = False
            else:
                song.song_subname_nodata = True

            # LUNATICは一旦ないことにしておく
            song.has_lunatic = False
            song.only_lunatic = False

            # 譜面データは初期状態では未取得としてマーク
            song.song_bpm_nodata = True
            song.exp_notesdesigner_nodata = True
            song.mas_notesdesigner_nodata = True
            song.exp_notes_nodata = True
            song.mas_notes_nodata = True
            song.exp_bell_nodata = True
            song.mas_bell_nodata = True

            self.songs.append(song)
            self.new_song_offi_ids.append(s.get("id"))

        # ----------------------------------

        # LUNATIC楽曲の追加
        # 上の処理とまとめちゃだめ！
        # 公式データは通常とLUNで別なので、既存楽曲との照らし合わせが必要
        for s in new_lunatic_official:

            # 既に存在する楽曲の追加LUNATICならば...
            existing_song = next((song for song in self.songs if song.song_name == s.get("title")), None)
            if existing_song:
                # 検索
                matching_reiwa = None
                for reiwa in reiwa_data_list:
                    if existing_song.song_name and existing_song.song_name in reiwa.get("title", ""):
                        matching_reiwa = reiwa
                        break
                # 適応
                if matching_reiwa:
                    existing_song.apply_reiwaf5_data(matching_reiwa, is_lunatic=True, is_only_lunatic=False)
                    existing_song.has_lunatic = True
                    existing_song.only_lunatic = False
                    existing_song.song_official_id_lunatic = s.get("id")
                    existing_song.character_lunatic = s.get("character")
                    date_str = format_date(s.get("date"))
                    existing_song.song_release_lunatic = date_str
                    existing_song.song_release_lunatic_version = date_to_ongekiversion(date_str)

                    # 譜面データは初期状態では未取得としてマーク
                    existing_song.lun_notes_nodata = True
                    existing_song.lun_bell_nodata = True
                    existing_song.lun_notesdesigner_nodata = True
                    self.new_lunatic_song_offi_ids.append(s.get("id"))
                continue

            # 新規楽曲 = only_lunaticならば...
            song = SongData.from_official_data(s, is_only_lunatic=True)
            matching_reiwa = None
            for reiwa in reiwa_data_list:
                if song.song_name and song.song_name in reiwa.get("title", ""):
                    matching_reiwa = reiwa
                    break
            if matching_reiwa is None:
                messages.append(f"[新曲登録(LUNATIC)] reiwaf5内にデータがありません。song_name: {song.song_name}")
                continue
            song.apply_reiwaf5_data(matching_reiwa, is_lunatic=True, is_only_lunatic=True)
            song.has_lunatic = True
            song.only_lunatic = True

            # 譜面データは初期状態では未取得としてマーク
            song.song_bpm_nodata = True
            song.lun_notes_nodata = True
            song.lun_bell_nodata = True
            song.lun_notesdesigner_nodata = True

            self.songs.append(song)
            self.new_song_offi_ids.append(s.get("id"))

        messages.append("新曲登録処理完了。")
        LineNotification.add_message_by_list(messages)

    def update_existing_songs(self) -> None:
        """
        定数情報の更新・削除曲処理・ジャンル名の付与を行う。
        """
        messages = ["【更新処理】"]
        official_data = self._fetch_official_json()
        reiwa_data_list = self._fetch_reiwaf5_json()

        # 公式データに存在しない楽曲を削除
        current_official_ids = {s.get("id") for s in official_data}
        songs_to_remove = [song for song in self.songs if song.song_official_id not in current_official_ids]
        for song in songs_to_remove:
            messages.append(f"削除曲: {song.song_name}")
            self.songs.remove(song)
            self.delete_song_offi_ids.append(song.song_official_id)

        # 定数情報の更新
        for song in self.songs:
            # 検索
            matching_reiwa = None
            for reiwa in reiwa_data_list:
                if song.song_name and song.song_name in reiwa.get("title", ""):
                    matching_reiwa = reiwa
                    break
            if not matching_reiwa:
                continue
            # EXPRT / MASTERを持つ曲 = not only_lunatic
            if not song.only_lunatic:
                # EXPERT
                if (
                    song.exp_const_nodata
                    and not bool(matching_reiwa.get("expert", {}).get("is_unknown"))
                    and string_level_to_float(matching_reiwa.get("expert", {}).get("level", "0")) >= 10
                ):
                    messages.append(
                        f"更新: {song.song_name} EXPERT {song.exp_const} -> {matching_reiwa.get('expert', {}).get('const')}"
                    )
                    song.exp_const = matching_reiwa.get("expert", {}).get("const")
                    song.exp_const_nodata = False
                    self.update_song_offi_ids.append(song.song_official_id)

                # MASTER
                if song.mas_const_nodata and not bool(matching_reiwa.get("master", {}).get("is_unknown")):
                    messages.append(
                        f"更新: {song.song_name} MASTER {song.mas_const} -> {matching_reiwa.get('master', {}).get('const')}"
                    )
                    song.mas_const = matching_reiwa.get("master", {}).get("const")
                    song.mas_const_nodata = False
                    self.update_song_offi_ids.append(song.song_official_id)

            # LUNATICをもつ曲
            if song.has_lunatic:
                if song.lun_const_nodata and not bool(matching_reiwa.get("lunatic", {}).get("is_unknown")):
                    messages.append(
                        f"更新: {song.song_name} LUNATIC {song.lun_const} -> {matching_reiwa.get('lunatic', {}).get('const')}"
                    )
                    song.lun_const = matching_reiwa.get("lunatic", {}).get("const")
                    song.lun_const_nodata = False
                    self.update_song_offi_ids.append(song.song_official_id)

        # ジャンル名の付与
        for song in self.songs:
            if song.song_subname_nodata:
                if song.song_name in self.genre_dict:
                    song.song_subname = self.genre_dict[song.song_name]
                    song.song_subname_nodata = False
                    self.update_song_offi_ids.append(song.song_official_id)
                else:
                    song.song_subname_nodata = True

        messages.append("更新処理完了。")
        LineNotification.add_message_by_list(messages)

    def link_fumen_ids(self) -> None:
        """
        譜面保管所の全保管所IDを取得し、既存楽曲データと曲名で突合してリンクする。
        """
        messages = ["【リンク処理】"]

        # 全保管所IDを取得
        fumen_ids_all = self._create_fumen_ids_all()

        # 既にリンク済みの保管所IDを除外
        fumen_ids_known = [song.song_fumen_id for song in self.songs if song.song_fumen_id and len(song.song_fumen_id) > 1]

        # 新曲候補の保管所IDたち
        fumen_ids_new = list(set(fumen_ids_all) - set(fumen_ids_known))

        messages.append(f"譜面保管所 新曲候補数: {len(fumen_ids_new)}")
        # print(fumen_ids_new)
        messages.append("-----\nリンク処理")

        for fumen_id in fumen_ids_new:

            # 新曲候補IDから保管所の登録曲名を取得
            try:
                url = f"https://www.sdvx.in/ongeki/{fumen_id[:2]}/js/{fumen_id}sort.js"
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
                    messages.append(f"- 譜面ID: {fumen_id} の保管所からの曲名情報取得に失敗しました。")
                    continue
            except Exception as e:
                messages.append(f"- 譜面ID: {fumen_id} の取得中にエラー発生: {e}")
                continue

            # 既存楽曲データと突合してリンク
            for song in self.songs:
                if song.song_name == song_name_fumen:
                    if song.song_fumen_id is None:
                        song.song_fumen_id = fumen_id
                        messages.append(f"- リンク成功: 『{song.song_name}』 ID:{song.song_official_id}-{song.song_fumen_id}")
                        self.update_song_offi_ids.append(song.song_official_id)
                    else:
                        messages.append(
                            f"- 『{song.song_name}』はリンク済です。 ID:{song.song_official_id}-{song.song_fumen_id}"
                        )
                    break
            else:
                messages.append(f"- 『{song_name_fumen}』のリンクに失敗しました。ID: None - {fumen_id}")

        # ボーナストラックに未リンクがある場合、元楽曲のリンク先を持ってくる
        for song in self.songs:
            if song.is_bonus and song.song_fumen_id is None:
                for song_original in self.songs:
                    if song.song_name[:-16] in song_original.song_name:
                        if song_original.song_fumen_id:
                            song.song_fumen_id = song_original.song_fumen_id
                            messages.append(
                                f"- リンク成功(ボーナストラック): 『{song.song_name}』 ID:{song.song_official_id}-{song.song_fumen_id}"
                            )
                            self.update_song_offi_ids.append(song.song_official_id)
                            break
                        else:
                            messages.append(
                                f"- 『{song.song_name}』のリンク(ボーナストラック)に失敗しました。ID: {song.song_official_id} - None"
                            )
                            break
                else:
                    messages.append(
                        f"- 『{song.song_name}』のリンク(ボーナストラック)に失敗しました。ID: {song.song_official_id} - None"
                    )

        # 未リンクの曲一覧を出力
        messages.append("-----\n未リンク曲一覧")
        for song in self.songs:
            if song.song_fumen_id is None:
                messages.append(f"- {song.song_name}")

        messages.append("リンク処理完了。")
        LineNotification.add_message_by_list(messages)

    def update_fumen_data(self) -> List[str]:
        """
        譜面保管所から各楽曲の譜面情報をスクレイピングして更新する。
        新曲およびnodataがある楽曲について、ノーツ数、ベル数、NOTES DESIGNER、BPMを更新する。
        全曲について、ReMASTER判定も更新する。
        """


        messages: List[str] = ["【保管所データ更新】"]
        logging.info("譜面保管所データ更新処理開始")

        # 取得対象の楽曲インデックスを収集
        target_index = []
        for i, song in enumerate(self.songs):
            if song.song_fumen_id is None:
                continue

            is_nodata = ( (not song.only_lunatic) and (
                song.exp_notes_nodata
                or song.exp_bell_nodata
                or song.exp_notesdesigner_nodata
                or song.mas_notes_nodata
                or song.mas_bell_nodata
                or song.mas_notesdesigner_nodata
            )) or ( song.has_lunatic and (
                song.lun_notes_nodata
                or song.lun_bell_nodata
                or song.lun_notesdesigner_nodata
            ))  or song.song_bpm_nodata

            # 新曲の場合は必ず更新対象、それ以外はnodataがあるものを対象とする
            if song.song_official_id in self.new_song_offi_ids:
                is_newsong = True
            elif is_nodata:
                is_newsong = False
            else:
                continue
            target_index.append(i)

        logging.info("保管所取得対象数: %d", len(target_index))

        # for i in tqdm.tqdm(target_index):
        for i in target_index:
            song: SongData = self.songs[i]

            url = f"https://www.sdvx.in/ongeki/{song.song_fumen_id[:2]}/js/{song.song_fumen_id}sort.js"
            try:
                time.sleep(0.5)
                resp = session.get(url, timeout=10)
                if resp.ok:
                    self.update_song_offi_ids.append(song.song_official_id)
                    data_parts = html.unescape(resp.text).replace("\r\n", "").split(";")
                    # BPM
                    bpm_match = re.search(r"<td class=f\d>(.*?)</table>", data_parts[2])
                    if bpm_match:
                        bpm_str = bpm_match.group(1)
                        try:
                            new_bpm = int(bpm_str)
                            if song.song_bpm_nodata or song.song_bpm != new_bpm:
                                messages.append(f"『{song.song_name}』: BPM updated to {new_bpm}")
                            song.song_bpm = new_bpm
                            song.song_bpm_nodata = False
                        except Exception as e:
                            song.song_bpm_nodata = True
                    else:
                        song.song_bpm_nodata = True

                    if not song.only_lunatic:
                        # EXPERT / MASTER NOTES DESIGNER
                        nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[3])
                        song.exp_notesdesigner = nd_match.group(1) if nd_match else None
                        song.exp_notesdesigner_nodata = not bool(nd_match)

                        nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[4])
                        song.mas_notesdesigner = nd_match.group(1) if nd_match else None
                        song.mas_notesdesigner_nodata = not bool(nd_match)

                        # EXPERT NOTES
                        notes_match = re.search(r"<td class=exp1>(.*?)</table>", data_parts[11])
                        if notes_match:
                            notes_str = notes_match.group(1)
                            try:
                                new_exp_notes = int(notes_str)
                                if song.exp_notes_nodata or song.exp_notes != new_exp_notes:
                                    messages.append(f"『{song.song_name}』: EXP NOTES updated to {new_exp_notes}")
                                song.exp_notes = new_exp_notes
                                song.exp_notes_nodata = False
                            except Exception as e:
                                song.exp_notes_nodata = True
                        else:
                            song.exp_notes_nodata = True

                        # MASTER NOTES
                        notes_match = re.search(r"<td class=mst1>(.*?)</table>", data_parts[12])
                        if notes_match:
                            notes_str = notes_match.group(1)
                            try:
                                new_mas_notes = int(notes_str)
                                if song.mas_notes_nodata or song.mas_notes != new_mas_notes:
                                    messages.append(f"『{song.song_name}』: MASTER NOTES updated to {new_mas_notes}")
                                song.mas_notes = new_mas_notes
                                song.mas_notes_nodata = False
                            except Exception as e:
                                song.mas_notes_nodata = True
                        else:
                            song.mas_notes_nodata = True

                        # EXPERT BELL
                        bell_match = re.search(r"<td class=y1>(.*?)</table>", data_parts[15])
                        if bell_match:
                            bell_str = bell_match.group(1)
                            try:
                                new_exp_bell = int(bell_str)
                                if song.exp_bell_nodata or song.exp_bell != new_exp_bell:
                                    messages.append(f"『{song.song_name}』: EXP BELL updated to {new_exp_bell}")
                                song.exp_bell = new_exp_bell
                                song.exp_bell_nodata = False
                            except Exception as e:
                                song.exp_bell_nodata = True
                        else:
                            song.exp_bell_nodata = True

                        # MASTER BELL
                        bell_match = re.search(r"<td class=y1>(.*?)</table>", data_parts[16])
                        if bell_match:
                            bell_str = bell_match.group(1)
                            try:
                                new_mas_bell = int(bell_str)
                                if song.mas_bell_nodata or song.mas_bell != new_mas_bell:
                                    messages.append(f"『{song.song_name}』: MASTER BELL updated to {new_mas_bell}")
                                song.mas_bell = new_mas_bell
                                song.mas_bell_nodata = False
                            except Exception as e:
                                song.mas_bell_nodata = True
                        else:
                            song.mas_bell_nodata = True

                    # LUNATIC
                    if song.has_lunatic:
                        lun_url = f"https://www.sdvx.in/ongeki/luna/js/{song.song_fumen_id}luna.js"
                        resp_lun = session.get(lun_url, timeout=10)
                        if resp_lun.ok:
                            data_parts = html.unescape(resp_lun.text).replace("\r\n", "").split(";")
                            nd_match = re.search(r"<td class=ef>NOTES DESIGNER / (.*?)</table>", data_parts[3])
                            song.lun_notesdesigner = nd_match.group(1) if nd_match else None
                            song.lun_notesdesigner_nodata = not bool(nd_match)

                            # LUNATIC NOTES
                            notes_match = re.search(r"<td class=luna1>(.*?)</table>", data_parts[5])
                            if notes_match:
                                notes_str = notes_match.group(1)
                                try:
                                    new_lun_notes = int(notes_str)
                                    if song.lun_notes_nodata or song.lun_notes != new_lun_notes:
                                        messages.append(f"『{song.song_name}』: LUNATIC NOTES updated to {new_lun_notes}")
                                    song.lun_notes = new_lun_notes
                                    song.lun_notes_nodata = False
                                except Exception as e:
                                    song.lun_notes_nodata = True
                            else:
                                song.lun_notes_nodata = True

                            # LUNATIC BELL
                            bell_match = re.search(r"<td class=y1>(.*?)</table>", data_parts[6])
                            if bell_match:
                                bell_str = bell_match.group(1)
                                try:
                                    new_lun_bell = int(bell_str)
                                    if song.lun_bell_nodata or song.lun_bell != new_lun_bell:
                                        messages.append(f"『{song.song_name}』: LUNATIC BELL updated to {new_lun_bell}")
                                    song.lun_bell = new_lun_bell
                                    song.lun_bell_nodata = False
                                except Exception as e:
                                    song.lun_bell_nodata = True
                            else:
                                song.lun_bell_nodata = True
                else:
                    messages.append(f"[fumen] 取得失敗 {song.song_fumen_id}")
                    # 新曲の場合は、request failed時に各項目をnodataにする
                    if is_newsong:
                        song.song_bpm_nodata = True
                        if not song.only_lunatic:
                            song.exp_notesdesigner_nodata = True
                            song.mas_notesdesigner_nodata = True
                            song.exp_notes_nodata = True
                            song.mas_notes_nodata = True
                            song.exp_bell_nodata = True
                            song.mas_bell_nodata = True
                        if song.has_lunatic:
                            song.lun_notesdesigner_nodata = True
                            song.lun_notes_nodata = True
                            song.lun_bell_nodata = True
            except Exception as e:
                messages.append(f"[fumen] エラー: {song.song_name}{song.song_fumen_id} - {e}")

        # ReMasterかどうかのデータを追加
        remaster_fumen_ids = self._fetch_fumen_remaster()
        for song in self.songs:
            if song.has_lunatic:
                if song.song_fumen_id is not None:
                    song.is_remaster = song.song_fumen_id in remaster_fumen_ids
                    song.is_remaster_nodata = False
                else:
                    song.is_remaster_nodata = True

        messages.append("保管所データ更新完了。")
        LineNotification.add_message_by_list(messages)


def main() -> None:
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

    manager.save_data()
    LineNotification.send_notification()


if __name__ == "__main__":
    main()
