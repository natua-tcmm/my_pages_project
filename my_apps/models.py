from django.db import models
from django.conf import settings
import requests, os, json, datetime, jaconv, unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "my_apps/my_data")
JSON_C_FILE_PATH = os.path.join(DATA_DIR, "songdata_c_dict.json")
JSON_O_FILE_PATH = os.path.join(DATA_DIR, "songdata_o_dict.json")
UPDATE_AT_C_FILE_PATH = os.path.join(DATA_DIR, "const_update_at_c.txt")
UPDATE_AT_O_FILE_PATH = os.path.join(DATA_DIR, "const_update_at_o.txt")

# DB構造を変化させたくなったら
# ・モデルを変更する (models.py の中の)
# ・これらの変更のためのマイグレーションを作成するために python manage.py makemigrations を実行
# ・データベースにこれらの変更を適用するために python manage.py migrate を実行
# https://docs.djangoproject.com/ja/4.2/intro/tutorial02/

# ----------------------------------


# CHUNITHM 曲データ
class SongDataCN(models.Model):
    # 基本情報
    song_official_id = models.CharField(max_length=10, unique=True)
    song_name = models.CharField(max_length=200)
    song_reading = models.CharField(max_length=200)
    song_artist = models.CharField(max_length=200)
    song_genre = models.CharField(max_length=20)
    song_bpm = models.IntegerField(null=True, blank=True)
    song_bpm_nodata = models.BooleanField(default=True)

    # 発売日情報（DateField として保持。データクラスでは文字列になっていますが、DB には日付として保存）
    song_release = models.DateField(null=True, blank=True)
    song_release_version = models.CharField(max_length=20, null=True, blank=True)

    # イメージ・譜面ID（譜面IDは「文字列5ケタ」の想定なので max_length を 5 に変更）
    song_image_url = models.CharField(max_length=100)
    song_fumen_id = models.CharField(max_length=5, null=True, unique=True)

    # フラグ
    is_worldsend = models.BooleanField(default=False)
    has_ultima = models.BooleanField(default=False)
    only_ultima = models.BooleanField(default=False)

    # EXPERT
    exp_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    exp_const_nodata = models.BooleanField(default=True)
    exp_notes = models.IntegerField(null=True, blank=True)
    exp_notes_nodata = models.BooleanField(default=True)
    exp_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    exp_notesdesigner_nodata = models.BooleanField(default=True)

    # MASTER
    mas_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    mas_const_nodata = models.BooleanField(default=True)
    mas_notes = models.IntegerField(null=True, blank=True)
    mas_notes_nodata = models.BooleanField(default=True)
    mas_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    mas_notesdesigner_nodata = models.BooleanField(default=True)

    # ULTIMA
    ult_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    ult_const_nodata = models.BooleanField(default=True)
    ult_notes = models.IntegerField(null=True, blank=True)
    ult_notes_nodata = models.BooleanField(default=True)
    ult_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    ult_notesdesigner_nodata = models.BooleanField(default=True)

    # その他
    we_star = models.CharField(max_length=10, null=True, blank=True)
    we_kanji = models.CharField(max_length=10, null=True, blank=True)


# CHUNITHM 曲データのマネージャ
class SongDataCNManager(models.Manager):

    # jsonからインポートするやつ
    @classmethod
    def import_songdata_from_json(cls):
        """
        楽曲情報をjsonからインポートするメソッド
        """
        try:
            with open(JSON_C_FILE_PATH, "r") as f:
                songdata_c_dict = json.load(f)
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {JSON_C_FILE_PATH}")
            return None
        except json.JSONDecodeError:
            print(f"JSONの読み込みに失敗しました: {JSON_C_FILE_PATH}")
            return None

        print("[SongDataCNManager] データベースに送信します")
        for a_song_data in songdata_c_dict["songs"]:
            song_official_id = a_song_data["song_official_id"]
            if (
                song_official_id in songdata_c_dict["new_song_offi_ids"]
                or song_official_id in songdata_c_dict["update_song_offi_ids"]
            ):
                o, created = SongDataCN.objects.update_or_create(song_official_id=song_official_id, defaults=a_song_data)
                action = "作成" if created else "更新"
                print(f"- {action}: {o.song_name}")
            elif song_official_id in songdata_c_dict["delete_song_offi_ids"]:
                print(f"- 削除: {a_song_data['song_name']}")
                n, _ = SongDataCN.objects.filter(song_official_id=song_official_id).delete()
                if n != 1:
                    print(f"-- 削除に失敗しました: {a_song_data['song_name']}")

        print("[SongDataCNManager] 送信完了")

        # 更新日時を記録
        with open(UPDATE_AT_C_FILE_PATH, "w") as f:
            f.write(songdata_c_dict.get("update_at"))

        return

    @classmethod
    def update_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        rights_data = requests.get("https://chunithm.sega.jp/storage/json/rightsInfo.json")
        rights_data.encoding = rights_data.apparent_encoding

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"), "w") as f:
            f.write("\n".join(rights_data.json()))

    @classmethod
    def search_song_by_query_list(cls, query_list, search_settings):
        """
        query_listから曲データを検索するメソッド
        """
        search_results = SongDataCN.objects.none()

        # TODO このへん後で整備する

        # 曲名
        if search_settings["is_use_name"]:
            for query in query_list:
                search_results = search_results | SongDataCN.objects.filter(song_name__icontains=query)

        # 読み方
        if search_settings["is_use_reading"]:
            # query_list[0]をカタカナとアルファベット大文字に変換して濁点を取る 他の文字はなし
            query_reading = "".join(
                [
                    c
                    for c in jaconv.hira2kata(unicodedata.normalize("NFKD", query_list[0]))
                    .upper()
                    .translate(str.maketrans("ァィゥェォャュョッヮヵヶ", "アイウエオヤユヨツワカケ"))
                    if ("\u30a1" <= c <= "\u30fa" or "A" <= c <= "Z")
                ]
            )
            print(query_reading)
            search_results = search_results | SongDataCN.objects.filter(song_reading__icontains=query_reading)

        # アーティスト名
        if search_settings["is_use_artists"]:
            for query in query_list:
                search_results = search_results | SongDataCN.objects.filter(song_artist__icontains=query)

        return list(search_results)

    @classmethod
    def get_new_songs(cls, date_before_2_weekly):
        """
        新曲を返すメソッド
        """
        song_new = SongDataCN.objects.filter(song_release__gt=date_before_2_weekly)
        search_results_song_list = list(song_new)
        return search_results_song_list


# ----------------------------------


# オンゲキ 曲データ
class SongDataON(models.Model):
    # 基本情報
    song_official_id = models.CharField(max_length=10)
    song_official_id_lunatic = models.CharField(max_length=10, null=True, blank=True)
    song_name = models.CharField(max_length=200)
    song_reading = models.CharField(max_length=200)
    song_subname = models.CharField(max_length=200, null=True, blank=True)
    song_subname_nodata = models.BooleanField(default=True)
    song_artist = models.CharField(max_length=500)
    song_genre = models.CharField(max_length=20)
    song_bpm = models.IntegerField(null=True, blank=True)
    song_bpm_nodata = models.BooleanField(default=True)

    # リリース情報
    song_release = models.DateField(null=True, blank=True)
    song_release_version = models.CharField(max_length=20, null=True, blank=True)
    song_release_lunatic = models.DateField(null=True, blank=True)
    song_release_lunatic_version = models.CharField(max_length=20, null=True, blank=True)

    # イメージ・譜面情報
    song_image_url = models.CharField(max_length=100)
    song_fumen_id = models.CharField(max_length=5, null=True, blank=True)  # 文字列5ケタを想定

    # キャラクター情報
    character = models.CharField(max_length=100)
    character_lunatic = models.CharField(max_length=100, null=True, blank=True)

    # フラグ
    is_bonus = models.BooleanField(default=False)
    has_lunatic = models.BooleanField(default=False)
    only_lunatic = models.BooleanField(default=False)
    is_remaster = models.BooleanField(null=True, blank=True)
    is_remaster_nodata = models.BooleanField(default=True)

    # EX難易度
    exp_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    exp_const_nodata = models.BooleanField(default=True)
    exp_notes = models.IntegerField(null=True, blank=True)
    exp_notes_nodata = models.BooleanField(default=True)
    exp_bell = models.IntegerField(null=True, blank=True)
    exp_bell_nodata = models.BooleanField(default=True)
    exp_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    exp_notesdesigner_nodata = models.BooleanField(default=True)

    # MAS難易度
    mas_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    mas_const_nodata = models.BooleanField(default=True)
    mas_notes = models.IntegerField(null=True, blank=True)
    mas_notes_nodata = models.BooleanField(default=True)
    mas_bell = models.IntegerField(null=True, blank=True)
    mas_bell_nodata = models.BooleanField(default=True)
    mas_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    mas_notesdesigner_nodata = models.BooleanField(default=True)

    # LUNATIC難易度
    lun_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    lun_const_nodata = models.BooleanField(default=True)
    lun_notes = models.IntegerField(null=True, blank=True)
    lun_notes_nodata = models.BooleanField(default=True)
    lun_bell = models.IntegerField(null=True, blank=True)
    lun_bell_nodata = models.BooleanField(default=True)
    lun_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    lun_notesdesigner_nodata = models.BooleanField(default=True)


# オンゲキ 曲データのマネージャ
class SongDataONManager(models.Manager):

    # jsonからインポートするやつ
    @classmethod
    def import_songdata_from_json(cls):
        """
        楽曲情報をjsonからインポートするメソッド
        """
        try:
            with open(JSON_O_FILE_PATH, "r") as f:
                songdata_o_dict = json.load(f)
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {JSON_O_FILE_PATH}")
            return None
        except json.JSONDecodeError:
            print(f"JSONの読み込みに失敗しました: {JSON_O_FILE_PATH}")
            return None

        print("[SongDataONManager] データベースに送信します")
        for a_song_data in songdata_o_dict["songs"]:
            song_official_id = a_song_data["song_official_id"]
            if (
                song_official_id in songdata_o_dict["new_song_offi_ids"]
                or song_official_id in songdata_o_dict["update_song_offi_ids"]
            ):
                o, created = SongDataON.objects.update_or_create(song_official_id=song_official_id, defaults=a_song_data)
                action = "作成" if created else "更新"
                print(f"- {action}: {o.song_name}")
            elif song_official_id in songdata_o_dict["delete_song_offi_ids"]:
                print(f"- 削除: {a_song_data['song_name']}")
                n, _ = SongDataON.objects.filter(song_official_id=song_official_id).delete()
                if n != 1:
                    print(f"-- 削除に失敗しました: {a_song_data['song_name']}")

        print("[SongDataONManager] 送信完了")

        # 更新日時を記録
        with open(UPDATE_AT_O_FILE_PATH, "w") as f:
            f.write(songdata_o_dict.get("update_at"))

        return

    @classmethod
    def update_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        ongeki_rights_url = "https://ongeki.sega.jp/assets/json/music/music.json"

        # リクエストを送信
        response = requests.get(ongeki_rights_url)
        response.encoding = response.apparent_encoding
        ongeki_rights_json = response.json()

        ongeki_rights = []

        for e in ongeki_rights_json:
            if e["copyright1"] != "-":
                ongeki_rights.append(e["copyright1"])

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"), "w") as f:
            f.write("\n".join(list(set(ongeki_rights))))

    @classmethod
    def search_song_by_query_list(cls, query_list, search_settings):
        """
        query_listから曲データを検索するメソッド
        """
        search_results = SongDataON.objects.none()

        # TODO このへん後で整備する

        # 曲名
        if search_settings["is_use_name"]:
            for query in query_list:
                search_results = search_results | SongDataON.objects.filter(song_name__icontains=query)

        # 読み方
        if search_settings["is_use_reading"]:
            # query_list[0]をカタカナとアルファベット大文字に変換して濁点を取る 他の文字はなし
            query_reading = "".join(
                [
                    c
                    for c in jaconv.hira2kata(unicodedata.normalize("NFKD", query_list[0]))
                    .upper()
                    .translate(str.maketrans("ァィゥェォャュョッヮヵヶ", "アイウエオヤユヨツワカケ"))
                    if ("\u30a1" <= c <= "\u30fa" or "A" <= c <= "Z")
                ]
            )
            print(query_reading)
            search_results = search_results | SongDataON.objects.filter(song_reading__icontains=query_reading)

        # アーティスト名
        if search_settings["is_use_artists"]:
            for query in query_list:
                search_results = search_results | SongDataON.objects.filter(song_artist__icontains=query)

        return list(search_results)

    @classmethod
    def get_new_songs(cls, date_before_2_weekly):
        """
        新曲を返すメソッド
        """
        song_new = SongDataON.objects.filter(song_release__gt=date_before_2_weekly)
        search_results_song_list = list(song_new)
        return search_results_song_list
