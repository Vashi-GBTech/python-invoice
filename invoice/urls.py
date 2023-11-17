from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views import UserViewSet, GroupViewSet  # Adjust the import based on your project structure

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
