import os, sys
from pathlib import Path
sys.path.append(Path(__file__).resolve().parent.parent.__str__())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django import setup
setup()

from django.conf import settings
# from datetime import datetime, date
# from apscheduler.schedulers.background import BackgroundScheduler
from my_apps.models import *
import datetime, requests, json, re
from bs4 import BeautifulSoup

def periodic_execution():

    # 定数情報のアップデート
    update_at_c = SongDataCNManager.import_songdata_from_json()

    # 著作権情報のアップデート
    SongDataCNManager.update_rights_data()
    SongDataOManager.update_rights_data()

    # オンゲキジャンル名を取得して既定の場所に出力
    get_ongeki_genre()

    # 現在時刻をフォーマットを整えて既定の場所に出力
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_at_c.txt"),"w") as f:
        f.write(update_at_c)
    # with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_at_o.txt"),"w") as f:
    #     f.write(update_at_o)

    return

def get_ongeki_genre():
    URL = "https://wikiwiki.jp/gameongeki/%E7%A7%B0%E5%8F%B7%E4%B8%80%E8%A6%A7"
    P = re.compile(r'[「」](.+)[「」]')

    # wikiwikiから取得
    r = requests.get(URL, headers={'User-Agent': ''})
    soup = BeautifulSoup(r.text,"html.parser")
    genre_table = soup.select('p:-soup-contains("称号はすべてオリジナル曲のジャンル名となっている") ~ div.h-scrollable td ')

    # リスト化
    genre_list = []
    for i,d in enumerate(genre_table):
        if i%2==0:
            genre_list.append(d.text)
        else:
            genre_list.append(re.findall(P,d.text)[0])
    genre_pairs = [genre_list[i:i+2] for i in range(0, len(genre_list), 2)]

    # json化して出力
    ongeki_genre_json = {}
    ongeki_genre_json["genre_data"] = {}
    ongeki_genre_json["updated_date"] = datetime.date.today().strftime("%Y/%m/%d")
    for genre,song_name in genre_pairs:
        ongeki_genre_json["genre_data"][genre]=song_name
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"),"w") as f:
            json.dump(ongeki_genre_json, f, indent=2)


if __name__=="__main__":
   periodic_execution()
