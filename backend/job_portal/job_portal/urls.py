from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Job Portal Admin Panel"



urlpatterns = [
    path("admin/", admin.site.urls),
    path("job/", include("job.urls")),
    path("mainapp/", include("mainapp.urls")),
    path("frontend/", include("frontend.urls"))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)