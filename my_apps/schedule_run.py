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
    # オンゲキジャンル名を取得して既定の場所に出力
    get_ongeki_genre()

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


    return


def get_ongeki_genre():
    URL = "https://wikiwiki.jp/gameongeki/%E7%A7%B0%E5%8F%B7%E4%B8%80%E8%A6%A7"
    P = re.compile(r"[「」](.+)[「」]")

    # 既存データを読み込み
    existing_data = {}
    json_path = os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                existing_json = json.load(f)
                existing_data = existing_json.get("genre_data", {})
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = {}

    # wikiwikiから取得
    r = requests.get(URL, headers={"User-Agent": ""})
    soup = BeautifulSoup(r.text, "html.parser")

    genre_list = []
    # 表1
    genre_table = soup.select(
        'p:-soup-contains("称号はすべてオリジナル曲・コラボ曲のジャンル名となっている。") ~ div.h-scrollable td '
    )
    for i, d in enumerate(genre_table):
        if i % 2 == 0:
            if len(d.text) == 0:
                break
            genre_list.append(d.text)
        else:
            genre_list.append(re.findall(P, d.text)[0].replace("」「", ", "))

    genre_table = soup.select('li:-soup-contains("称号はすべてオリジナル曲のジャンル名となっている") div.h-scrollable td ')
    for i, d in enumerate(genre_table):
        if i <= 1:
            continue
        if i % 2 == 0:
            if len(d.text) == 0:
                break
            genre_list.append(d.text)
        else:
            genre_list.append(re.findall(P, d.text)[0].replace("」「", ", "))

    # リストを2つずつに分ける
    genre_pairs = [genre_list[i : i + 2] for i in range(0, len(genre_list), 2)]

    # 新しいデータと既存データをマージ
    merged_data = existing_data.copy()  # 既存データをベースに
    for genre, song_name in genre_pairs:
        merged_data[genre] = song_name  # 新しいデータで上書き/追加

    # json化して出力
    ongeki_genre_json = {
        "genre_data": merged_data,
        "updated_date": datetime.date.today().strftime("%Y/%m/%d")
    }
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"), "w", encoding="utf-8") as f:
        json.dump(ongeki_genre_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    schedule_run()
    # get_ongeki_genre()
