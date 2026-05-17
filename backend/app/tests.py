from django.test import TestCase
from django.contrib.auth.models import User, Group,Permission
from django.contrib.contenttypes.models import ContentType
from app.models import Loja, Produto, Pedido, ItemPedido, Estoque
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
            codigo=1,
            unidade_medida="kg"
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
            "codigo": "PX",
            "unidade_medida": "un",
            "ativo": True
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
            "codigo": "PT",
            "unidade_medida": "un",
            "ativo": True
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
    
 