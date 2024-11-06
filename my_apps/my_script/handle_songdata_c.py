import requests, re, json, html, copy, datetime, os
from pathlib import Path
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import linebot.v3.messaging as bot # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_FILE_PATH = os.path.join(BASE_DIR,"my_apps/my_data/songdata_c_dict.json")

# 環境変数のロード
load_dotenv(verbose=True)
dotenv_path = os.path.join(BASE_DIR.parent, '.env')
load_dotenv(dotenv_path)
LINE_BOT_ACCESS_TOKEN = os.environ.get("LINE_BOT_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

############################

# 関数集
def init_songdata_c():
    songdata_c = {

        "song_official_id":None,
        "song_name":None,
        "song_reading":None,
        "song_artist":None,
        "song_genre":None,
        "song_bpm":None,
        "song_bpm_nodata":None,
        "song_release":None,
        "song_image_url":None,
        "song_fumen_id":None, # 文字列5ケタ 01234みたいに

        "is_worldsend":None,
        "has_ultima":None,
        "only_ultima":None,

        "exp_const":None,
        "exp_const_nodata":None,
        "exp_notes":None,
        "exp_notes_nodata":None,
        "exp_notesdesigner":None,
        "exp_notesdesigner_nodata":None,

        "mas_const":None,
        "mas_const_nodata":None,
        "mas_notes":None,
        "mas_notes_nodata":None,
        "mas_notesdesigner":None,
        "mas_notesdesigner_nodata":None,

        "ult_const":None,
        "ult_const_nodata":None,
        "ult_notes":None,
        "ult_notes_nodata":None,
        "ult_notesdesigner":None,
        "ult_notesdesigner_nodata":None,

        "we_star":None,
        "we_kanji":None,

    }
    return songdata_c

def get_json_by_official():
    """
    公式サイトからjsonファイルを取得する
    """
    response= requests.get("https://chunithm.sega.jp/storage/json/music.json")
    response.encoding = response.apparent_encoding
    json_offi = response.json()
    return json_offi

def apply_songdata_c_by_official(songdata_c,s_offi):
    """
    公式データから楽曲情報を取り出す
    """
    songdata_c["song_official_id"]=s_offi["id"]
    songdata_c["song_name"]=s_offi["title"]
    songdata_c["song_reading"]=s_offi["reading"]
    songdata_c["song_artist"]=s_offi["artist"]
    songdata_c["song_genre"]=s_offi["catname"]
    songdata_c["song_image_url"]=s_offi["image"]
    songdata_c["is_worldsend"]=bool(len(s_offi["we_kanji"])>0)
    songdata_c["has_ultima"]=bool(len(s_offi["lev_ult"])>0)
    songdata_c["only_ultima"]=False
    if songdata_c["is_worldsend"]:
        songdata_c["we_star"]=s_offi["we_star"]
        songdata_c["we_kanji"]=s_offi["we_kanji"]

def get_songdata_c_by_reiwaf5():
    """
    reiwaf5からjsonを取得する
    """
    response= requests.get("https://reiwa.f5.si/chunirec_all.json")
    response.encoding = response.apparent_encoding
    json_reiwaf5 = response.json()
    return json_reiwaf5

def search_songdata_c_by_reiwaf5(songdata_c,json_reiwaf5,msg_list):
    """
    reiwaf5の情報から楽曲データを検索する
    """
    for i,sr_tmp in enumerate(json_reiwaf5):
        if songdata_c["song_name"]==sr_tmp["meta"]["title"]:
            sr = sr_tmp
            break
    else:
        msg_list.append(f"[search_songdata_c_by_reiwaf5] reiwaf5内にデータがありません。検索に失敗しました。song_name:{songdata_c['song_name']}")
        return None

    return sr

def aplly_songdata_c_by_reiwaf5(songdata_c,s_reiwaf5):
    """
    reiwaf5の情報から楽曲データを取り出す
    """

    # リリース日
    songdata_c["song_release"]=s_reiwaf5["meta"]["release"]

    # EXPERT
    # レベル10未満はレベルと定数が一致する
    if s_reiwaf5["data"]["EXP"]["level"]<10:
        songdata_c["exp_const"]=s_reiwaf5["data"]["EXP"]["level"]
        songdata_c["exp_const_nodata"]=False
    elif bool(s_reiwaf5["data"]["EXP"]["is_const_unknown"]):
        songdata_c["exp_const"]=s_reiwaf5["data"]["EXP"]["level"]
        songdata_c["exp_const_nodata"]=True
    else:
        songdata_c["exp_const"]=s_reiwaf5["data"]["EXP"]["const"]
        songdata_c["exp_const_nodata"]=False

    # MASTER
    if bool(s_reiwaf5["data"]["MAS"]["is_const_unknown"]):
        songdata_c["mas_const"]=s_reiwaf5["data"]["MAS"]["level"]
        songdata_c["mas_const_nodata"]=True
    else:
        songdata_c["mas_const"]=s_reiwaf5["data"]["MAS"]["const"]
        songdata_c["mas_const_nodata"]=False

    # ULTIMA 存在するなら
    if songdata_c["has_ultima"]:
        if bool(s_reiwaf5["data"]["ULT"]["is_const_unknown"]):
            songdata_c["ult_const"]=s_reiwaf5["data"]["ULT"]["level"]
            songdata_c["ult_const_nodata"]=True
        else:
            songdata_c["ult_const"]=s_reiwaf5["data"]["ULT"]["const"]
            songdata_c["ult_const_nodata"]=False

def search_fumenID_c_by_officialID(song_official_id,songdata_c_dict):
    """
    officialIDからfumenIDを検索
    """
    for e in songdata_c_dict["songs"]:
        if e["song_official_id"]==song_official_id:
            return f'{e["song_fumen_id"]}'
    else:
        print(f"- ",end="")
        print(f"ID:{song_official_id}")
        return None

def make_known_fumen_ids_list(songdata_c_dict):
    """
    既知の保管所IDをリストにする
    """
    known_fumen_ids = []
    for e in songdata_c_dict["songs"]:
        if e["song_fumen_id"] is not None and len(e["song_fumen_id"])>1:
            known_fumen_ids.append(e["song_fumen_id"])
    return known_fumen_ids

def get_songdata_c_by_fumen(songdata_c):
    """
    譜面保管所から楽曲データを取り出す
    """
    return_msg = []

    # 通常譜面
    request = requests.get(f"https://www.sdvx.in/chunithm/{songdata_c['song_fumen_id'][:2]}/js/{songdata_c['song_fumen_id']}sort.js")

    if request.ok:
        data = html.unescape(request.text).replace("\r\n","").split(";")

        try:
            songdata_c["song_bpm"] = int(re.search(r'<td class=f\d>(.*?)</table>',data[2]).group(1))
            songdata_c["song_bpm_nodata"]=False
        except:
            songdata_c["song_bpm_nodata"]=True

        try:
            songdata_c["exp_notesdesigner"]=re.search(r'<td class=ef>NOTES DESIGNER / (.*?)</table>',data[3]).group(1)
            songdata_c["exp_notesdesigner_nodata"]=False
        except:
            songdata_c["exp_notesdesigner_nodata"]=True

        try:
            songdata_c["mas_notesdesigner"]=re.search(r'<td class=ef>NOTES DESIGNER / (.*?)</table>',data[4]).group(1)
            songdata_c["mas_notesdesigner_nodata"]=False
        except:
            songdata_c["mas_notesdesigner_nodata"]=True

        try:
            songdata_c["exp_notes"]=int(re.search(r'<td class=exp1>(.*?)</table>',data[11]).group(1))
            songdata_c["exp_notes_nodata"]=False
        except:
            songdata_c["exp_notes_nodata"]=True

        try:
            songdata_c["mas_notes"]=int(re.search(r'<td class=mst1>(.*?)</table>',data[12]).group(1))
            songdata_c["mas_notes_nodata"]=False
        except:
            songdata_c["mas_notes_nodata"]=True

        # songdata_c["song_bpm_nodata"]=False
        # songdata_c["exp_notesdesigner_nodata"]=False
        # songdata_c["mas_notesdesigner_nodata"]=False
        # songdata_c["exp_notes_nodata"]=False
        # songdata_c["mas_notes_nodata"]=False

    else:
        # print(f"[get_songdata_c_by_fumen] 取得失敗(通常) {songdata_c['song_fumen_id']}")
        return_msg.append(f"[get_songdata_c_by_fumen] 取得失敗(通常) {songdata_c['song_fumen_id']}")
        songdata_c["song_bpm_nodata"]=True
        songdata_c["exp_notesdesigner_nodata"]=True
        songdata_c["mas_notesdesigner_nodata"]=True
        songdata_c["exp_notes_nodata"]=True
        songdata_c["mas_notes_nodata"]=True

    # ULT譜面
    if songdata_c["has_ultima"]:
        request = requests.get(f"https://www.sdvx.in/chunithm/ult/js/{songdata_c['song_fumen_id']}ult.js")

        if request.ok:
            data = html.unescape(request.text).replace("\r\n","").split(";")

            try:
                songdata_c["ult_notesdesigner"]=re.search(r'<td class=ef>NOTES DESIGNER / (.*?)</table>',data[3]).group(1)
                songdata_c["ult_notesdesigner_nodata"]=False
            except:
                songdata_c["ult_notesdesigner_nodata"]=True

            try:
                songdata_c["ult_notes"]=int(re.search(r'<td class=ult1>(.*?)</table>',data[5]).group(1))
                songdata_c["ult_notes_nodata"]=False
            except:
                songdata_c["ult_notes_nodata"]=True

            # songdata_c["ult_notesdesigner_nodata"]=False
            # songdata_c["ult_notes_nodata"]=False
        else:
            # print(f"[get_songdata_c_by_fumen] 取得失敗(ULT) {songdata_c['song_fumen_id']}")
            return_msg.append(f"[get_songdata_c_by_fumen] 取得失敗(ULT) {songdata_c['song_fumen_id']}")
            songdata_c["ult_notesdesigner_nodata"]=True
            songdata_c["ult_notes_nodata"]=True

    return return_msg

def search_songdata_c_by_official_id(songdata_c_dict,offi_id):
    """
    公式IDでsongdata_cを検索する
    """
    for songdata_c in songdata_c_dict["songs"]:
        if songdata_c["song_official_id"]==offi_id:
            return songdata_c
    else:
        return None

def send_line_msg(msg_list):
    """
    LINEでメッセージを送信する
    """
    msg = "\n".join(msg_list)
    configuration = bot.Configuration(
        access_token=LINE_BOT_ACCESS_TOKEN
    )
    message_dict = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text":msg}]
    }

    with bot.ApiClient(configuration) as api:
        api_instance = bot.MessagingApi(api)
        push_message_request = bot.PushMessageRequest.from_dict(
            message_dict)
        try:
            res = api_instance.push_message(push_message_request)
        except Exception as e:
            pass

def convert_json_file_unicode_escape_to_string(file_path):
    """
    JSONファイルのUnicodeエスケープを文字列にする
    """
    # JSONファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as file:
        json_string = file.read()

    # Unicodeエスケープシーケンスをデコードしてから再エンコード
    decoded_data = json.loads(json_string)
    encoded_string = json.dumps(decoded_data, ensure_ascii=False, indent=4)

    # 同じファイル名で上書き保存
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(encoded_string)

############################

# 新曲登録処理
def get_new_song_data():

    msg_list = ["【新曲登録処理】"]

    # 公式とreiwaf5から全楽曲データを取得する
    json_official = get_json_by_official()
    json_reiwaf5 = get_songdata_c_by_reiwaf5()

    # データ一覧を読み込む
    with open(JSON_FILE_PATH, "r") as f:
        songdata_c_dict = json.load(f)

    ################


    ## 新曲IDを取得
    # (公式jsonのID一覧と既存ID一覧と照らし合わせる)
    print("---\n新曲候補")
    new_song_ids = []
    for s_offi in json_official:
        # WEを除外する
        if not len(s_offi["we_kanji"])>0:
            if search_fumenID_c_by_officialID(s_offi["id"],songdata_c_dict) is None:
                new_song_ids.append([s_offi["id"],s_offi["title"]])

    # リンク処理しないならreturnしていいけど、しないままでよさそう
    # if len(new_song_ids)==0:
    #     return

    msg_list.append(f"新曲候補数:{len(new_song_ids)}")

    ## 新曲のデータを作る
    # 公式jsonから新曲IDに対応するデータを抽出 このへんリファクタリングできるなぁあ
    json_official_new = []
    for new_song_id in new_song_ids:
        for s_offi in json_official:
            if s_offi["id"]==new_song_id[0]:
                json_official_new.append(s_offi)

    # データを作成し追加する(保管所の情報以外)
    songdata_c_dict["new_song_offi_ids"] = []
    for s_offi in json_official_new:

        # 初期化
        songdata_c = init_songdata_c()

        # 公式サイトから
        apply_songdata_c_by_official(songdata_c,s_offi)

        # reiwaf5から
        if songdata_c["is_worldsend"]:
            pass
        else:
            s_reiwaf5 = search_songdata_c_by_reiwaf5(songdata_c,json_reiwaf5,msg_list)
            if s_reiwaf5 is None:
                continue
            aplly_songdata_c_by_reiwaf5(songdata_c,s_reiwaf5)

        # 譜面保管所からの分をNoDataにしておく
        if songdata_c["is_worldsend"]:
            pass
        else:
            songdata_c["song_bpm_nodata"]=True
            songdata_c["exp_notesdesigner_nodata"]=True
            songdata_c["mas_notesdesigner_nodata"]=True
            songdata_c["exp_notes_nodata"]=True
            songdata_c["mas_notes_nodata"]=True

            if songdata_c["has_ultima"]:
                songdata_c["ult_notesdesigner_nodata"]=True
                songdata_c["ult_notes_nodata"]=True


        songdata_c_dict["songs"].append(songdata_c)
        songdata_c_dict["new_song_offi_ids"].append(s_offi["id"])


    ## 保管所IDとの紐づけ
    # 保管所の全IDを取得、DBに存在するIDを除外したものを保管所新曲IDとする
    import html,requests
    songs_fumen_tmp = []
    urls = [f"https://www.sdvx.in/chunithm/sort/{g}.htm" for g in ["pops","niconico","toho","variety","irodorimidori","gekimai","original"] ]
    for url in urls:
        html_ = requests.get(url)
        soup = BeautifulSoup(html_.content, "html.parser")
        for l in str(soup).split("\n"):
            try:
                songs_fumen_tmp.append(re.search(r'<script src="/chunithm/.*?/.*?/([0-9]+)sort\.js">',l).group(1))
            except:
                pass
    known_fumen_ids = make_known_fumen_ids_list(songdata_c_dict)
    new_songs_fumen_tmp = list( set(songs_fumen_tmp)-set(known_fumen_ids) )

    msg_list.append(f"譜面保管所新曲候補数:{len(new_songs_fumen_tmp)}")
    msg_list.append(f"-----\nリンク処理")

    # 保管所新曲IDから曲名を取得し公式IDと照合
    link_id_tuples = []
    for fumen_id in new_songs_fumen_tmp:
        # 曲名取得
        request = requests.get(f"https://www.sdvx.in/chunithm/{fumen_id[:2]}/js/{fumen_id}sort.js")
        if request.ok:
            data = html.unescape(request.text).replace("\r\n","").split(";")
            song_name_fumen = re.search(r'<div class=f\d>(.*?)</div>',data[0]).group(1)
        else:
            msg_list.append(f"- 譜面ID:{fumen_id}の保管所からの曲名情報取得に失敗しました。")
            continue

        # データを検索
        for s in songdata_c_dict["songs"]:
            # WEを除外
            if s["is_worldsend"]:
                pass
            else:
                # 曲名が一致しているものを抽出
                if s["song_name"]==song_name_fumen:
                    # IDが未知ならリンク
                    if s["song_fumen_id"] is None:
                        s["song_fumen_id"]=fumen_id
                        link_id_tuples.append([s['song_official_id'],s['song_fumen_id']])
                        msg_list.append(f"- リンク成功:『{s['song_name']}』 ID:{s['song_official_id']}-{s['song_fumen_id']}")
                        break
                    # IDが既知ならリンクしない
                    else:
                        msg_list.append(f"- 『{s['song_name']}』はリンク済です。 ID:{s['song_official_id']}-{s['song_fumen_id']}")
                        break
        # 曲名一致してないなら
        else:
            msg_list.append(f"- 『{s['song_name']}』のリンクに失敗しました。 ID:{s['song_official_id']}-{s['song_fumen_id']}")


    ## 保管所からのデータをスクレイピングして登録する
    # link_id_tuplesから保管所データ未登録のIDを収集
    print("---\n保管所からデータを取得します。")
    import html
    link_ids = [ t[0] for t in link_id_tuples ]
    for songdata_c in songdata_c_dict["songs"]:

        # 未登録データであればスクレイピング
        if( songdata_c["song_official_id"] in link_ids):

            # 譜面保管所から
            if songdata_c["is_worldsend"]:
                pass
            else:
                return_msg = get_songdata_c_by_fumen(songdata_c)
                msg_list += return_msg

    ################

    # 保存する
    songdata_c_dict["update_at"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(songdata_c_dict, f, indent=4)
        print("保存しました。")
    convert_json_file_unicode_escape_to_string(JSON_FILE_PATH)


    # LINE通知
    send_line_msg(msg_list)
    print("\n".join(msg_list))

    return

# 既存曲確認処理
def check_existing_song():

    msg_list = ["【更新処理】"]

    # 公式とreiwaf5から全楽曲データを取得する
    json_reiwaf5 = get_songdata_c_by_reiwaf5()
    json_official = get_json_by_official()

    # データ一覧を読み込む
    with open(JSON_FILE_PATH, "r") as f:
        songdata_c_dict = json.load(f)

    ################

    # 更新曲一覧の初期化
    songdata_c_dict["update_song_offi_ids"] = []
    songdata_c_dict["delete_song_offi_ids"] = []

    # 削除曲
    msg_list.append("削除曲")
    for songdata_c in copy.deepcopy(songdata_c_dict["songs"]):
        # 検索
        for s_offi in json_official:
            if s_offi["id"]==songdata_c["song_official_id"]:
                break
        else:
            msg_list.append(f'- {songdata_c["song_name"]}')
            songdata_c_dict["songs"].remove(songdata_c)
            songdata_c_dict["delete_song_offi_ids"].append(songdata_c["song_official_id"])

    # ULT
    msg_list.append("ULTIMA更新")
    for s_offi in json_official:
        songdata_c = search_songdata_c_by_official_id(songdata_c_dict,s_offi["id"])
        if not len(s_offi["we_kanji"])>0:
            # ultimaが存在してないはずなのに存在していたら
            if songdata_c["has_ultima"] != bool(len(s_offi["lev_ult"])>0):

                # print(songdata_c["song_name"])
                msg_list.append(f"- {songdata_c['song_name']}")

                # reiwaf5の情報を取得
                s_reiwaf5 = search_songdata_c_by_reiwaf5(songdata_c,json_reiwaf5,msg_list)
                if s_reiwaf5 is None:
                    continue

                # 情報を更新する
                songdata_c["has_ultima"] = True
                if bool(s_reiwaf5["data"]["ULT"]["is_const_unknown"]):
                    songdata_c["ult_const"]=s_reiwaf5["data"]["ULT"]["level"]
                    songdata_c["ult_const_nodata"]=True
                else:
                    songdata_c["ult_const"]=s_reiwaf5["data"]["ULT"]["const"]
                    songdata_c["ult_const_nodata"]=False

                songdata_c_dict["update_song_offi_ids"].append(songdata_c["song_official_id"])

    # 定数更新
    msg_list.append("定数更新")
    for songdata_c in songdata_c_dict["songs"]:
        if songdata_c["is_worldsend"]:
                continue

        s_reiwaf5 = search_songdata_c_by_reiwaf5(songdata_c,json_reiwaf5,msg_list)

        # EXPERT/MASTER
        if songdata_c["exp_const"]!=s_reiwaf5["data"]["EXP"]["const"] and not bool(s_reiwaf5["data"]["EXP"]["is_const_unknown"]) and s_reiwaf5["data"]["EXP"]["level"]>=10:
            msg_list.append(f'- {songdata_c["song_name"]} EXPERT | {songdata_c["exp_const"]} -> {s_reiwaf5["data"]["EXP"]["const"]}')
            songdata_c["exp_const"]=s_reiwaf5["data"]["EXP"]["const"]
            songdata_c["exp_const_nodata"]=False
            songdata_c_dict["update_song_offi_ids"].append(songdata_c["song_official_id"])


        if songdata_c["mas_const"]!=s_reiwaf5["data"]["MAS"]["const"] and not bool(s_reiwaf5["data"]["MAS"]["is_const_unknown"]):
            msg_list.append(f'- {songdata_c["song_name"]} MASTER | {songdata_c["mas_const"]} -> {s_reiwaf5["data"]["MAS"]["const"]}')
            songdata_c["mas_const"]=s_reiwaf5["data"]["MAS"]["const"]
            songdata_c["mas_const_nodata"]=False
            songdata_c_dict["update_song_offi_ids"].append(songdata_c["song_official_id"])

        # ULTIMA 存在するなら
        if songdata_c["has_ultima"]:
            if songdata_c["ult_const"]!=s_reiwaf5["data"]["ULT"]["const"] and not bool(s_reiwaf5["data"]["ULT"]["is_const_unknown"]):
                msg_list.append(f'- {songdata_c["song_name"]} ULTIMA | {songdata_c["ult_const"]} -> {s_reiwaf5["data"]["ULT"]["const"]}')
                songdata_c["ult_const"]=s_reiwaf5["data"]["ULT"]["const"]
                songdata_c["ult_const_nodata"]=False
                songdata_c_dict["update_song_offi_ids"].append(songdata_c["song_official_id"])


    # BPM更新
    msg_list.append("BPM更新")
    for songdata_c in songdata_c_dict["songs"]:
        if songdata_c["is_worldsend"] or songdata_c["song_fumen_id"] is None:
                continue
        if songdata_c["song_bpm_nodata"]:

            msg_list.append(f'- {songdata_c["song_name"]}')

            request = requests.get(f"https://www.sdvx.in/chunithm/{songdata_c['song_fumen_id'][:2]}/js/{songdata_c['song_fumen_id']}sort.js")

            if request.ok:
                data = html.unescape(request.text).replace("\r\n","").split(";")

                try:
                    songdata_c["song_bpm"] = int(re.search(r'<td class=f\d>(.*?)</table>',data[2]).group(1))
                    songdata_c["song_bpm_nodata"]=False
                    songdata_c_dict["update_song_offi_ids"].append(songdata_c["song_official_id"])
                except:
                    msg_list.append(f"--- 更新できませんでした")

            else:
                msg_list.append(f"--- 取得に失敗しました")

    ################

    # 保存する
    songdata_c_dict["update_at"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(songdata_c_dict, f, indent=4)
        print("保存しました")
    convert_json_file_unicode_escape_to_string(JSON_FILE_PATH)

    # LINE通知
    send_line_msg(msg_list)
    print("\n".join(msg_list))

    return

# 実行
def json_file_update():
    get_new_song_data()
    check_existing_song()

if __name__=="__main__":
    send_line_msg(["test"])
