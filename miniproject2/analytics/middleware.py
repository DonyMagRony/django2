from datetime import datetime
from .models import ApiRequestLog

class ApiRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ApiRequestLog.objects.create(
                user=request.user,
                endpoint=request.path,
                method=request.method,
                request_time=datetime.now()
            )
        response = self.get_response(request)
        return response
