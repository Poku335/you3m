from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.static import serve
import os

def api_info(request):
    return JsonResponse({
        'message': 'YouTube to MP3 Converter API',
        'version': '1.0',
        'endpoints': {
            'convert': '/api/convert/',
            'status': '/api/status/<task_id>/',
            'download': '/api/download/<task_id>/',
            'tasks': '/api/tasks/',
        }
    })

class ReactAppView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            with open(os.path.join(settings.BASE_DIR, 'static', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return JsonResponse({
                'message': 'React app not found. Please build the frontend first.',
                'api_info': 'API is available at /api/'
            })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('converter.urls')),
    path('api-info/', api_info, name='api_info'),
]

# Serve React app for all other routes
if not settings.DEBUG:
    from django.http import HttpResponse
    urlpatterns += [
        re_path(r'^.*$', ReactAppView.as_view(), name='react_app'),
    ]
else:
    urlpatterns += [
        path('', api_info, name='api_info'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)