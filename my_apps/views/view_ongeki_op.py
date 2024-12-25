from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
# from django.db.models import Q
# from django.core.handlers.wsgi import WSGIRequest

from ..models import *

import requests,re,math,datetime,dateutil.parser
from collections import defaultdict
from bs4 import BeautifulSoup
from django.conf import settings

CONST_LIST = [15.9, 15.8, 15.7, 15.6, 15.5, 15.4, 15.3, 15.2, 15.1, 15,
    14.9, 14.8, 14.7, 14.6, 14.5, 14.4, 14.3, 14.2, 14.1, 14,
    13.9, 13.8, 13.7, 13.6, 13.5, 13.4, 13.3, 13.2, 13.1, 13,
    12.9, 12.8, 12.7, 12.6, 12.5, 12.4, 12.3, 12.2, 12.1, 12,
    11.9, 11.8, 11.7, 11.6, 11.5, 11.4, 11.3, 11.2, 11.1, 11,
    10.9, 10.8, 10.7, 10.6, 10.5, 10.4, 10.3, 10.2, 10.1, 10,
    9.7, 9, 8.7, 8, 7.7, 7, 6, 5, 4, 3, 2, 1, 0
]

# --------------------------------------------------

title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# オンゲキOP
def ongeki_op(request):

    context = { "title":f"オンゲキ版OVERPOWER {title_base}" ,"is_beta":False, "is_app":True }

    # Ajax処理
    if request.method=="POST":

        # メタ情報を取得
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # POSTから検索queryを取得
        post = request.POST

        # 入力情報を取得
        osl_id = post.get("osl_id")
        op_before = post.get("op_before")
        if op_before == "":
            op_before = 0
        else:
            op_before = int(float(post.get("op_before"))*10000+0.5)/10000
        display_format = int(post.get("display_format"))

        # OngekiScoreLogにrequest送る
        # TODO : invalic_music_listの情報を送り届ける
        player_data,records_data_list, _ = get_ongeki_score_log_player_data(osl_id)
        response = {"player_data":player_data,"records":records_data_list}

        # OPを計算
        op_aggregate = calc_op(response)
        op_aggregate_all = op_aggregate["ALL"]["ALL"]

        # 情報収集
        print(f"[{ip}][ongeki_op] {osl_id} / {player_data['name']} / {op_aggregate_all['op_percent_str']}")

        # 概要+ALLを描画
        op_rank = f'{op_aggregate_all["op_color"].capitalize()}{("-"+str(op_aggregate_all["op_rank"])) if op_aggregate_all["op_color"]!="rainbow" else ""}'
        op_rank_bool = bool(op_aggregate_all["op_color"]!="")
        op_diff = max( int((op_aggregate_all['op_percent']-op_before)*10000+0.5)/10000, 0)

        tweet_text = f'{player_data["name"]}さんのO.N.G.E.K.I. POWER\n{op_aggregate_all["op_percent_str"]}'
        if op_rank_bool:
            tweet_text += f' 【{op_rank}】'
        tweet_text += "\n"
        if op_diff!=0:
            tweet_text += f'前回からの更新差分: +{op_diff}%\n'
        tweet_text += "\n"

        c = {
            "oslid":int(osl_id),
            "op_p_int":op_aggregate_all["op_percent_str"].split(".")[0],
            "op_p_dec":op_aggregate_all["op_percent_str"].split(".")[1][:-1],
            "op":f'{op_aggregate_all["op"]:.4f}',
            "op_diff":op_diff,
            "op_max":f'{op_aggregate_all["op_max"]:.4f}',
            "op_rank_bool":op_rank_bool,
            "op_rank":op_rank,
            "player_name":player_data["name"],
            "rating":player_data["rating"],
            "max_rating":player_data["max_rating"],
            "pc_class":f'pc-{op_aggregate_all["op_color"]}',
            "is_developer":player_data["is_developer"],
            "is_premium":player_data["is_premium"],
            "tweet_text": tweet_text,
            "op_card_all":rendar_op_card("ALL","ALL",op_aggregate["ALL"]["ALL"],is_display_fb=(display_format!=1))
        }
        op_summary_html = render_to_string("ongeki_op/op_summary.html",context=c)

        # カードを描画
        op_card_all_html = ""
        for category_outer in op_aggregate.keys():
            if category_outer == "ALL":
                continue
            for category_inner in op_aggregate[category_outer].keys():
                op_aggr_cat = op_aggregate[category_outer][category_inner]
                op_card_all_html += rendar_op_card(category_inner,category_outer,op_aggr_cat,is_display_fb=(display_format!=1))

        # お返しする
        ajax_response = { "op_summary_html":op_summary_html, "op_card_html":op_card_all_html, "op_new":op_aggregate_all['op_percent'] }
        return JsonResponse(ajax_response)

    return render(request, 'ongeki_op/ongeki_op.html',context=context)


# --------------------------------------------------

# 単曲レート計算
def calc_music_rate( score_rank:str, t_score:int, const:float )->float:

    music_rate = 0

    if score_rank == "SSS+" or score_rank == "AB+":
        music_rate = const + 2
    elif score_rank == "SSS":
        music_rate = const + 1.5 + math.floor((t_score-1_000_000)/150)*0.01
    elif score_rank == "SS":
        music_rate = const + 1 + math.floor((t_score-990_000)/200)*0.01
    elif score_rank == "S":
        music_rate = const + 0 + math.floor((t_score-970_000)/200)*0.01
    elif score_rank == "AAA" or score_rank == "AA":
        music_rate = const - 4 + math.floor((t_score-900_000)/175)*0.01

    music_rate = int(music_rate*100+0.5)/100

    return music_rate

# オンゲキのバージョンを求める
def date2ongekiversion(t:str) -> str:
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
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
        datetime.date(2018,7,26),
        datetime.date(2019,2,7),
        datetime.date(2019,8,22),
        datetime.date(2020,2,20),
        datetime.date(2020,9,30),
        datetime.date(2021,3,31),
        datetime.date(2021,10,21),
        datetime.date(2022,3,3),
        datetime.date(2022,8,4),
        datetime.date(2024,3,7),
        datetime.date(9999,12,31),
    ]

    for i in range(len(ongeki_versions)):
        if ongeki_versions_date[i] <= d < ongeki_versions_date[i+1]:
            return ongeki_versions[i]



def get_ongeki_score_log_player_data(user_id: str) -> tuple:

    CONST_URL = "https://reiwa.f5.si/ongeki_const_all.json"
    ALL_URL = "https://reiwa.f5.si/ongeki_all.json"
    MUSIC_ID_PATTERN = re.compile(r'href="(.*?)"')

    # 定数情報の取得を辞書化
    r_const = requests.get(CONST_URL)
    r_const.encoding = r_const.apparent_encoding
    ongeki_const_json = {d["music_id"]: d for d in r_const.json()}

    # 基本情報の取得を辞書化
    r_all = requests.get(ALL_URL)
    r_all.encoding = r_all.apparent_encoding
    ongeki_all_json = {m["meta"]["title"]: m for m in r_all.json()}

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

        # 楽曲IDを取得
        match = MUSIC_ID_PATTERN.search(str(list(r.contents[1].descendants)[2]))
        if not match:
            print("[ongeki_op][warning] 楽曲ID取得時に見つからんかったぞ")
            continue
        music_id = int(match.group(1).split("/")[-2])

        music_const_data = ongeki_const_json.get(music_id)
        if not music_const_data:
            print(f"[ongeki_op][warning] 楽曲ID {music_id} が見つかりません")
            continue

        music_title = list(r.contents[1].descendants)[1].text
        music_diff = r.contents[25].text.upper()

        # 基本情報を検索
        music_all_data = ongeki_all_json.get(music_title)
        if not music_all_data:
            print(f"[ongeki_op][warning] all_jsonの検索結果が0件やぞ title:{music_title} id:{music_id}")
            invalid_music_list.append(music_title)
            continue

        # 入れ物
        record_data = {
            "id": music_id,
            "title": music_title,
            "artist": music_const_data["artist"],
            "difficulty": music_diff,
            "level": r.contents[5].text,
            "const": music_const_data[music_diff.lower()]["const"],
            "category": music_const_data["category"],
            "is_const_unknown": music_const_data[music_diff.lower()]["is_unknown"],
            "is_bonus": "ソロ" in music_title,
            "score_rank": r.contents[21].text,
            "t-score": int(list(r.contents[11].descendants)[1].text),
        }

        # 追加日(LUNはLUN追加日)
        if record_data["difficulty"] == "LUNATIC":
            d = music_all_data["meta"]["release"].replace("-", "")
            record_data["version"] = date2ongekiversion(
                (datetime.datetime.strptime(d, "%Y%m%d") - datetime.timedelta(hours=9)).isoformat() + "Z"
            )
        else:
            record_data["version"] = date2ongekiversion(music_const_data["add_date"])

        lamp_key = int(r.contents[7].text)

        record_data["is_AB"] = lamp_key in [4, 5]
        record_data["is_FC"] = lamp_key in [2, 3, 4, 5]
        record_data["is_FB"] = lamp_key in [1, 3, 5]

        record_data["music_rate"] = calc_music_rate(record_data["score_rank"], record_data["t-score"], record_data["const"])

        records_data_list.append(record_data)

    return player_data, records_data_list, invalid_music_list




# OP計算
def calc_op(response):

    # MASTERに絞り込み・単曲OPを計算
    records = response["records"]
    records_master = []
    for r in records:
        if r["difficulty"] != "MASTER" or r["is_bonus"]:
            continue
        if r["score_rank"] == "AB+":
            r["music_op"] = (r["const"] + 3) * 5
        else:
            lump_op = 0.5 * r["is_FC"] + 0.5 * r["is_AB"]
            r["music_op"] = min(r["const"] + 2, r["music_rate"]) * 5 + lump_op + max(0, (r["t-score"] - 1007500) * 0.0015)
        r["music_op_max"] = (r["const"] + 3) * 5
        records_master.append(r)

    # 仕分け
    keys = ["level", "category", "version", "const"]
    opkey_list = [
        ["11", "11+", "12", "12+", "13", "13+", "14", "14+", "15", "15+"],
        ["POPS＆ANIME", "niconico", "東方Project", "VARIETY", "チュウマイ", "オンゲキ"],
        [
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
        ],
        [str(c) for c in CONST_LIST][::-1],
    ]

    # OP集計
    op_aggregate = {}
    op_aggregate["ALL"] = { "ALL": aggr_op(records_master)}
    for n, key in enumerate(keys):
        records_master_divided = defaultdict(list)
        for r in records_master:
            records_master_divided[str(r[key])].append(r)
        opkey = opkey_list[n]

        op_aggregate[key] = {}

        for k in opkey:
            records_master_one_division = records_master_divided.get(k)
            if records_master_one_division:
                op_tmp = aggr_op(records_master_one_division)
                op_aggregate[key][k] = op_tmp

    return op_aggregate


# OP集計
def aggr_op(records):

    music_count = len(records)
    op = sum(r["music_op"] for r in records)
    op_max = sum(r["music_op_max"] for r in records)

    ranks = {"MAX": 0, "SSS+": 0, "SSS": 0, "SS": 0, "S": 0, "others": 0}
    lumps = {"AB+": 0, "AB": 0, "FC": 0, "others": 0}
    bells = {"FB": 0, "others": 0}

    for r in records:
        rank = r["score_rank"]
        if rank == "AB+":
            ranks["MAX"] += 1
            lumps["AB+"] += 1
        else:
            ranks[r.get("score_rank", "others")] = ranks.get(r.get("score_rank", "others"), 0) + 1
            if r.get("is_AB"):
                lumps["AB"] += 1
            elif r.get("is_FC"):
                lumps["FC"] += 1
            else:
                lumps["others"] += 1

        if r.get("is_FB"):
            bells["FB"] += 1
        else:
            bells["others"] += 1

    op_color_dict = {
        "rainbow": 99.6,
        "platinum3": 99.2,
        "platinum2": 98.8,
        "platinum1": 98.5,
        "gold3": 98.0,
        "gold2": 97.5,
        "gold1": 97.0,
        "silver3": 96.5,
        "silver2": 96.0,
        "silver1": 95.5,
        "bronze3": 95.0,
        "bronze2": 94.0,
        "bronze1": 93.0,
    }

    op_percent = (op * 100) / op_max if op_max != 0 else 0
    op_color = ""
    op_rank = 0

    for op_color_name, op_color_border in op_color_dict.items():
        if op_percent >= op_color_border:
            if op_color_name == "rainbow":
                op_color = op_color_name
            else:
                op_color = op_color_name[:-1]
                op_rank = int(op_color_name[-1])
            break

    op_tmp = {
        "op": round(op, 4),
        "op_max": round(op_max, 4),
        "op_percent": round(op_percent, 4),
        "op_percent_str": f"{op_percent:.4f}%",
        "op_color": op_color,
        "op_rank": op_rank,
        "ranks": ranks,
        "lumps": lumps,
        "bells": bells,
        "music_count": music_count,
    }

    return op_tmp

# カードのhtmlをレンダリング
def rendar_op_card( category_inner:str, category_outer:str, op_aggr_cat:dict, is_display_fb:bool ) -> str:

    c = {
        "category_outer":category_outer,
        "category_inner":category_inner,
        "op_percent_str":op_aggr_cat["op_percent_str"],
        "op":f'{op_aggr_cat["op"]:.2f}',
        "op_max":f'{op_aggr_cat["op_max"]:.2f}',

        "rank_max":op_aggr_cat["ranks"]["MAX"],
        "rank_sssp":op_aggr_cat["ranks"]["SSS+"],
        "rank_sss":op_aggr_cat["ranks"]["SSS"],
        "rank_ss":op_aggr_cat["ranks"]["SS"],
        "rank_s":op_aggr_cat["ranks"]["S"],
        "rank_others":op_aggr_cat["ranks"]["others"],

        "rank_max_r":op_aggr_cat["ranks"]["MAX"]*100/op_aggr_cat["music_count"],
        "rank_sssp_r":(op_aggr_cat["ranks"]["SSS+"]+op_aggr_cat["ranks"]["MAX"])*100/op_aggr_cat["music_count"],
        "rank_sss_r":(op_aggr_cat["ranks"]["SSS"]+op_aggr_cat["ranks"]["SSS+"]+op_aggr_cat["ranks"]["MAX"])*100/op_aggr_cat["music_count"],
        "rank_ss_r":(op_aggr_cat["ranks"]["SS"]+op_aggr_cat["ranks"]["SSS"]+op_aggr_cat["ranks"]["SSS+"]+op_aggr_cat["ranks"]["MAX"])*100/op_aggr_cat["music_count"],
        "rank_s_r":(op_aggr_cat["ranks"]["S"]+op_aggr_cat["ranks"]["SS"]+op_aggr_cat["ranks"]["SSS"]+op_aggr_cat["ranks"]["SSS+"]+op_aggr_cat["ranks"]["MAX"])*100/op_aggr_cat["music_count"],

        "lump_abp":op_aggr_cat["lumps"]["AB+"],
        "lump_ab":op_aggr_cat["lumps"]["AB"],
        "lump_fc":op_aggr_cat["lumps"]["FC"],
        "lump_others":op_aggr_cat["lumps"]["others"],

        "lump_abp_r":op_aggr_cat["lumps"]["AB+"]*100/op_aggr_cat["music_count"],
        "lump_ab_r":(op_aggr_cat["lumps"]["AB"]+op_aggr_cat["lumps"]["AB+"])*100/op_aggr_cat["music_count"],
        "lump_fc_r":(op_aggr_cat["lumps"]["FC"]+op_aggr_cat["lumps"]["AB"]+op_aggr_cat["lumps"]["AB+"])*100/op_aggr_cat["music_count"],

        "bell_fb":op_aggr_cat["bells"]["FB"],
        "bell_others":op_aggr_cat["bells"]["others"],

        "bell_fb_r":op_aggr_cat["bells"]["FB"]*100/op_aggr_cat["music_count"],

        "is_display_fb":is_display_fb,

    }

    op_card_html = render_to_string("ongeki_op/op_card.html",context=c)

    return op_card_html
