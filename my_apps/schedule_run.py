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
    update_log_c = SongDataCManager.update_song_data()
    update_log_o = SongDataOManager.update_song_data()

    # 著作権情報のアップデート
    SongDataCManager.update_rights_data()
    SongDataOManager.update_rights_data()

    # オンゲキジャンル名を取得して既定の場所に出力
    ongeki_genre_url = "https://drive.google.com/uc?id=1UNLvS7gOdZHaM4bXmtS4LcOid5akZdFi"
    r = requests.get(ongeki_genre_url)
    r.encoding = r.apparent_encoding
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/ongeki_genre_data.json"),"w") as f:
        json.dump(r.json(), f, indent=2)

    # 現在時刻をフォーマットを整えて既定の場所に出力
    t_delta = datetime.timedelta(hours=9)
    jst = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(jst)
    with open(os.path.join(settings.BASE_DIR, "my_apps/my_data/const_update_time.txt"),"w") as f:
        f.write(now.strftime("%Y年%m月%d日 %H:%M"))

    return str(update_log_c+update_log_o)


if __name__=="__main__":
   periodic_execution()
