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
    song_release_version = models.CharField(max_length=40, null=True, blank=True)

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
    song_release_version = models.CharField(max_length=40, null=True, blank=True)
    song_release_lunatic = models.DateField(null=True, blank=True)
    song_release_lunatic_version = models.CharField(max_length=40, null=True, blank=True)

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

# ----------------------------------

class BaseSongDataManager(models.Manager):
    # サブクラスで上書きする
    songdata_model : models.Model = None
    json_file_path = None
    update_at_file_path = None # データベースの更新日時を記録するファイルのパス

    @classmethod
    def import_songdata_from_json(cls):
        """
        JSONから楽曲情報を読み込み、update_or_create で DB を更新する共通処理
        """
        try:
            with open(cls.json_file_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {cls.json_file_path}")
            return None
        except json.JSONDecodeError:
            print(f"JSONの読み込みに失敗しました: {cls.json_file_path}")
            return None

        print(f"[{cls.__name__}] データベースに送信します")
        for song in data["songs"]:
            song_official_id = song["song_official_id"]
            if (song_official_id in data["new_song_offi_ids"] or
                song_official_id in data["update_song_offi_ids"]):
                obj, created = cls.songdata_model.objects.update_or_create(
                    song_official_id=song_official_id,
                    defaults=song
                )
                action = "作成" if created else "更新"
                print(f"- {action}: {obj.song_name}")
            elif song_official_id in data.get("delete_song_offi_ids", []):
                print(f"- 削除: {song['song_name']}")
                n, _ = cls.songdata_model.objects.filter(song_official_id=song_official_id).delete()
                if n != 1:
                    print(f"-- 削除に失敗しました: {song['song_name']}")
        print(f"[{cls.__name__}] 送信完了")

        # 更新日時の記録
        with open(cls.update_at_file_path, "w") as f:
            f.write(data.get("update_at", ""))
        return

    @classmethod
    def get_update_time(cls):
        with open(cls.update_at_file_path, "r") as f:
            update_time = f.readline()
        return update_time

    @classmethod
    def search_song_by_query_list(cls, query_list, search_settings):
        """
        クエリリストと検索設定から楽曲データを検索する共通処理
        """

        # TODO あとで詳しくする

        qs = cls.songdata_model.objects.all()
        search_results = qs.none()

        # 曲名による検索
        if search_settings.get("is_use_name"):
            for query in query_list:
                search_results |= qs.filter(song_name__icontains=query)

        # 読み方による検索
        if search_settings.get("is_use_reading"):
            # query_list[0] をカタカナ＋大文字アルファベットに変換し、濁点除去
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
            search_results |= qs.filter(song_reading__icontains=query_reading)

        # アーティスト名による検索
        if search_settings.get("is_use_artists"):
            for query in query_list:
                search_results |= qs.filter(song_artist__icontains=query)


        # TODO 検索絞り込み、内部処理の追加

        return list(search_results)

    @classmethod
    def get_new_songs(cls, date_before_2_weekly):
        """
        指定日以降に発売された楽曲を返す共通処理
        """
        qs = cls.songdata_model.objects.all()
        return list(qs.filter(song_release__gt=date_before_2_weekly))


# CHUNITHM 用マネージャー
class SongDataCNManager(BaseSongDataManager):
    songdata_model = SongDataCN
    json_file_path = JSON_C_FILE_PATH
    update_at_file_path = UPDATE_AT_C_FILE_PATH

    @classmethod
    def update_rights_data(cls):
        """
        CHUNITHM の著作権情報を取得するメソッド
        """
        rights_data = requests.get("https://chunithm.sega.jp/storage/json/rightsInfo.json")
        rights_data.encoding = rights_data.apparent_encoding
        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"), "w") as f:
            f.write("\n".join(rights_data.json()))


# ONGEKI 用マネージャー
class SongDataONManager(BaseSongDataManager):
    songdata_model = SongDataON
    json_file_path = JSON_O_FILE_PATH
    update_at_file_path = UPDATE_AT_O_FILE_PATH

    @classmethod
    def update_rights_data(cls):
        """
        ONGEKI の著作権情報を取得するメソッド
        """
        ongeki_rights_url = "https://ongeki.sega.jp/assets/json/music/music.json"
        response = requests.get(ongeki_rights_url)
        response.encoding = response.apparent_encoding
        ongeki_rights_json = response.json()

        ongeki_rights = []
        for e in ongeki_rights_json:
            if e["copyright1"] != "-":
                ongeki_rights.append(e["copyright1"])

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"), "w") as f:
            f.write("\n".join(list(set(ongeki_rights))))
