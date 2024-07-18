from django.db import models
from django.conf import settings
import requests,os,json,datetime,jaconv,unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_C_FILE_PATH = os.path.join(BASE_DIR,"my_apps/my_data/songdata_c_dict.json")


# Create your models here.

# DB構造を変化させたくなったら
# ・モデルを変更する (models.py の中の)
# ・これらの変更のためのマイグレーションを作成するために python manage.py makemigrations を実行
# ・データベースにこれらの変更を適用するために python manage.py migrate を実行
# https://docs.djangoproject.com/ja/4.2/intro/tutorial02/

# ----------------------------------

# CHUNITHM 曲データ

class SongDataCN(models.Model):

    song_official_id = models.CharField(max_length=10,unique=True)
    song_name = models.CharField(max_length=200)
    song_reading = models.CharField(max_length=200)
    song_artist = models.CharField(max_length=500)
    song_genre = models.CharField(max_length=20)
    song_bpm = models.IntegerField(null=True)
    song_bpm_nodata = models.BooleanField()
    song_release = models.DateField()
    song_image_url = models.CharField(max_length=100)
    song_fumen_id = models.CharField(max_length=10,null=True,unique=True)

    is_worldsend = models.BooleanField()
    has_ultima = models.BooleanField()
    only_ultima = models.BooleanField()

    exp_const = models.DecimalField(max_digits=4,decimal_places=1,null=True)
    exp_const_nodata = models.BooleanField()
    exp_notes = models.IntegerField(null=True)
    exp_notes_nodata = models.BooleanField()
    exp_notesdesigner = models.CharField(max_length=100,null=True)
    exp_notesdesigner_nodata = models.BooleanField()

    mas_const = models.DecimalField(max_digits=4,decimal_places=1,null=True)
    mas_const_nodata = models.BooleanField()
    mas_notes = models.IntegerField(null=True)
    mas_notes_nodata = models.BooleanField()
    mas_notesdesigner = models.CharField(max_length=100,null=True)
    mas_notesdesigner_nodata = models.BooleanField()

    ult_const = models.DecimalField(max_digits=4,decimal_places=1,null=True)
    ult_const_nodata = models.BooleanField(null=True)
    ult_notes = models.IntegerField(null=True)
    ult_notes_nodata = models.BooleanField(null=True)
    ult_notesdesigner = models.CharField(max_length=100,null=True)
    ult_notesdesigner_nodata = models.BooleanField(null=True)

    we_star = models.CharField(max_length=10,null=True)
    we_kanji = models.CharField(max_length=10,null=True)


class SongDataCNManager(models.Manager):

    # jsonからインポートするやつ
    @classmethod
    def import_songdata_from_json(cls):
        """
        楽曲情報をjsonからインポートするメソッド
        """

        # データ一覧を読み込む
        with open(JSON_C_FILE_PATH, "r") as f:
            songdata_c_dict = json.load(f)

        # DBを更新する
        print("[SongDataCNManager]データベースに送信します")
        for a_song_data in songdata_c_dict["songs"]:
            # 更新されたやつだけ
            if  (a_song_data["song_official_id"] in songdata_c_dict["new_song_offi_ids"]) or \
                (a_song_data["song_official_id"] in songdata_c_dict["update_song_offi_ids"]):

                o,c =SongDataCN.objects.update_or_create(song_official_id=a_song_data["song_official_id"],defaults=a_song_data)
                if c:
                    print(f"- 作成したよん→ {o.song_name}")
                else:
                    print(f"- 更新したよん→ {o.song_name}")

        print("[SongDataCNManager]送信が完了しました")
        return songdata_c_dict["update_at"]

    @classmethod
    def update_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        rights_data= requests.get("https://chunithm.sega.jp/storage/json/rightsInfo.json")
        rights_data.encoding = rights_data.apparent_encoding

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"),"w") as f:
            f.write("\n".join(rights_data.json()))

    @classmethod
    def search_song_by_query_list(cls,query_list,search_settings):
        """
        query_listから曲データを検索するメソッド
        """
        search_results = SongDataCN.objects.none()

        # 曲名
        if search_settings["is_use_name"]:
            for query in query_list:
                search_results = search_results|SongDataCN.objects.filter(song_name__icontains=query)

        # 読み方
        if search_settings["is_use_reading"]:
            # query_list[0]をカタカナとアルファベット大文字に変換して濁点を取る 他の文字はなし
            query_reading = "".join([ c for c in jaconv.hira2kata(unicodedata.normalize("NFKD",query_list[0])).upper().translate(str.maketrans("ァィゥェォャュョッヮヵヶ","アイウエオヤユヨツワカケ")) if ( "\u30a1"<=c<="\u30fa" or "A"<=c<="Z" ) ])
            print(query_reading)
            search_results = search_results|SongDataCN.objects.filter(song_reading__icontains=query_reading)

        # アーティスト名
        if search_settings["is_use_artists"]:
            for query in query_list:
                search_results = search_results|SongDataCN.objects.filter(song_artist__icontains=query)

        return list(search_results)

    @classmethod
    def get_new_songs(cls,date_before_2_weekly):
        """
        新曲を返すメソッド
        """
        song_new = SongDataCN.objects.filter(song_release__gt=date_before_2_weekly)
        search_results_song_list = list(song_new)
        return search_results_song_list


# ----------------------------------

# CHUNITHM 曲データ(旧)

class SongDataC(models.Model):

    # 曲名など
    song_name = models.CharField(max_length=100)
    song_name_reading = models.CharField(max_length=100)
    song_auther = models.CharField(max_length=100)

    # カテゴリ
    song_catname = models.CharField(max_length=20)

    song_bpm = models.IntegerField()
    song_release = models.DateField()

    # レベル
    expert_const = models.DecimalField(max_digits=4,decimal_places=1)
    expert_notes = models.IntegerField()

    master_const = models.DecimalField(max_digits=4,decimal_places=1)
    master_notes = models.IntegerField()

    ultima_const = models.DecimalField(max_digits=4,decimal_places=1)
    ultima_notes = models.IntegerField()

    # 譜面保管所ID
    fumen_id = models.IntegerField()

class SongDataCManager(models.Manager):

    @classmethod
    def update_song_data(cls):
        """
        定数情報を更新するメソッド
        """
        # 情報を取得する
        new_song_data = cls.get_song_data()

        # 更新する
        result = ""

        print("CHUNITHM 更新するよん")
        result += "CHUNITHM 更新するよん\n"

        for a_song_data in new_song_data:
            o,c =SongDataC.objects.update_or_create(song_name=a_song_data["song_name"],defaults=a_song_data)
            if c:
                print(f"- 作成したよん→ {o.song_name}")
                result += f"- 作成したよん→ {o.song_name}\n"

        print("CHUNITHM 更新終わったよん")
        result += "CHUNITHM 更新終わったよん\n"

        return result

    @classmethod
    def get_song_data(cls):
        """
        定数情報を取得するメソッド
        """
        import requests,re
        from bs4 import BeautifulSoup

        chuni_const_url = "https://reiwa.f5.si/chunirec_all.json"
        chuni_offi_url = "https://chunithm.sega.jp/storage/json/music.json"

        # 定数情報を取得する
        response= requests.get(chuni_const_url)
        response.encoding = response.apparent_encoding
        rec_json = response.json()

        # 読み情報を取得する
        response= requests.get(chuni_offi_url)
        response.encoding = response.apparent_encoding
        offi_json = response.json()

        # 譜面保管所IDを取得する
        ids_c = {}
        target = ["pops","niconico","toho","variety","irodorimidori","gekimai","original","ultima"]

        for t in target:
            TARGET_URL = f"https://www.sdvx.in/chunithm/sort/{t}.htm"
            html = requests.get(TARGET_URL)
            soup = BeautifulSoup(html.content, "html.parser")
            songs = soup.select("body > center > table > tr > td > td > td > tr > td > td> table > tr > td")
            songs_str = str(songs)

            pattern1 = re.compile(r'script src=\"/chunithm/.*/js/.*sort\.js\"></script><script>SORT.*\(\);</script><!--.*-->')
            result1 = pattern1.findall(songs_str)
            for r in result1:
                ids_c[r[84:-3]]=int(r[28:33])

            pattern2 = re.compile(r'script src=\"/chunithm/ult/js/.*ult\.js\"></script><script>SORT.*\(\);</script><!--.*-->')
            result2 = pattern2.findall(songs_str)
            for r in result2:
                ids_c[r[85:-3]]=int(r[29:34])

        # 整形する
        new_songdata = []
        for j in rec_json:

            # WE除外
            if j["meta"]["genre"]=="WORLD'S END":
                continue

            d = {}

            # 情報入力(だいたい)
            d["song_name"]=j["meta"]["title"]
            d["song_name_reading"]=""
            d["song_auther"]=j["meta"]["artist"]
            d["song_catname"]=j["meta"]["genre"]

            d["song_bpm"]=j["meta"]["bpm"]
            # d["song_release"]=datetime.date(*[ int(e) for e in j["meta"]["release"].split("-")])
            d["song_release"]=j["meta"]["release"]


            d["expert_const"]=j["data"]["EXP"]["const"]
            if j["data"]["EXP"]["is_const_unknown"]:
                d["expert_const"]=0
            d["expert_notes"]=j["data"]["EXP"]["maxcombo"]

            d["master_const"]=j["data"]["MAS"]["const"]
            if j["data"]["MAS"]["is_const_unknown"]:
                d["master_const"]=0
            d["master_notes"]=j["data"]["MAS"]["maxcombo"]

            try:
                d["ultima_const"]=j["data"]["ULT"]["const"]
                if j["data"]["ULT"]["is_const_unknown"]:
                    d["ultima_const"]=0
                d["ultima_notes"]=j["data"]["ULT"]["maxcombo"]
            except:
                d["ultima_const"]=0
                d["ultima_notes"]=0

            # reading
            for e in offi_json:
                if e["title"]==d["song_name"]:
                    d["song_name_reading"]=e["reading"]
                    break

            # 譜面id
            try:
                d["fumen_id"] = ids_c[d["song_name"]]
            except:
                print(f"-- リンク失敗 曲名:{d['song_name']}")
                d["fumen_id"] = 0

            # # 定数未確定情報
            # tmp = 0
            # for k in ["EXP","MAS","ULT"]:
            #     try:
            #         tmp += j["data"][k]["is_const_unknown"]
            #     except:
            #         pass
            # if tmp>0:
            #     d["is_const_unknown"]=True
            # else:
            #     d["is_const_unknown"]=False


            # jsonに足す
            new_songdata.append(d)

        print("取得できたよん")
        return new_songdata

    @classmethod
    def update_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        rights_data= requests.get("https://chunithm.sega.jp/storage/json/rightsInfo.json")
        rights_data.encoding = rights_data.apparent_encoding

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_chunithm.txt"),"w") as f:
            f.write("\n".join(rights_data.json()))

# ----------------------------------

# オンゲキ 曲データ
class SongDataO(models.Model):

    # 曲名など
    song_name = models.CharField(max_length=100)
    song_auther = models.CharField(max_length=100)

    # カテゴリ
    song_catname = models.CharField(max_length=20)
    song_release = models.DateField()

    # レベル
    expert_const = models.DecimalField(max_digits=4,decimal_places=1)
    expert_notes = models.IntegerField()

    master_const = models.DecimalField(max_digits=4,decimal_places=1)
    master_notes = models.IntegerField()

    lunatic_const = models.DecimalField(max_digits=4,decimal_places=1)
    lunatic_notes = models.IntegerField()

    # 譜面保管所ID
    fumen_id = models.IntegerField()

class SongDataOManager(models.Manager):

    @classmethod
    def update_song_data(cls):
        """
        定数情報を更新するメソッド
        """
        # 情報を取得する
        new_song_data = cls.get_song_data()

        # 更新する
        result = ""

        print("オンゲキ 更新するよん")
        result += "オンゲキ 更新するよん\n"

        for a_song_data in new_song_data:
            o,c =SongDataO.objects.update_or_create(song_name=a_song_data["song_name"],defaults=a_song_data)
            if c:
                print(f"- 作成したよん→ {o.song_name}")
                result += f"- 作成したよん→ {o.song_name}\n"

        print("オンゲキ 更新終わったよん")
        result += "オンゲキ 更新終わったよん\n"

        update_at = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

        return result,update_at

    @classmethod
    def get_song_data(cls):
        """
        定数情報を取得するメソッド
        """
        import requests,re
        from bs4 import BeautifulSoup

        ongeki_const_url = "https://reiwa.f5.si/ongeki_const_all.json"

        # 定数情報を取得する
        response= requests.get(ongeki_const_url)
        response.encoding = response.apparent_encoding
        ongeki_json = response.json()

        # 譜面保管所IDを取得する
        ids_o = {}
        target = ["pops","niconico","toho","variety","chumai","ongeki","lunatic"]

        for t in target:

            TARGET_URL = f"https://www.sdvx.in/ongeki/sort/{t}.htm"
            html = requests.get(TARGET_URL)
            soup = BeautifulSoup(html.content, "html.parser")
            songs = soup.select("body > center > table > tr > td > td > td > tr > td > td> table > tr > td")
            songs_str = str(songs)

            pattern1 = re.compile(r'script src=\"/ongeki/.*/js/.*sort\.js\"></script><script>SORT.*\(\);</script><!--.*-->')
            result1 = pattern1.findall(songs_str)
            for r in result1:
                ids_o[r[82:-3]]=int(r[26:31])

            pattern2 = re.compile(r'script src=\"/ongeki/luna/js/.*luna\.js\"></script><script>SORT.*\(\);</script><!--.*-->')
            result2 = pattern2.findall(songs_str)
            for r in result2:
                ids_o[r[85:-3]]=int(r[28:33])

        # 整形する
        new_songdata = []
        for j in ongeki_json:

            d = {}

            # 情報入力(だいたい)
            d["song_name"]=j["title"]
            d["song_auther"]=j["artist"]
            d["song_catname"]=j["category"]

            # d["song_release"]=datetime.date(*[ int(e) for e in j["add_date"].split("-")])
            d["song_release"]=j["add_date"].split("T")[0]

            try:
                d["expert_const"]=float(j["expert"]["const"])
                if j["expert"]["is_unknown"]:
                    d["expert_const"] = 0
            except:
                d["expert_const"] = 0

            try:
                d["master_const"]=float(j["master"]["const"])
                if j["master"]["is_unknown"]:
                    d["master_const"] = 0
            except:
                d["master_const"] = 0

            try:
                d["lunatic_const"] = float(j["lunatic"]["const"])
                if j["lunatic"]["is_unknown"]:
                    d["lunatic_const"] = 0
            except:
                d["lunatic_const"] = 0

            d["expert_notes"]=0
            d["master_notes"]=0
            d["lunatic_notes"]=0
            # d["expert_notes"]=j["expert"]["maxcombo"]
            # d["master_notes"]=j["master"]["maxcombo"]
            # d["lunatic_notes"]=j["data"]["ULT"]["maxcombo"]

            # 譜面id
            try:
                d["fumen_id"] = ids_o[d["song_name"]]
            except:
                print(f"-- リンク失敗 曲名:{d['song_name']}")
                d["fumen_id"] = 0

            # jsonに足す
            new_songdata.append(d)

        print("取得できたよん")
        return new_songdata

    @classmethod
    def update_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        ongeki_rights_url = "https://ongeki.sega.jp/assets/json/music/music.json"

        # 定数情報を取得する
        response= requests.get(ongeki_rights_url)
        response.encoding = response.apparent_encoding
        ongeki_rights_json = response.json()

        ongeki_rights = []

        for e in ongeki_rights_json:
            if e["copyright1"] != "-":
                ongeki_rights.append(e["copyright1"])

        with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_rights_ongeki.txt"),"w") as f:
            f.write("\n".join(list(set(ongeki_rights))))

    @classmethod
    def search_song_by_query_list(cls,query_list,search_settings):
        """
        query_listから曲データを検索するメソッド
        """
        # 曲名
        song_search_by_name = SongDataO.objects.none()
        for q in query_list:
            song_search_by_name = song_search_by_name|SongDataO.objects.filter(song_name__icontains=q)
            # song_search_by_reading = SongDataO.objects.filter(...)

        # アーティスト名
        song_search_by_artists = SongDataO.objects.filter(song_auther__icontains=query_list[0])

        # 必要に合わせて結合
        song_search_tmp = SongDataO.objects.none()
        if search_settings["is_use_name"]:
            song_search_tmp = song_search_tmp|song_search_by_name
        # if is_use_reading:
        #     song_search_tmp = song_search_tmp|song_search_by_reading
        if search_settings["is_use_artists"]:
            song_search_tmp = song_search_tmp|song_search_by_artists

        # リストにして完成
        song_search = list(song_search_tmp)

        return song_search

    @classmethod
    def get_new_songs(cls,date_before_2_weekly):
        """
        新曲を返すメソッド
        """
        song_new = SongDataO.objects.filter(song_release__gt=date_before_2_weekly)
        search_results_song_list = list(song_new)
        return search_results_song_list

# ----------------------------------

# 部内戦2023試合データ
class GameDataB2023(models.Model):
    game_kisyu = models.CharField(max_length=30)
    game_no = models.CharField(max_length=30)
    game_player = models.CharField(max_length=100)
    game_kadai1 = models.CharField(max_length=50)
    game_kadai2 = models.CharField(max_length=50)
    game_kadai3 = models.CharField(max_length=50)
