from django.test import TestCase
from django.contrib.auth.models import User, Group,Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Loja, Produto, Pedido, ItemPedido, Estoque, Notificacao
from app.notifications import notificar_estoque_baixo
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.urls import reverse


from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth.models import User, Group
from app.models import Loja


class PedidoAPITestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Criar grupos
        self.grupo_responsavel, _ = Group.objects.get_or_create(name='Responsavel')
        self.grupo_gerente, _ = Group.objects.get_or_create(name='Gerente')

        # Usuário responsável
        self.responsavel = User.objects.create_user(
            username='teste',
            password='123'
        )
        self.responsavel.groups.add(self.grupo_responsavel)

        # Usuário gerente
        self.gerente = User.objects.create_user(
            username='admin',
            password='123'
        )
        self.gerente.groups.add(self.grupo_gerente)

    
        self.produto = Produto.objects.create(
            nome_produto="coxinha",
            unidade_medida="QUILO",
            categoria="SALGADOS_GDE",
        )
        # Loja
        self.loja = Loja.objects.create(
            nome_loja='Loja A',
            endereco='Rua 1',
            responsavel=self.responsavel
        )



    def test_registro_e_login(self):

        self.client.post("/login/", {
            "email": "admin",
            "password": "123"
            })
        
    # registra
        self.client.post("/api/v1/user/registrar/", {
            "email": "novo@email.com",
            "password": "123456",
            "tipo_usuario": "responsavel"
        })


        self.client.post("/logout/")
        # login
        response = self.client.post("/login/", {
            "email": "novo@email.com",
            "password": "123456"
        })

        self.assertEqual(response.status_code, 200)




    

    def test_login_sucesso(self):
        url = "/login/"

        data = {
            "email": "teste",
            "password": "123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)

        # valida cookies JWT
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)


    def test_fluxo_completo_gerente(self):
        # login como gerente
        self.client.force_authenticate(user=self.gerente)

        # cria produto
        url_produto = reverse('produto-list')

        produto_data = {
            "nome_produto": "Produto X",
            "unidade_medida": "UNIDADE",
            "categoria": "MERCADO",
        }

        response = self.client.post(url_produto, produto_data)
        self.assertEqual(response.status_code, 201)

        # cria loja
        url_loja = reverse('loja-list')

        loja_data = {
            "nome_loja": "Loja Gerente",
            "endereco": "Rua 1",
            "responsavel": self.gerente.id
        }

        response = self.client.post(url_loja, loja_data)
        self.assertEqual(response.status_code, 201)

    def test_responsavel_cria_pedido(self):
        self.client.force_authenticate(user=self.responsavel)

        url = "/api/v1/pedidos/"

        data = {
            "loja": self.loja.id,
            "status": "novo",
            "itens": [
                {
                    "produto": self.produto.id,
                    "quantidade": 2
                }
            ]
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)


    def test_user_nao_pode_criar_produto(self):
        self.client.force_authenticate(user=self.responsavel)
        

        url = reverse('produto-list')

        data = {
            "nome_produto": "Produto Teste",
            "unidade_medida": "UNIDADE",
            "categoria": "MERCADO",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)

    def test_responsavel_nao_pode_criar_loja(self):
        self.client.force_authenticate(user=self.responsavel)

        url = reverse('loja-list')

        data = {
            "nome_loja": "Loja Teste",
            "endereco": "Rua 2",
            "responsavel": self.responsavel.id
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
    
 
class NotificacaoEstoqueBaixoTestCase(TestCase):
    def test_notifica_apenas_responsavel_da_loja_com_estoque_baixo(self):
        grupo_responsavel, _ = Group.objects.get_or_create(name='Responsavel')
        responsavel_loja_1 = User.objects.create_user(
            username='loja1',
            email='loja1@email.com',
            password='123456',
        )
        responsavel_loja_1.groups.add(grupo_responsavel)
        responsavel_loja_2 = User.objects.create_user(
            username='loja2',
            email='loja2@email.com',
            password='123456',
        )
        responsavel_loja_2.groups.add(grupo_responsavel)

        loja_1 = Loja.objects.create(
            nome_loja='Loja 1',
            cidade='Cidade 1',
            endereco='Rua 1',
            responsavel=responsavel_loja_1,
        )
        Loja.objects.create(
            nome_loja='Loja 2',
            cidade='Cidade 2',
            endereco='Rua 2',
            responsavel=responsavel_loja_2,
        )
        produto = Produto.objects.create(
            nome_produto='Coxinha',
            categoria='SALGADOS_GDE',
            estoque_minimo_sugerido=5,
        )
        estoque = Estoque.objects.create(
            loja=loja_1,
            produto=produto,
            quantidade_atual=3,
            quantidade_minima=5,
        )

        notificar_estoque_baixo(estoque)

        self.assertTrue(
            Notificacao.objects.filter(
                usuario=responsavel_loja_1,
                tipo='estoque_baixo',
            ).exists()
        )
        self.assertFalse(
            Notificacao.objects.filter(
                usuario=responsavel_loja_2,
                tipo='estoque_baixo',
            ).exists()
        )

    def test_nao_duplica_notificacao_do_mesmo_estoque(self):
        usuario = User.objects.create_user(
            username='loja',
            email='loja@email.com',
            password='123456',
        )
        loja = Loja.objects.create(
            nome_loja='Loja',
            cidade='Cidade',
            endereco='Rua',
            responsavel=usuario,
        )
        produto = Produto.objects.create(
            nome_produto='Esfiha',
            categoria='ESFIHAS_GDE',
        )
        estoque = Estoque.objects.create(
            loja=loja,
            produto=produto,
            quantidade_atual=1,
            quantidade_minima=2,
        )

        notificar_estoque_baixo(estoque)
        Notificacao.objects.update(lida=True)
        notificar_estoque_baixo(estoque)

        self.assertEqual(
            Notificacao.objects.filter(
                usuario=usuario,
                tipo='estoque_baixo',
            ).count(),
            1,
        )

