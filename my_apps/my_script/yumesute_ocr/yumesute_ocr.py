import cv2
import numpy as np
import easyocr
from skimage.metrics import structural_similarity as ssim
from decimal import Decimal, ROUND_DOWN, getcontext


def ocr_image(img_cv: np.ndarray) -> dict:
    """
    画像全体にOCRを実行し、指定範囲内の文字データを抽出してdict形式で返す
    """

    # 文字データの場所の計算
    ranges_ratio = {
        "song_name": (0.67, 0.59, 0.89, 0.64),
        "level_list": (0.54, 0.75, 0.95, 0.81),
        "score": (0.56, 0.88, 0.65, 0.96),
        "rate": (0.735, 0.88, 0.83, 0.96),
    }
    height, width = img_cv.shape[:2]
    ranges = {
        label: (
            int(round(x1 * width)),
            int(round(y1 * height)),
            int(round(x2 * width)),
            int(round(y2 * height)),
        )
        for label, (x1, y1, x2, y2) in ranges_ratio.items()
    }

    # 画像全体にOCRを実行
    reader = easyocr.Reader(["en", "ja"])
    results_text = reader.readtext(img_cv, detail=1, text_threshold=0.6, low_text=0.3)
    results_levels = reader.readtext(img_cv, detail=1, text_threshold=0.5, low_text=0.3, allowlist="0123456789IVX.%")
    results_numbers = reader.readtext(img_cv, detail=1, text_threshold=0.75, low_text=0.4, allowlist="0123456789.%")

    # 結果をdictにまとめる
    score_data = {"song_name": "", "level_list": [], "score": None, "rate": None}

    # 各範囲と検出された文字を確認
    for data_type, (x_min, y_min, x_max, y_max) in ranges.items():

        match data_type:
            case "song_name":
                results = results_text
            case "level_list":
                results = results_levels
            case "score":
                results = results_numbers
            case "rate":
                results = results_numbers

        for d in results:
            x, y = d[0][0]  # 左上の座標
            # 範囲内なら...
            if x_min <= x <= x_max and y_min <= y <= y_max:
                match data_type:
                    case "song_name":
                        score_data[data_type] += d[1]
                    case "level_list":
                        score_data[data_type].append(d[1])
                    case "score":
                        score_data[data_type] = d[1]
                    case "rate":
                        score_data[data_type] = d[1]

    return score_data


def calculate_ssim(img1, img2):
    """
    2つの画像の構造的類似度（SSIM）を計算する関数
    """
    # グレースケールに変換
    gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

    # 同じサイズにリサイズ
    h, w = min(gray1.shape[0], gray2.shape[0]), min(gray1.shape[1], gray2.shape[1])
    gray1 = cv2.resize(gray1, (w, h))
    gray2 = cv2.resize(gray2, (w, h))

    # SSIM計算（-1から1の範囲、1が完全一致）
    similarity = ssim(gray1, gray2)
    return similarity


def simple_color_analysis(image, bins=32):
    """
    ヒストグラムベースの簡単な色分析
    """
    # 各チャンネルのヒストグラムを計算
    hist_r = cv2.calcHist([image], [0], None, [bins], [0, 256])
    hist_g = cv2.calcHist([image], [1], None, [bins], [0, 256])
    hist_b = cv2.calcHist([image], [2], None, [bins], [0, 256])

    # 最も多い色の範囲を取得
    max_r = np.argmax(hist_r) * (256 // bins)
    max_g = np.argmax(hist_g) * (256 // bins)
    max_b = np.argmax(hist_b) * (256 // bins)

    return (max_r, max_g, max_b)


def difficult_color_pick(image):
    """
    難易度抽出用の色分析
    入力は既にRGBに変換された画像
    """
    # 画像をトリミング
    x_min_ratio, y_min_ratio = 0.605, 0.609
    x_max_ratio, y_max_ratio = 0.889, 0.67
    size = image.shape[:2][::-1]  # (width, height)
    x_min = int(x_min_ratio * size[0])
    y_min = int(y_min_ratio * size[1])
    x_max = int(x_max_ratio * size[0])
    y_max = int(y_max_ratio * size[1])

    cropped = image[y_min:y_max, x_min:x_max]

    # トリミングした画像の色分析
    dominant_color = simple_color_analysis(cropped)
    return (int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2]))


def detect_difficulty(frame):
    # 難易度を抽出する
    difficult_color_dict = {
        "NORMAL": (0, 40, 192, 208),
        "HARD": (1, 216, 120, 16),
        "EXTRA": (2, 216, 56, 96),
        "STELLA": (3, 88, 48, 176),
        "OLIVIER": (4, 32, 24, 32),
    }
    r, g, b = difficult_color_pick(frame)
    # r,g,bが最も近い難易度名を取得
    min_dist = float("inf")
    detected_difficulty = None
    detected_difficulty_index = None
    for diff_name, (i, dr, dg, db) in difficult_color_dict.items():
        dist = (r - dr) ** 2 + (g - dg) ** 2 + (b - db) ** 2
        if dist < min_dist:
            min_dist = dist
            detected_difficulty = diff_name
            detected_difficulty_index = i

    return detected_difficulty, detected_difficulty_index


def calculate_frame_interval(fps, interval_seconds):
    """
    FPSとインターバル秒からフレーム間隔を計算する
    """
    return int(fps * interval_seconds)


def roman_to_int(roman):
    """
    ローマ数字(1〜39, IV対応)を整数に変換する
    """
    if not all(c in "IVX" for c in roman):
        raise ValueError(f"Invalid Roman numeral: {roman}")
    roman_map = {"I": 1, "V": 5, "X": 10}
    result = 0
    prev_value = 0
    for char in reversed(roman):
        value = roman_map.get(char, 0)
        if value < prev_value:
            result -= value
        else:
            result += value
            prev_value = value
    if 1 <= result <= 39:
        return result
    return None


def is_sorted_int_list(lst):
    """
    渡されたList[str]が、全要素が整数でかつ昇順に並んでいるか確認しT/Fを返す関数
    ※長さが4じゃなかったら例外
    """
    if len(lst) != 4:
        raise ValueError("List length must be 4")
    try:
        int_list = [int(x) for x in lst]
    except ValueError:
        return False
    return all(int_list[i] <= int_list[i + 1] for i in range(3))


def process_score_data(score_data, detected_difficulty):
    """
    スコアデータの処理を行う関数
    スコアとレートの変換と調整を行います
    """

    # スコアとレート
    try:
        score_data["score"] = float(score_data["score"].replace("%", ""))
    except (ValueError, TypeError):
        score_data["score"] = None
    try:
        score_data["rate"] = float(score_data["rate"])
    except (ValueError, TypeError):
        score_data["rate"] = None

    # score==0 xor rate==0 なら、もう片方を0.0にする
    if score_data["score"] == 0.0 and score_data["rate"] is None:
        score_data["rate"] = 0.0
    elif score_data["score"] is None and score_data["rate"] == 0.0:
        score_data["score"] = 0.0

    # スコアとレートの整合性を確認する
    if detected_difficulty != "OLIVIER":
        if score_data["level"] is not None:
            # レートがNoneなら、スコアからレートを計算する
            if score_data["score"] is not None and score_data["rate"] is None:
                score_data["rate"] = calculate_score2rate(score_data["level"], score_data["score"])
                print(f"Info: スコアからレートを計算しました。 {score_data['song_name']} ({score_data['difficulty']})")
            # 両方Noneでないなら、スコアからレートを計算して整合性を確認する
            elif score_data["score"] is not None and score_data["rate"] is not None:
                calculated_rate = calculate_score2rate(score_data["level"], score_data["score"])
                if abs(calculated_rate - score_data["rate"]) > 0.01:
                    print(f"Warning: スコアとレートが合いません。 {score_data['song_name']} ({score_data['difficulty']})")
                    print(f"  スコア: {score_data['score']}, レート: {score_data['rate']}, 計算されたレート: {calculated_rate}")
            # スコアがNoneならレートからスコアを計算する(逆変換の実装)
            elif score_data["score"] is None and score_data["rate"] is not None:
                score_data["score"] = calculate_rate2score(score_data["level"], score_data["rate"])
                print(f"Info: レートからスコアを計算しました。 {score_data['song_name']} ({score_data['difficulty']})")

    return score_data


def calculate_score2rate(level: int, score: float) -> float:
    """
    レベルとスコアに基づいてレートを計算する関数
    Decimalを使い、scoreは小数点以下4桁まで扱う
    """
    getcontext().prec = 8  # 十分な精度を確保

    score = Decimal(str(score)).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
    level = Decimal(str(level))

    if score < Decimal("0") or score > Decimal("101"):
        raise ValueError("スコアは0〜101の範囲でなければなりません")
    if level < Decimal("1"):
        raise ValueError("レベルは1以上でなければなりません")

    if score >= Decimal("98.0000"):
        score_alpha_table = [
            (Decimal("98.0000"), Decimal("0.00")),
            (Decimal("100.0000"), Decimal("1.50")),
            (Decimal("100.2500"), Decimal("2.25")),
            (Decimal("100.5000"), Decimal("3.00")),
            (Decimal("100.7500"), Decimal("4.50")),
            (Decimal("100.9500"), Decimal("6.00")),
            (Decimal("101.0000"), Decimal("6.05")),
        ]

        alpha = Decimal("0.00")
        if score >= Decimal("101.0000"):
            alpha = Decimal("6.05")
        else:
            for i in range(len(score_alpha_table) - 1):
                score1, alpha1 = score_alpha_table[i]
                score2, alpha2 = score_alpha_table[i + 1]
                if score1 <= score <= score2:
                    ratio = (score - score1) / (score2 - score1)
                    alpha = alpha1 + (alpha2 - alpha1) * ratio
                    break
        rate = level + alpha

    elif Decimal("95") <= score < Decimal("98"):
        rate = level * (Decimal("0.75") + (score - Decimal("95")) / Decimal("12"))

    elif Decimal("90") <= score < Decimal("95"):
        rate = level * (Decimal("0.5") + (score - Decimal("90")) / Decimal("20"))

    else:  # score < 90
        rate = level * score / Decimal("180")

    # 小数第2位まで切り捨て
    rate = rate.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    return float(rate)


def calculate_rate2score(level: int, rate: float) -> float:
    """
    レベルとレートに基づいてスコアを計算する関数（calculate_rateの逆変換）
    Decimalを使い、rateは小数点以下2桁まで扱う
    """
    getcontext().prec = 8  # 十分な精度を確保

    rate = Decimal(str(rate)).quantize(Decimal("0.01"))
    level = Decimal(str(level))

    if rate < Decimal("0"):
        raise ValueError("レートは0以上でなければなりません")
    if level < Decimal("1"):
        raise ValueError("レベルは1以上でなければなりません")

    # rate >= level + 0.00 (98%以上の範囲)
    if rate >= level:
        alpha = rate - level

        # alphaから対応するスコアを逆算
        score_alpha_table = [
            (Decimal("98.0000"), Decimal("0.00")),
            (Decimal("100.0000"), Decimal("1.50")),
            (Decimal("100.2500"), Decimal("2.25")),
            (Decimal("100.5000"), Decimal("3.00")),
            (Decimal("100.7500"), Decimal("4.50")),
            (Decimal("100.9500"), Decimal("6.00")),
            (Decimal("101.0000"), Decimal("6.05")),
        ]

        if alpha >= Decimal("6.05"):
            score = Decimal("101.0000")
        else:
            score = Decimal("98.0000")  # デフォルト値
            for i in range(len(score_alpha_table) - 1):
                score1, alpha1 = score_alpha_table[i]
                score2, alpha2 = score_alpha_table[i + 1]
                if alpha1 <= alpha <= alpha2:
                    ratio = (alpha - alpha1) / (alpha2 - alpha1)
                    score = score1 + (score2 - score1) * ratio
                    break

    # level * 0.75 <= rate < level (95% <= score < 98%)
    elif rate >= level * Decimal("0.75"):
        # rate = level * (0.75 + (score - 95) / 12)
        # rate / level = 0.75 + (score - 95) / 12
        # (rate / level - 0.75) = (score - 95) / 12
        # score = 95 + 12 * (rate / level - 0.75)
        score = Decimal("95") + Decimal("12") * (rate / level - Decimal("0.75"))

    # level * 0.5 <= rate < level * 0.75 (90% <= score < 95%)
    elif rate >= level * Decimal("0.5"):
        # rate = level * (0.5 + (score - 90) / 20)
        # rate / level = 0.5 + (score - 90) / 20
        # (rate / level - 0.5) = (score - 90) / 20
        # score = 90 + 20 * (rate / level - 0.5)
        score = Decimal("90") + Decimal("20") * (rate / level - Decimal("0.5"))

    else:  # rate < level * 0.5 (score < 90%)
        # rate = level * score / 180
        # score = 180 * rate / level
        score = Decimal("180") * rate / level

    # 小数第4位まで切り捨て（元の関数に合わせる）
    score = score.quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
    return float(score)


def should_skip_frame(frame, frame_before, detected_difficulty, detected_difficulty_before):
    """
    フレームをスキップするかどうかを判断する関数
    前フレームとの類似度と難易度を比較して判断する
    """
    if frame_before is None or detected_difficulty_before is None:
        return False

    is_same_difficulty = detected_difficulty == detected_difficulty_before

    # 前回取得した画像(右半分)との類似度を計算し、類似度が高い場合はスキップ
    _, w = frame.shape[:2]
    frame_right = frame[:, w // 2 :]
    frame_before_right = frame_before[:, w // 2 :]

    similarity = calculate_ssim(frame_before_right, frame_right)

    # 類似度が高いかつ難易度が同じ場合はスキップ
    return similarity > 0.95 and is_same_difficulty


def process_difficulty_data(score_data, detected_difficulty, detected_difficulty_index):
    """
    難易度データを整える関数
    level_listの形式チェックとレベルの変換を行う
    """
    # 難易度データを整える
    score_data["difficulty"] = detected_difficulty

    # level_listの形式チェック
    level_list = score_data["level_list"]
    valid_level_list = False
    # OLIVIER未開放: 整数4つ
    if len(level_list) == 4:
        valid_level_list = is_sorted_int_list(level_list)
    # OLIVIER開放済: 整数4つ+アルファベット1つ
    elif len(level_list) == 5:
        valid_level_list = is_sorted_int_list(level_list[:4]) and level_list[4].isalpha()

    if valid_level_list:
        # レベルを整数に変換
        try:
            # OLIVIER
            if detected_difficulty == "OLIVIER":
                if len(level_list) == 5:
                    score_data["level"] = roman_to_int(score_data["level_list"][detected_difficulty_index])
                # OCRで検出できなかった場合はNone
                else:
                    score_data["level"] = None
            # 通常難易度
            else:
                score_data["level"] = int(score_data["level_list"][detected_difficulty_index])
        except (ValueError, TypeError):
            score_data["level"] = None
    else:
        score_data["level"] = None

    return score_data


def yumesute_ocr(video_path, interval_seconds=0.1):

    # 動画を読み込む
    cap = cv2.VideoCapture(video_path)

    # 動画を右向きに90°回転
    cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 0)

    if not cap.isOpened():
        raise ValueError("動画ファイルが見つかりません。" + video_path)

    # アスペクト比を確認
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    aspect_ratio = width / height

    # 2360×1640 px
    print(f"Video resolution: {int(width)}x{int(height)}, Aspect ratio: {aspect_ratio:.2f}")
    if not (0.69 <= aspect_ratio <= 0.70):
        raise ValueError(f"動画アスペクト比が不正です: {aspect_ratio:.2f}。0.69〜0.70である必要があります。")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = calculate_frame_interval(fps, interval_seconds)

    # 初期化
    score_data_list = []
    frame_count = -1
    frame_before = None
    detected_difficulty_before = None

    try:
        while True:
            # 動画からフレームを取得
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval == 0:
                # 画像をRGBに変換して90度回転
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.rot90(frame, k=1)

                # 難易度を抽出する
                detected_difficulty, detected_difficulty_index = detect_difficulty(frame)

                # スキップ判断
                if should_skip_frame(frame, frame_before, detected_difficulty, detected_difficulty_before):
                    continue

                # OCRを実行
                frame_before = frame.copy()
                detected_difficulty_before = detected_difficulty
                score_data = ocr_image(frame)
                print(score_data)

                if score_data["song_name"] == "":
                    continue

                # 難易度データを整える
                score_data = process_difficulty_data(score_data, detected_difficulty, detected_difficulty_index)

                # スコアデータの処理
                score_data = process_score_data(score_data, detected_difficulty)

                score_data_list.append(score_data)
                print(
                    f"\033[32mDone! : {score_data['song_name']}\033[0m {score_data['difficulty']} {score_data['level']} {score_data['score']} {score_data['rate']}"
                )

    finally:
        cap.release()

    return score_data_list
