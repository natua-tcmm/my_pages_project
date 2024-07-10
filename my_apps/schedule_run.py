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
import datetime, requests, json

def periodic_execution():

    # 定数情報のアップデート
    update_at_c = SongDataCNManager.import_songdata_from_json()

    # 著作権情報のアップデート
    SongDataCNManager.update_rights_data()
    SongDataOManager.update_rights_data()

    # オンゲキジャンル名を取得して既定の場所に出力
    ongeki_genre_url = "https://drive.google.com/uc?id=1UNLvS7gOdZHaM4bXmtS4LcOid5akZdFi"
    r = requests.get(ongeki_genre_url)
    r.encoding = r.apparent_encoding
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"),"w") as f:
        json.dump(r.json(), f, indent=2)

    # 現在時刻をフォーマットを整えて既定の場所に出力
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_at_c.txt"),"w") as f:
        f.write(update_at_c)
    # with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_at_o.txt"),"w") as f:
    #     f.write(update_at_o)

    return


if __name__=="__main__":
   periodic_execution()
