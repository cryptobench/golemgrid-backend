
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        jwt = {}
        jwt['refresh_token'] = str(refresh)
        jwt['access_token'] = str(refresh.access_token)

        # Add extra responses here
        jwt['user'] = {'username': self.user.username, "email": self.user.email,
                       "first_name": self.user.first_name, "last_name": self.user.last_name}
        return jwt


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
