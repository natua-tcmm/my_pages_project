from django.shortcuts import render, redirect
from django.conf import settings
from pathlib import Path
import os
import uuid
from ..forms import YumesuteOcrVideoForm
from ..my_script.yumesute_ocr.run_ocr import run_ocr

BASE_DIR = Path(__file__).resolve().parent.parent.parent
title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# ユメステOCR(β版)
def yumesute_ocr(request):
    message = None
    video_url = None

    if request.method == "POST":
        form = YumesuteOcrVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data["video"]
            # 保存先ディレクトリ
            save_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "videos")
            os.makedirs(save_dir, exist_ok=True)
            # ファイル名重複回避
            filename_uuid = str(uuid.uuid4())
            video_path = os.path.join(save_dir, filename_uuid)
            with open(video_path, "wb+") as destination:
                for chunk in video.chunks():
                    destination.write(chunk)
            message = "アップロードが完了しました。"

            # OCR実行
            csv_filename, csv_path, filename_uuid = run_ocr(video_path, filename_uuid)
            print(csv_filename, csv_path, filename_uuid)

            # 動画データを削除
            if os.path.exists(video_path):
                os.remove(video_path)

        else:
            message = "アップロードに失敗しました：" + "; ".join([str(e) for e in form.errors.values()])
    else:
        form = YumesuteOcrVideoForm()

    context = {
        "title": f"ユメステOCR(β版) {title_base}",
        "is_beta": True,
        "is_app": True,
        "form": form,
        "message": message,
        "video_url": video_url,
    }
    return render(request, "yumesute_ocr/yumesute_ocr.html", context=context)
