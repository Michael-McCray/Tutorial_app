from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
	
	url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('tutorial_app.urls')), # ADD THIS NEW TUPLE!
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


