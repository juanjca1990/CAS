
from django.contrib import admin
from django.urls import include, path

from socios import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.lista_socios,name="lista_socios"),
    path('socios/', include('socios.urls')),
]