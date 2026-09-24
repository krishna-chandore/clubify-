
from django.contrib import admin
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Clubify Administration"
admin.site.site_title = "Clubify Admin Portal"
admin.site.index_title = "Welcome to Clubify Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clubapp.urls')),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

