from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGerenteOrAdministrador(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_superuser or
            user.groups.filter(name='Admin').exists() or
            user.groups.filter(name='Gerente').exists()
        )


class IsGerenteOrAdministradorOrResponsavel(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Leitura — qualquer usuário autenticado pode
        if request.method in SAFE_METHODS:
            return True

        # Escrita — só gerente/admin/responsavel
        return (
            user.is_superuser or
            user.groups.filter(name='Admin').exists() or
            user.groups.filter(name='Gerente').exists() or
            user.groups.filter(name='Responsavel').exists()
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Leitura — qualquer autenticado (get_queryset já filtra por loja)
        if request.method in SAFE_METHODS:
            return True

        # Gerente/admin → tudo
        if (
            user.is_superuser
            or user.groups.filter(name='Admin').exists()
            or user.groups.filter(name='Gerente').exists()
        ):
            return True

        # Responsável → só o que é dele
        if user.groups.filter(name='Responsavel').exists():
            if hasattr(obj, 'loja'):
                return user.loja_set.filter(id=obj.loja_id).exists()

            return obj.responsavel == user

        return False
