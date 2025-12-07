from django.contrib import admin
from django.urls import path, include
from . import views
from django. conf.urls. static import static
from django. conf import settings

urlpatterns = [
    path('admin/', admin.site.urls, name='home'),
    path('', views.home_view),  # <--- Tomma citattecken betyder "startsidan"
    path('about/', views.about_view, name='about'),
    path('posts/', include('posts.urls')),
    path('users/', include('users.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)