"""
URL configuration for main_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin urls
    path("admin/", admin.site.urls),
    # Djoser (JWT auth)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/", include("accounts.urls")),
    # Local apps
    path("upload/", include("image_processer.urls")),
    path("server/", include("ping.urls")),
    path("medicine/", include("medicines.urls")),
    path("medicines/", include("medicines.urls")),
    path("alarm/", include("alarm.urls")),
    path("intake/", include("intake.urls")),
    path("health/", include("health_state.urls")),
    path("", include("ping.urls")),  # Default to ping app
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
