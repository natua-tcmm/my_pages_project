import os, sys
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent.parent.__str__())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django import setup

setup()

from django.conf import settings

# from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from my_apps.models import *
import datetime, requests, json, re
from bs4 import BeautifulSoup

from my_apps.my_script import handle_songdata_c_refactor
from my_apps.my_script import handle_songdata_o_refactor


def periodic_execution():
    # 定数情報のアップデート
    update_log_c = SongDataCManager.update_song_data()
    update_log_o = SongDataOManager.update_song_data()

    # 著作権情報のアップデート
    SongDataCManager.update_rights_data()
    SongDataOManager.update_rights_data()

    # オンゲキジャンル名を取得して既定の場所に出力
    get_ongeki_genre()

    # [テスト運用] 新しいデータ収集ツール
    print("-" * 50)
    print("新しいデータ収集ツールを実行します...")
    print("[CHUNITHM]")
    handle_songdata_c_refactor.main()
    print("[オンゲキ]")
    handle_songdata_o_refactor.main()
    print("-" * 50)

    # 現在時刻をフォーマットを整えて既定の場所に出力
    t_delta = datetime.timedelta(hours=9)
    jst = datetime.timezone(t_delta, "JST")
    now = datetime.datetime.now(jst)
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_time.txt"), "w") as f:
        f.write(now.strftime("%Y年%m月%d日 %H:%M"))

    return str(update_log_c + update_log_o)


def get_ongeki_genre():
    URL = "https://wikiwiki.jp/gameongeki/%E7%A7%B0%E5%8F%B7%E4%B8%80%E8%A6%A7"
    P = re.compile(r"[「」](.+)[「」]")

    # wikiwikiから取得
    r = requests.get(URL, headers={"User-Agent": ""})
    soup = BeautifulSoup(r.text, "html.parser")
    genre_table = soup.select(
        'p:-soup-contains("称号はすべてオリジナル曲・コラボ曲のジャンル名となっている。") ~ div.h-scrollable td '
    )

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
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"), "w", encoding="utf-8") as f:
        json.dump(ongeki_genre_json, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    periodic_execution()
    # get_ongeki_genre()
