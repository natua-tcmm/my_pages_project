from django.shortcuts import render,redirect
from django.conf import settings


title_base = "| △Natua♪▽のツールとか保管所"

# --------------------------------------------------

# テンプレート こいつをコピペして作ろう
def yumesute_ocr(request):
    context = {"title": f"ユメステOCR(β版) {title_base}", "is_beta": True, "is_app": True}
    return render(request, "yumesute_ocr/yumesute_ocr.html", context=context)
