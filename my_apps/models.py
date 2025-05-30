from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import requests, os, json, datetime, jaconv, unicodedata, re
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
    song_release_version = models.CharField(max_length=100, null=True, blank=True)

    # イメージ・譜面ID（譜面IDは「文字列5ケタ」の想定なので max_length を 5 に変更）
    song_image_url = models.CharField(max_length=100)
    song_fumen_id = models.CharField(max_length=5, null=True, unique=True)

    # フラグ
    is_worldsend = models.BooleanField(default=False)
    has_ultima = models.BooleanField(default=False)
    only_ultima = models.BooleanField(default=False)

    # フォルダ位置情報
    song_namefolder_name = models.CharField(max_length=20, null=True, blank=True)
    song_namefolder_index = models.IntegerField(null=True, blank=True)

    # BASIC
    bas_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bas_const_nodata = models.BooleanField(default=True)

    # ADVANCED
    adv_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    adv_const_nodata = models.BooleanField(default=True)

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
    song_release_version = models.CharField(max_length=100, null=True, blank=True)
    song_release_lunatic = models.DateField(null=True, blank=True)
    song_release_lunatic_version = models.CharField(max_length=100, null=True, blank=True)

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

    # # フォルダ位置情報
    # song_namefolder_name = models.CharField(max_length=20, null=True, blank=True)
    # song_namefolder_index = models.IntegerField(null=True, blank=True)

    # BASIC
    bas_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bas_const_nodata = models.BooleanField(default=True)

    # ADVANCED
    adv_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    adv_const_nodata = models.BooleanField(default=True)

    # EXPERT
    exp_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    exp_const_nodata = models.BooleanField(default=True)
    exp_notes = models.IntegerField(null=True, blank=True)
    exp_notes_nodata = models.BooleanField(default=True)
    exp_bell = models.IntegerField(null=True, blank=True)
    exp_bell_nodata = models.BooleanField(default=True)
    exp_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    exp_notesdesigner_nodata = models.BooleanField(default=True)

    # MASTER
    mas_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    mas_const_nodata = models.BooleanField(default=True)
    mas_notes = models.IntegerField(null=True, blank=True)
    mas_notes_nodata = models.BooleanField(default=True)
    mas_bell = models.IntegerField(null=True, blank=True)
    mas_bell_nodata = models.BooleanField(default=True)
    mas_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    mas_notesdesigner_nodata = models.BooleanField(default=True)

    # LUNATIC
    lun_const = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    lun_const_nodata = models.BooleanField(default=True)
    lun_notes = models.IntegerField(null=True, blank=True)
    lun_notes_nodata = models.BooleanField(default=True)
    lun_bell = models.IntegerField(null=True, blank=True)
    lun_bell_nodata = models.BooleanField(default=True)
    lun_notesdesigner = models.CharField(max_length=100, null=True, blank=True)
    lun_notesdesigner_nodata = models.BooleanField(default=True)


# ----------------------------------


# データベースのマネージャー
class BaseSongDataManager(models.Manager):
    # サブクラスで上書きする
    songdata_model: models.Model = None
    json_file_path = None
    update_at_file_path = None  # データベースの更新日時を記録するファイルのパス

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
            if song_official_id in data["new_song_offi_ids"] or song_official_id in data["update_song_offi_ids"]:
                obj, created = cls.songdata_model.objects.update_or_create(song_official_id=song_official_id, defaults=song)
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
    def reflesh_all_db(cls):
        """
        JSONから楽曲情報を読み込み、DBを全て更新する共通処理(通常は使用しない)
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

        print(f"[{cls.__name__}] データベースをすべて削除し、リフレッシュします")
        cls.songdata_model.objects.all().delete()

        # data["songs"]をすべて登録
        for song in data["songs"]:
            obj, created = cls.songdata_model.objects.update_or_create(song_official_id=song["song_official_id"], defaults=song)
            action = "作成" if created else "更新"
            print(f"- {action}: {obj.song_name}")

        print(f"[{cls.__name__}] 送信完了")

        # 更新日時の記録
        with open(cls.update_at_file_path, "w") as f:
            f.write(data.get("update_at", ""))
        return

    @classmethod
    def get_update_time(cls):
        """
        更新日時を取得する共通処理
        """
        with open(cls.update_at_file_path, "r") as f:
            update_time = f.readline()
        return update_time

    @classmethod
    def _create_query_list(cls, query):
        """
        クエリから検索クエリリストを生成する共通処理
        ・ひらがな・カタカナ変換
        ・末尾のアルファベットを削除
        """
        query_list = [query]

        # 末尾にアルファベットがあれば消す(日本語入力中を想定)
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

    @classmethod
    def search_song_by_query(cls, query_original: str, search_settings: dict):
        """
        検索クエリと検索設定から楽曲データを検索する共通処理
        """

        # 検索クエリリストの生成
        query_list = cls._create_query_list(query_original)

        qs = cls.songdata_model.objects.all()
        search_results = qs.none()

        # queryによる検索
        for query in query_list:

            # 曲名による検索
            if search_settings.get("is_use_name"):

                # 曲名による検索
                search_results |= qs.filter(song_name__icontains=query)

                # ジャンル名による検索(オンゲキのみ)
                if cls.songdata_model == SongDataON:
                    search_results |= qs.filter(song_subname__icontains=query)

                # 読み方による検索
                if query == query_original:
                    # query_original をカタカナ＋大文字アルファベットに変換し、濁点除去
                    query_reading = "".join(
                        [
                            c
                            for c in jaconv.hira2kata(unicodedata.normalize("NFKD", query_original))
                            .upper()
                            .translate(str.maketrans("ァィゥェォャュョッヮヵヶ", "アイウエオヤユヨツワカケ"))
                            if ("\u30a1" <= c <= "\u30fa" or "A" <= c <= "Z")
                        ]
                    )
                    # 検索
                    if len(query_reading) > 0:
                        # print(query_reading)
                        search_results |= qs.filter(song_reading__icontains=query_reading)

            # アーティスト名による検索
            if search_settings.get("is_use_artists"):
                search_results |= qs.filter(song_artist__icontains=query)

            # ノーツデザイナー名による検索
            if search_settings.get("is_use_nd"):
                search_results |= qs.filter(exp_notesdesigner__icontains=query)
                search_results |= qs.filter(mas_notesdesigner__icontains=query)
                if cls.songdata_model == SongDataCN:
                    search_results |= qs.filter(ult_notesdesigner__icontains=query)
                elif cls.songdata_model == SongDataON:
                    search_results |= qs.filter(lun_notesdesigner__icontains=query)

        # 絞り込みオプション
        # BPM
        if search_settings.get("is_use_bpm"):
            search_results = search_results.filter(song_bpm__range=(search_settings["bpm_from"], search_settings["bpm_to"]))
        # ノーツ数
        if search_settings.get("is_use_notes"):
            search_results = search_results.filter(
                Q(exp_notes__range=(search_settings["notes_from"], search_settings["notes_to"]))
                | Q(mas_notes__range=(search_settings["notes_from"], search_settings["notes_to"]))
                | (
                    Q(ult_notes__range=(search_settings["notes_from"], search_settings["notes_to"]))
                    if cls.songdata_model == SongDataCN
                    else Q()
                )
                | (
                    Q(lun_notes__range=(search_settings["notes_from"], search_settings["notes_to"]))
                    if cls.songdata_model == SongDataON
                    else Q()
                )
            )

        # ボーナストラック
        if cls.songdata_model == SongDataON and (not search_settings.get("is_disp_bonus")):
            search_results = search_results.filter(is_bonus=False)

        # LUNATIC関連
        if cls.songdata_model == SongDataON and search_settings.get("is_use_lunatic_option"):
            match search_settings.get("lunatic_option"):
                case "all":
                    pass
                case "has":
                    search_results = search_results.filter(has_lunatic=True)
                case "not-has":
                    search_results = search_results.filter(has_lunatic=False)
                case "only":
                    search_results = search_results.filter(only_lunatic=True)
                case "not-only":
                    search_results = search_results.filter(only_lunatic=False)
                case "has-not-only":
                    search_results = search_results.filter(has_lunatic=True, only_lunatic=False)
                case "remaster":
                    search_results = search_results.filter(is_remaster=True)
                case "not-remaster":
                    search_results = search_results.filter(is_remaster__in=[False, None])
                case _:
                    raise ValueError("Lunatic option is invalid")

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


# ----------------------------------

# アクセス情報収集のためのモデル
# ページ閲覧情報
class PageViewManager(models.Manager):
    @classmethod
    def add_log(cls, request):
        if request.method == "GET":
            ip = cls.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            return PageView.objects.create(
                path=request.path,
                method=request.method,
                ip=ip,
                user_agent=user_agent,
                timestamp=timezone.now(),
            )

    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return request.META.get('REMOTE_ADDR')

class PageView(models.Model):
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()

# ツール利用情報
class ToolUsageManager(models.Manager):
    @classmethod
    def add_usage(cls, request, tool_name, info):
        ip = cls.get_client_ip(request)
        return ToolUsage.objects.create(
            tool_name=tool_name,
            info=info,
            path=request.path,
            ip=ip,
            timestamp=timezone.now(),
        )

    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return request.META.get('REMOTE_ADDR')

class ToolUsage(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField()
    path = models.CharField(max_length=255)
    tool_name = models.CharField(max_length=255)
    info = models.CharField(max_length=255)
