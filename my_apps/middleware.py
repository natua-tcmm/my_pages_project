from .models import *

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 静的ファイルなど不要なリクエストは除外
        if not request.path.startswith('/static/'):
            PageViewManager.add_log(request)
        response = self.get_response(request)
        return response
