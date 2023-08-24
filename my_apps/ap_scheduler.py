from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from .models import *
import datetime

# 定期的に実行する関数
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


def start():
  scheduler = BackgroundScheduler()
  # scheduler.add_job( periodic_execution, 'interval', hours=2, start_date='2023-01-01 00:00:00' )
  scheduler.add_job( periodic_execution, 'date', run_date="2023-08-24 20:09:50" )
  scheduler.start()
