from django.contrib import admin
from django.urls import path

from mix import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),  # <--- Tomma citattecken betyder "startsidan"
    path('/about/', views.about_view, name='about'),
]
