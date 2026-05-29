from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('manage-rag/', admin.site.urls),
    path('', include('apps.knowledge.urls')),
    path('', include('apps.experiment.urls')),
]
