from django.db import models
import requests

# Create your models here.

# DB構造を変化させたくなったら
# ・モデルを変更する (models.py の中の)
# ・これらの変更のためのマイグレーションを作成するために python manage.py makemigrations を実行
# ・データベースにこれらの変更を適用するために python manage.py migrate を実行
# https://docs.djangoproject.com/ja/4.2/intro/tutorial02/

# ----------------------------------

# CHUNITHM 曲データ

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

    # 定数の未確定さ
    # is_const_unknown = models.BooleanField()

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

        print("更新するよん")
        result += "更新するよん\n"

        for a_song_data in new_song_data:
            o,c =SongDataC.objects.update_or_create(song_name=a_song_data["song_name"],defaults=a_song_data)
            if c:
                print(f"- 作成したよん→ {o.song_name}")
                result += f"- 作成したよん→ {o.song_name}\n"

        print("更新終わったよん")
        result += "更新終わったよん\n"

        return result

    @classmethod
    def get_song_data(cls):
        """
        定数情報を取得するメソッド
        """
        import requests

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
            d["expert_notes"]=j["data"]["EXP"]["maxcombo"]
            d["master_const"]=j["data"]["MAS"]["const"]
            d["master_notes"]=j["data"]["MAS"]["maxcombo"]
            try:
                d["ultima_const"]=j["data"]["ULT"]["const"]
                d["ultima_notes"]=j["data"]["ULT"]["maxcombo"]
            except:
                d["ultima_const"]=0
                d["ultima_notes"]=0

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

            # reading
            for e in offi_json:
                if e["title"]==d["song_name"]:
                    d["song_name_reading"]=e["reading"]
                    break

            # jsonに足す
            new_songdata.append(d)

        print("取得できたよん")
        return new_songdata

    @classmethod
    def get_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        rights_data= requests.get("https://chunithm.sega.jp/storage/json/rightsInfo.json")
        rights_data.encoding = rights_data.apparent_encoding
        return rights_data.json()

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

        print("更新するよん")
        result += "更新するよん\n"

        for a_song_data in new_song_data:
            o,c =SongDataO.objects.update_or_create(song_name=a_song_data["song_name"],defaults=a_song_data)
            if c:
                print(f"- 作成したよん→ {o.song_name}")
                result += f"- 作成したよん→ {o.song_name}\n"

        print("更新終わったよん")
        result += "更新終わったよん\n"

        return result

    @classmethod
    def get_song_data(cls):
        """
        定数情報を取得するメソッド
        """
        import requests

        ongeki_const_url = "https://reiwa.f5.si/ongeki_const_all.json"

        # 定数情報を取得する
        response= requests.get(ongeki_const_url)
        response.encoding = response.apparent_encoding
        ongeki_json = response.json()

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
            except:
                d["expert_const"] = 0

            try:
                d["master_const"]=float(j["master"]["const"])
            except:
                d["master_const"] = 0

            try:
                d["lunatic_const"] = float(j["lunatic"]["const"])
            except:
                d["lunatic_const"] = 0

            d["expert_notes"]=0
            d["master_notes"]=0
            d["lunatic_notes"]=0
            # d["expert_notes"]=j["expert"]["maxcombo"]
            # d["master_notes"]=j["master"]["maxcombo"]
            # d["lunatic_notes"]=j["data"]["ULT"]["maxcombo"]

            # jsonに足す
            new_songdata.append(d)

        print("取得できたよん")
        return new_songdata

    @classmethod
    def get_rights_data(cls):
        """
        著作権情報を取得するメソッド
        """
        import requests

        ongeki_rights_url = "https://ongeki.sega.jp/assets/json/music/music.json"

        # 定数情報を取得する
        response= requests.get(ongeki_rights_url)
        response.encoding = response.apparent_encoding
        ongeki_rights_json = response.json()

        ongeki_rights = []

        for e in ongeki_rights_json:
            if e["copyright1"] != "-":
                ongeki_rights.append(e["copyright1"])

        return (list(set(ongeki_rights)))
