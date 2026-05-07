from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .serializers import LoginSerializer, UserSerializer

from rest_framework import viewsets, filters
from apps.authentication.permissions import IsAdmin
from .models import User
from .serializers import CreateUserSerializer


class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer},
        description="Connexion utilisateur avec email et mot de passe. Retourne access token, refresh token et infos utilisateur.",
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        description="Retourne les informations de l'utilisateur connecté.",
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related(
        "teacher_profile",
        "student_profile",
    ).all()

    permission_classes = [IsAdmin]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "email",
        "role",
        "teacher_profile__first_name",
        "teacher_profile__last_name",
        "student_profile__first_name",
        "student_profile__last_name",
    ]
    ordering_fields = ["email", "role", "created_at"]
    ordering = ["email"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer