from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
import os
from ..forms import YumesuteOcrVideoForm


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
            save_dir = os.path.join(settings.MEDIA_ROOT, "yumesute_ocr", "videos")
            os.makedirs(save_dir, exist_ok=True)
            # ファイル名重複回避
            filename = timezone.now().strftime("%Y%m%d%H%M%S") + "_" + video.name
            save_path = os.path.join(save_dir, filename)
            with open(save_path, "wb+") as destination:
                for chunk in video.chunks():
                    destination.write(chunk)
            video_url = settings.MEDIA_URL + f"yumesute_ocr/videos/{filename}"
            message = "アップロードが完了しました。"
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
