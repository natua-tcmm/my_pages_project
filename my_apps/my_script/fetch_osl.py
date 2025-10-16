import requests, re, math, datetime, dateutil.parser
from bs4 import BeautifulSoup


# 単曲レート計算
def calc_music_rate_old(score_rank: str, t_score: int, const: float) -> float:

    music_rate = 0

    if score_rank == "SSS+" or score_rank == "AB+":
        music_rate = const + 2
    elif score_rank == "SSS":
        music_rate = const + 1.5 + math.floor((t_score - 1_000_000) / 150) * 0.01
    elif score_rank == "SS":
        music_rate = const + 1 + math.floor((t_score - 990_000) / 200) * 0.01
    elif score_rank == "S":
        music_rate = const + 0 + math.floor((t_score - 970_000) / 200) * 0.01
    elif score_rank == "AAA" or score_rank == "AA":
        music_rate = const - 4 + math.floor((t_score - 900_000) / 175) * 0.01

    music_rate = int(music_rate * 100 + 0.5) / 100

    return music_rate

# 単曲レート計算(新)
def calc_music_rate(score_rank: str, t_score: int, const: float, is_FC:bool, is_AB:bool, is_FB:bool) -> float:

    music_rate = 0

    # TSポイント
    # スコアランク	TS	値
    if score_rank == "AB+":
        music_rate = const + 2.0
    elif score_rank == "SSS+":
        music_rate = const + 1.75 + math.floor((t_score - 1_007_500) / 10) * 0.001
    elif score_rank == "SSS":
        music_rate = const + 1.25 + math.floor((t_score - 1_000_000) / 15) * 0.001
    elif score_rank == "SS":
        music_rate = const + 0.75 + math.floor((t_score - 990_000) / 20) * 0.001
    elif score_rank == "S":
        music_rate = const + math.floor((t_score - 970_000) / 26.66666) * 0.001
    elif score_rank in ["AAA","AA"]:
        music_rate = const - 4 + math.floor((t_score - 900_000) / 17.5) * 0.001
    elif score_rank in ["A","BBB"]:
        music_rate = const - 6 + math.floor((t_score - 800_000) / 50) * 0.001
    else:
        music_rate = 0

    if music_rate < 0:
        music_rate = 0

    # ランクポイント
    if score_rank == "SSS+":
        music_rate += 0.3
    elif score_rank == "SSS":
        music_rate += 0.2
    elif score_rank == "SS":
        music_rate += 0.1

    # FBポイント
    if is_FB:
        music_rate += 0.05

    # ランプポイント
    is_ABplus = score_rank == "AB+"
    if is_FC and not is_AB:
        music_rate += 0.1
    elif is_AB and not is_ABplus:
        music_rate += 0.3
    elif is_ABplus:
        music_rate += 0.35


    # 切り捨て
    music_rate = int(music_rate * 1000 + 0.5) / 1000

    return music_rate


# オンゲキのバージョンを求める
def date2ongekiversion(t: str) -> str:
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    d = dateutil.parser.parse(t).astimezone(JST).date()
    # d = datetime.datetime.fromisoformat(t).astimezone(datetime.timezone(datetime.timedelta(hours=9))).date()

    ongeki_versions = [
        "無印",
        "PLUS",
        "SUMMER",
        "SUMMER PLUS",
        "R.E.D.",
        "R.E.D. PLUS",
        "bright",
        "bright MEMORY Act.1",
        "bright MEMORY Act.2",
        "bright MEMORY Act.3",
    ]

    ongeki_versions_date = [
        datetime.date(2018, 7, 26),
        datetime.date(2019, 2, 7),
        datetime.date(2019, 8, 22),
        datetime.date(2020, 2, 20),
        datetime.date(2020, 9, 30),
        datetime.date(2021, 3, 31),
        datetime.date(2021, 10, 21),
        datetime.date(2022, 3, 3),
        datetime.date(2022, 8, 4),
        datetime.date(2024, 3, 7),
        datetime.date(9999, 12, 31),
    ]

    for i in range(len(ongeki_versions)):
        if ongeki_versions_date[i] <= d < ongeki_versions_date[i + 1]:
            return ongeki_versions[i]


# OngekiScoreLogのプレイヤーデータを取得する
def get_ongeki_score_log_player_data(user_id: str) -> tuple:

    # CONST_URL = "https://reiwa.f5.si/ongeki_const_all.json"
    ALL_URL = "https://natua.pythonanywhere.com/my_apps/songdata_ongeki.json"
    MUSIC_ID_PATTERN = re.compile(r'href="(.*?)"')

    # 定数情報の取得を辞書化
    # r_const = requests.get(CONST_URL)
    # r_const.encoding = r_const.apparent_encoding
    # ongeki_const_json = {d["music_id"]: d for d in r_const.json()}

    # 基本情報の取得を辞書化
    r_all = requests.get(ALL_URL)
    r_all.encoding = r_all.apparent_encoding
    ongeki_all = [
         m
        for m in r_all.json()["songs"]
        if not (m["meta"]["name"] == "Perfect Shining!!" and m["lunatic"]["const"] == 0) # Perfect Shining!![LUN0]を除外
    ]

    # -------------------------

    # OngekiScoreLogにrequest
    url = f"https://ongeki-score.net/user/{user_id}/technical?archive=1"
    r = requests.get(url)

    # 解析
    soup = BeautifulSoup(r.text, "lxml")

    # -------------------------

    # プロフィール文字列
    profiles = soup.find(class_="table").tbody.contents

    player_data = {
        "name": profiles[1].td.text,
        "trophy": profiles[3].td.text,
        "level": int(profiles[5].td.text),
        "battle_point": int(profiles[7].td.text),
        "rating": float(profiles[9].td.text.split()[0]),
        "max_rating": float(profiles[9].td.text.split()[-1][:-1]),
        "money": int(profiles[11].td.text.split()[0]),
        "money_total": int(profiles[11].td.text.split()[-1][:-1]),
        "total_play": int(profiles[13].td.text),
        "comment": profiles[15].td.text,
        "is_premium": bool(soup.find(class_="net-premium")),
        "is_developer": bool(soup.find(class_="developer")),
    }

    # -------------------------

    # レコード
    records_raw = soup.find(class_="list").children
    records_data_list = []
    invalid_music_list = []

    for r in records_raw:

        # 空の場合は次へ
        if r == "\n":
            continue


        # 楽曲情報を取得
        music_title: str = list(r.contents[1].descendants)[1].text
        music_diff: str = r.contents[25].text.upper()

        # OngekiScoreLog楽曲IDを取得
        match_result = MUSIC_ID_PATTERN.search(str(list(r.contents[1].descendants)[2]))
        if not match_result:
            raise ValueError(f"[ongeki_op][error] OngekiScoreLog楽曲IDが不明です title:{music_title}")
        music_id = int(match_result.group(1).split("/")[-2])

        music_data = None

        # Singularity問題
        if music_title == "Singularity":
            match music_id:
                case 362:
                    music_artist = "technoplanet"
                case 425:
                    music_artist = "ETIA.「Arcaea」"
                case 487:
                    music_artist = "SEGA SOUND STAFF「セガNET麻雀 MJ」"
                case _:
                    raise ValueError(f"[ongeki_op][error] Singularityのアーティストが不明です music_id:{music_id}")


            for m in ongeki_all:
                if m["meta"]["name"] == music_title and m["meta"]["artist"] == music_artist:
                    # print(f'{m["meta"]["name"]} / {m["meta"]["artist"]}')
                    music_data = m
                    break
            # print(music_data)

        else:
            # 楽曲データベースを曲名で検索
            for m in ongeki_all:
                if m["meta"]["name"] == music_title:
                    music_data = m
                    break

        # 楽曲データが見つからない場合
        if not music_data:
            # print(f"[ongeki_op][warning] 楽曲DBにデータないぞ title:{music_title}")
            invalid_music_list.append(music_title)
            continue

        # record_dataを作成
        lamp_key = int(r.contents[7].text)
        record_data = {
            "id": music_id,
            "title": music_title,
            "artist": music_data["meta"]["artist"],
            "difficulty": music_diff,
            "level": r.contents[5].text,
            "const": music_data[music_diff.lower()]["const"],
            "category": music_data["meta"]["genre"],
            "is_const_unknown": music_data[music_diff.lower()]["const_nodata"],
            "is_bonus": music_data["meta"]["is_bonus"],
            "score_rank": r.contents[21].text,
            "t-score": int(list(r.contents[11].descendants)[1].text),
            "is_AB": lamp_key in [4, 5],
            "is_FC": lamp_key in [2, 3, 4, 5],
            "is_FB": lamp_key in [1, 3, 5],
            "version": (
                music_data["meta"]["release_lunatic_version"]
                if music_diff.lower()[0] == "l"
                else music_data["meta"]["release_version"]
            )[5:],
        }

        try:
            record_data["music_rate_old"] = calc_music_rate_old(record_data["score_rank"], record_data["t-score"], record_data["const"])
        except Exception as e:
            print(
                f"[ongeki_op][error] 旧計算式 単曲レート計算に失敗: {str(e)} | {music_title} Rank {record_data['score_rank']} {record_data['t-score']} {record_data['const']}"
            )
            # record_data["music_rate"] = 0

        try:
            record_data["music_rate"] = calc_music_rate(record_data["score_rank"], record_data["t-score"], record_data["const"], record_data["is_FC"], record_data["is_AB"], record_data["is_FB"])
        except Exception as e:
            print(
                f"[ongeki_op][error] 新計算式 単曲レート計算に失敗: {str(e)} | {music_title} Rank {record_data['score_rank']} {record_data['t-score']} {record_data['const']}"
            )
            # record_data["music_rate"] = 0

        # 追加日
        # d = music_data["meta"]["release"].replace("-", "")
        # record_data["version"] = date2ongekiversion(
        #     (datetime.datetime.strptime(d, "%Y%m%d") - datetime.timedelta(hours=9)).isoformat() + "Z"
        # )
        # if record_data["difficulty"] == "LUNATIC":
        #     d = music_data["meta"]["release"].replace("-", "")
        #     record_data["version"] = date2ongekiversion(
        #         (datetime.datetime.strptime(d, "%Y%m%d") - datetime.timedelta(hours=9)).isoformat() + "Z"
        #     )
        # else:
        #     record_data["version"] = date2ongekiversion(music_const_data["add_date"])

        records_data_list.append(record_data)

    return player_data, records_data_list, invalid_music_list


if __name__ == "__main__":
    # p, r, _ = get_ongeki_score_log_player_data("5216")
    pass
