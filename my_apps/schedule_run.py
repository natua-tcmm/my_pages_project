import os, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR.__str__())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django import setup

setup()

from django.conf import settings
import datetime, requests, json, re
from bs4 import BeautifulSoup

from my_apps.models import SongDataCNManager, SongDataONManager
from my_apps.my_script import handle_songdata_c_refactor, handle_songdata_o_refactor


def schedule_run():

    # -------------------------------------
    # 楽曲データの更新
    # -------------------------------------
    # jsonファイルを更新する
    print("-" * 50)
    print("楽曲データの更新を開始します")
    print("-" * 50)
    handle_songdata_c_refactor.main()
    handle_songdata_o_refactor.main()

    # jsonファイルからデータベースにインポート・アップデート日時を更新
    print("-" * 50)
    print("楽曲データをデータベースにインポートします")
    print("-" * 50)
    SongDataCNManager.import_songdata_from_json()
    SongDataONManager.import_songdata_from_json()

    print("-" * 50)

    # -------------------------------------
    # その他
    # -------------------------------------
    # 著作権情報のアップデート
    SongDataCNManager.update_rights_data()
    SongDataONManager.update_rights_data()

    # オンゲキジャンル名を取得して既定の場所に出力
    get_ongeki_genre()

    return


def get_ongeki_genre():
    URL = "https://wikiwiki.jp/gameongeki/%E7%A7%B0%E5%8F%B7%E4%B8%80%E8%A6%A7"
    P = re.compile(r"[「」](.+)[「」]")

    # wikiwikiから取得
    r = requests.get(URL, headers={"User-Agent": ""})
    soup = BeautifulSoup(r.text, "html.parser")
    genre_table = soup.select('p:-soup-contains("称号はすべてオリジナル曲のジャンル名となっている") ~ div.h-scrollable td ')

    # リスト化
    genre_list = []
    for i, d in enumerate(genre_table):
        if i % 2 == 0:
            if len(d.text) == 0:
                break
            genre_list.append(d.text)
        else:
            genre_list.append(re.findall(P, d.text)[0].replace("」「", ", "))
    genre_pairs = [genre_list[i : i + 2] for i in range(0, len(genre_list), 2)]

    # json化して出力
    ongeki_genre_json = {}
    ongeki_genre_json["genre_data"] = {}
    ongeki_genre_json["updated_date"] = datetime.date.today().strftime("%Y/%m/%d")
    for genre, song_name in genre_pairs:
        ongeki_genre_json["genre_data"][genre] = song_name
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"), "w") as f:
        json.dump(ongeki_genre_json, f, indent=2)


if __name__ == "__main__":
    schedule_run()
