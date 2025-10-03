import csv
import os
import unicodedata
import re
import pprint
from datetime import datetime
from pathlib import Path
from .yumesute_ocr import yumesute_ocr


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# TODO ジャケット下部や「ORIGINAL」表示が拾われることがある

# """仕様"""一覧
# 難易度変更時のエフェクトで見えなくなる問題がある
# IVがIになることがある
# 星章の読み取りバリデート未対応
# ロングバージョン非対応
# アスペクト比2360x1640以外非対応
# 曲名の読み取りが曖昧な場合はカッコを付ける

# 130曲で25分

ACCEPT_THRESHOLD = 0.595  # これ以下かつギャップ大なら自動受理
GAP_THRESHOLD = 0.20  # top2 - top1 がこれ以上ならギャップあり（確定しやすい）


def normalize_text(s: str) -> str:
    if s is None:
        return ""
    # NFKC 正規化、前後空白削除、連続空白を単一に
    s = unicodedata.normalize("NFKC", s).strip()
    s = re.sub(r"\s+", " ", s)
    # 任意で追加正規化ルール（半角チルダ→波ダッシュ等）はここに追加
    return s


def meaningful_char_count(s: str) -> int:
    # 文字カテゴリが Letter または Number のものを「意味ある文字」とする
    cnt = 0
    for ch in s:
        cat = unicodedata.category(ch)
        if cat and cat[0] in ("L", "N"):
            cnt += 1
    return cnt


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            ins = current[j - 1] + 1
            dele = previous[j] + 1
            sub = previous[j - 1] + (0 if ca == cb else 1)
            current.append(min(ins, dele, sub))
        previous = current
    return previous[-1]


def compute_normalized_distance(a: str, b: str) -> float:
    mlen = max(len(a), len(b))
    if mlen == 0:
        return 0.0
    return levenshtein(a, b) / mlen


def find_top2_and_decide(raw_target: str, song_name_list_orig: list):
    target_norm = normalize_text(raw_target)
    distances = []
    for cand in song_name_list_orig:
        cand_norm = normalize_text(cand)
        dn = compute_normalized_distance(target_norm, cand_norm)
        distances.append((cand, cand_norm, dn))
    distances.sort(key=lambda x: x[2])
    top1 = distances[0]
    top2 = distances[1] if len(distances) > 1 else None
    dn1 = top1[2]
    dn2 = top2[2] if top2 is not None else None
    gap = (dn2 - dn1) if dn2 is not None else None

    accepted = dn1 <= ACCEPT_THRESHOLD and (gap is not None and gap >= GAP_THRESHOLD)
    return top1[0], accepted


def load_song_name_list(file_path):
    """
    曲名リストをファイルから読み込む関数
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def edit_distance(str1, str2):
    """
    2つの文字列の編集距離（レーベンシュタイン距離）を計算する
    """
    m, n = len(str1), len(str2)

    # DPテーブルを初期化
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 基本ケース：空文字列からの変換
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # DPテーブルを埋める
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # 文字が同じなら操作不要
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])  # 削除  # 挿入  # 置換

    return dp[m][n]


def find_closest_song_name(target_song_name, song_name_list):
    """
    編集距離を使って最も近い曲名を探す
    """
    min_distance = float("inf")
    closest_song_name = target_song_name

    for song_name in song_name_list:
        distance = edit_distance(target_song_name, song_name)
        if distance < min_distance:
            min_distance = distance
            closest_song_name = song_name

    # print(f"{min_distance}\t{closest_song_name}")
    return closest_song_name


def run_ocr(video_path,filename_uuid):

    # OCR実行
    score_data_list = yumesute_ocr(video_path)

    # 正しい曲名に置換する
    song_name_list = load_song_name_list(os.path.join(BASE_DIR, "my_apps", "my_script", "yumesute_ocr", "song_name_list.txt"))
    for d in score_data_list:
        raw = d.get("song_name", "")
        d["song_name_raw"] = raw  # 元の OCR 文字列を保存
        top1_name, accepted = find_top2_and_decide(raw, song_name_list)
        if accepted:
            d["song_name"] = top1_name
        else:
            d["song_name"] = f"({top1_name})"

    pprint.pprint(score_data_list)

    # song_nameとdifficultyをキーとして重複削除
    unique_dict = {}
    for d in score_data_list:
        key = (d["song_name"], d["difficulty"])
        if (key not in unique_dict) and (d["song_name"] != "") and (d["difficulty"] is not None):
            unique_dict[key] = d
    score_data_list = list(unique_dict.values())

    # CSVに保存（ヘッダーのみ日本語に変更）
    csv_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "csvs")
    os.makedirs(csv_dir, exist_ok=True)
    now_str = datetime.now().strftime("%Y%m%d%H%M")
    csv_filename = f"{now_str}_{filename_uuid}.csv"
    csv_path = os.path.join(csv_dir, csv_filename)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        # キー名はそのまま、ヘッダーのみ日本語
        fieldnames = ["song_name", "song_name_raw", "difficulty", "level", "level_list", "score", "rate"]
        header = {
            "song_name": "曲名",
            "song_name_raw": "曲名(OCR読み取り結果のまま)",
            "difficulty": "難易度",
            "level": "レベル",
            "level_list": "各難易度のレベル",
            "score": "スコア",
            "rate": "レート/星章",
        }
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(header)
        for d in score_data_list:
            writer.writerow(d)

    return csv_filename, csv_path, filename_uuid


if __name__ == "__main__":
    print(BASE_DIR)
