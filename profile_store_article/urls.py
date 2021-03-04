from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, include


admin.site.login = staff_member_required(admin.site.login, login_url=settings.LOGIN_URL)

urlpatterns = [
    path('varbed/', admin.site.urls),

    path('', include('apps.user_profile.urls')),
    path('store/', include('apps.store.urls')),
    path('articles/', include('apps.article.urls')),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)