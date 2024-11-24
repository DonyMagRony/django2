from .models import APIRequestLog

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            APIRequestLog.objects.using('analytics').create(
                user=request.user,
                endpoint=request.path,
            )
        return self.get_response(request)
