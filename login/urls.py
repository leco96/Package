from rest_framework import routers
from .views import UserViewSet, TokenBlacklisted

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet, basename="my_users")
routers.register(r'blackList', TokenBlacklisted, basename='blacklist_token')






