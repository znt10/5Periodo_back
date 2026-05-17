from rest_framework.exceptions import PermissionDenied


class BaseMixin:
    def is_admin(self, user):
        return user.is_superuser or user.groups.filter(name='Gerente').exists()


class ResponsavelOuAdminMixin(BaseMixin):

    def get_queryset(self):
        user = self.request.user

        if self.is_admin(user):
            return super().get_queryset()

        return super().get_queryset().filter(responsavel=user)

    def perform_update(self, serializer):
        user = self.request.user

        if not self.is_admin(user):
            if serializer.instance.responsavel != user:
                raise PermissionDenied("Você só pode editar o que é seu")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if not self.is_admin(user):
            if instance.responsavel != user:
                raise PermissionDenied("Você só pode deletar o que é seu")

        instance.delete()

class UserOuAdminMixin(BaseMixin):

    def get_queryset(self):
        user = self.request.user

        if self.is_admin(user):
            return super().get_queryset()

        return super().get_queryset().filter(id=user.id)
    
    
class ApenasAdminPodeCriarMixin(BaseMixin):

    def perform_create(self, serializer):
        user = self.request.user

        if not self.is_admin(user):
            raise PermissionDenied("Apenas gerente/admin pode criar")

        serializer.save()