from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    path('admin/', admin.site.urls, name='home'),
    path('', views.home_view),  # <--- Tomma citattecken betyder "startsidan"
    path('about/', views.about_view, name='about'),
    path('posts/', include(('posts.urls', 'posts'), namespace='posts')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
