from rest_framework.routers import DefaultRouter
from .viewsets import EstoqueViewSet, LojaViewSet, PedidoViewSet, ItemPedidoViewSet, ProdutoViewSet, UsuarioViewSet, NotificacaoViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet)
router.register(r'itens-pedido', ItemPedidoViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'lojas', LojaViewSet)
router.register(r'estoque', EstoqueViewSet)
router.register(r'user', UsuarioViewSet)
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacoes')

urlpatterns = router.urls
