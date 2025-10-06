from .models import *

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ここでログを記録する
        def should_count_access(path):
            if not path.startswith('/my_apps/') or path.startswith('/my_apps/api/'):
                return False
            if path.startswith('/my_apps/yumesute_ocr'):
                return path == '/my_apps/yumesute_ocr'
            return True

        if should_count_access(request.path):
            PageViewManager.add_log(request)
        response = self.get_response(request)
        return response
