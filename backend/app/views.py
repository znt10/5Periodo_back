from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import HttpRequest, HttpResponse

from app.models import Loja
from app.relatorios.pedidos_pdf import gerar_relatorio_pedidos_pdf

User = get_user_model()

permission_classes = [IsAuthenticated]
def relatorio_pdf(request: HttpRequest,) -> HttpResponse:
    periodo = request.GET.get("periodo", "dia")
 
    if periodo not in ("dia", "semana", "mes"):
        periodo = "dia"
 
    return gerar_relatorio_pedidos_pdf(periodo)
 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import Produto


@api_view(["GET"])
def seed_produtos(request):
    dados = {
        "ESFIHAS GDE": [
            "Carne", "Frango", "Bauru", "calabresa",
            "Hamburger", "Salsicha com cheddar", "Torta de banana"
        ],
        "ESFIHAS MINI": [
            "Carne", "Frango", "Bauru", "calabresa",
            "Hamburger", "Salsicha com cheddar", "Torta de banana"
        ],
        "FOGAZZAS GDE": [
            "Presunto e Queijo", "2 Queijos", "Calabresa",
            "Frango", "Pizza", "Chocolate", "Doce de leite"
        ],
        "FOGAZZAS MINI": [
            "Presunto e Queijo", "2 Queijos", "Calabresa",
            "Frango", "Pizza", "Chocolate", "Doce de leite"
        ],

    "RECHEIOS": [
        "Açúcar+canela",
        "Bisnaga de chocolate",
        "Bisnaga doce de leite",
        "Bisnaga Beijinho",
        "Calabresa",
        "Carne",
        "Catupiry",
        "Frango",
        "Laranja",
        "Limão",
        "Massa de empada",
        "Massa Pastel",
        "Mussarela",
        "Óleo",
        "Orégano",
        "Ovo",
        "Palmito",
        "Pimenta",
        "Presunto",
        "Tomate",
    ],

    "MERCADO": [
        "Açúcar",
        "Café",
        "Detergente",
        "Leite",
        "Nescau",
        "Bombril",
        "Adoçante",
    ],

    }

    total = 0

    for categoria, produtos in dados.items():
        for nome in produtos:
            Produto.objects.get_or_create(
                nome=nome,
                categoria=categoria,
            )
            total += 1

    return Response({"message": f"{total} produtos cadastrados"})

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token nao encontrado no cookie."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
            serializer.is_valid(raise_exception=True)
            response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        access_token = response.data.get("access")
        if access_token:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                path="/",
                max_age=int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
            )

        return response


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Credenciais invalidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        group = user.groups.first()

        if group is None:
            return Response(
                {
                    "error": (
                        "Usuario sem grupo. Adicione o usuario ao grupo "
                        "Gerente ou Responsavel."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        role = group.name
        loja_vinculada = Loja.objects.filter(responsavel=user).first()

        response = Response(
            {
                "message": "Login realizado com sucesso",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "group": role,
                    "loja": {
                        "id": loja_vinculada.public_id,
                        "nome": loja_vinculada.nome_loja,
                    }
                    if loja_vinculada
                    else None,
                },
                "access": str(access),
                "refresh": str(refresh),
            }
        )

        cookie_args = {
            "httponly": True,
            "secure": not settings.DEBUG,
            "samesite": "Lax",
            "path": "/",
        }

        response.set_cookie(
            key="access_token",
            value=str(access),
            max_age=int(access.lifetime.total_seconds()),
            **cookie_args,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            max_age=int(refresh.lifetime.total_seconds()),
            **cookie_args,
        )
        response.set_cookie(
            key="role",
            value=role,
            max_age=int(refresh.lifetime.total_seconds()),
            **cookie_args,
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(csrf_exempt)
    def post(self, request):
        response = Response({"message": "Logout realizado com sucesso"})

        response.delete_cookie("access_token", path="/", samesite="Lax")
        response.delete_cookie("refresh_token", path="/", samesite="Lax")
        response.delete_cookie("role", path="/", samesite="Lax")

        return response
