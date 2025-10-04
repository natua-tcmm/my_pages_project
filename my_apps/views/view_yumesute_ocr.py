from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pathlib import Path
import os
import uuid
from ..jobs import run_ocr_job
import threading

BASE_DIR = Path(__file__).resolve().parent.parent.parent
title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------


# ユメステOCR(β版)
def yumesute_ocr(request):
    message = None
    video_url = None

    context = {
        "title": f"ユメステOCR(β版) {title_base}",
        "is_beta": True,
        "is_app": True,
        "message": message,
        "video_url": video_url,
    }
    return render(request, "yumesute_ocr/yumesute_ocr.html", context=context)


@csrf_exempt
def yumesute_ocr_ajax_upload(request):
    """
    動画アップロード（Ajax）→ OCRはバックグラウンドで実行
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POSTのみ対応しています。"})

    video = request.FILES.get("video")
    if not video:
        return JsonResponse({"success": False, "error": "ファイルが選択されていません。"})

    if not video.name.lower().endswith(".mp4"):
        return JsonResponse({"success": False, "error": "mp4ファイルのみアップロードできます。"})

    if video.size > 300 * 1024 * 1024:
        return JsonResponse({"success": False, "error": "ファイルサイズは300MB以下にしてください。"})

    # 動画を保存
    save_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "videos")
    os.makedirs(save_dir, exist_ok=True)
    filename_uuid = str(uuid.uuid4())
    video_path = os.path.join(save_dir, filename_uuid)
    with open(video_path, "wb+") as destination:
        for chunk in video.chunks():
            destination.write(chunk)

    # OCRをバックグラウンドで実行（threading）
    thread = threading.Thread(target=run_ocr_job, args=(video_path, filename_uuid))
    thread.start()

    # ここですぐレスポンス返却
    return JsonResponse({"success": True, "filename_uuid": filename_uuid})


def yumesute_ocr_csv_download(request):
    """
    OCR結果のCSVダウンロード
    """
    uuid_val = request.GET.get("uuid")
    if not uuid_val:
        raise Http404("uuidが指定されていません。")
    csv_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "csvs")

    # csvファイルを検索
    csv_file = None
    for fname in os.listdir(csv_dir):
        if fname.endswith(".csv") and uuid_val in fname:
            csv_file = os.path.join(csv_dir, fname)
            break
    if not csv_file or not os.path.exists(csv_file):
        raise Http404("CSVファイルが見つかりません。")

    return FileResponse(open(csv_file, "rb"), as_attachment=True, filename=os.path.basename(csv_file))

def yumesute_ocr_check_status(request):
    """
    OCR完了状況を返すAPI（JSON）
    """
    uuid_val = request.GET.get("uuid")
    if not uuid_val:
        return JsonResponse({"ready": False, "error": "uuidが指定されていません。"})

    csv_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "csvs")
    error_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "errors")
    error_path = os.path.join(error_dir, f"{uuid_val}.error.txt")

    # エラーがあれば返す
    if os.path.exists(error_path):
        with open(error_path, "r", encoding="utf-8") as f:
            error_msg = f.read()
        return JsonResponse({"ready": False, "error": error_msg})

    # csvファイルがあれば完了
    for fname in os.listdir(csv_dir):
        if fname.endswith(".csv") and uuid_val in fname:
            return JsonResponse({"ready": True})

    # どちらもなければ未完了
    return JsonResponse({"ready": False})
