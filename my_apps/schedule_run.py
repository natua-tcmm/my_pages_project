import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django import setup
setup()

from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from my_apps.models import *
import datetime

def periodic_execution():
    # 定数情報のアップデート
    update_log_c = SongDataCManager.update_song_data()
    update_log_o = SongDataOManager.update_song_data()

    #現在時刻をフォーマットを整えて既定の場所に出力
    t_delta = datetime.timedelta(hours=9)
    jst = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(jst)
    with open("my_apps/my_data/const_update_time.txt","w") as f:
        f.write(now.strftime("%Y年%m月%d日 %H:%M"))

    return str(update_log_c+update_log_o)


if __name__=="__main__":
   periodic_execution()
