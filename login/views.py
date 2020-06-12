from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from login.serializers import PruebaSerializer, BlackListToken
from login.models import UserCustom


class TokenBlacklisted(viewsets.ViewSet):
    serializer_class = BlackListToken
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        token = RefreshToken(request.data['blackList_token'])
        userid = request.user.id
        user = UserCustom.objects.get(id=userid)
        token.for_user(user)
        token.blacklist()
        return Response(status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = UserCustom.objects.all()
    serializer_class = PruebaSerializer


