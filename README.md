# UniStock API

Backend do sistema **UniStock**, desenvolvido com Django e Django REST Framework.

A API e responsavel pelo gerenciamento de usuarios, lojas, produtos, estoque e pedidos. A autenticacao do sistema utiliza JWT salvo em cookies HTTP-only.

## Tecnologias

- Python 3.12
- Django
- Django REST Framework
- Simple JWT
- MySQL
- Docker Compose

## Como Rodar

Entre na pasta do backend:

```powershell
cd "D:\5 Periodo\backend"
```

Suba o container:

```powershell
docker compose up --build
```

Ou rode em segundo plano:

```powershell
docker compose up -d --build
```

A API ficara disponivel em:

```text
http://localhost:8000
```

Para parar o container:

```powershell
docker compose down
```

## Usuario Admin Padrao

Login:

```text
admin@email.com
```

Senha:

```text
UNIFIP@123
```

O usuario admin padrao e criado/atualizado automaticamente ao subir o Docker.

```text
grupo: Admin
is_staff: True
is_superuser: True
```

Admin Django:

```text
http://localhost:8000/admin/
```

## Endpoints Principais

```text
POST /login/
POST /logout/
POST /token/refresh/

GET /api/v1/user/me/
POST /api/v1/user/registrar/

GET /api/v1/lojas/
GET /api/v1/produtos/
GET /api/v1/estoque/
GET /api/v1/pedidos/
```

## Documentacao da API

```text
http://localhost:8000/api/schema/
http://localhost:8000/api/schema/swagger/
```

## Observacoes

- O projeto usa MySQL como banco de dados.
- As configuracoes do ambiente ficam no arquivo `.env`.
- Ao subir o Docker, o sistema aplica as migrations, carrega os grupos e cria/atualiza o usuario admin padrao automaticamente.
- Usuarios precisam estar em um grupo, como `Admin`, `Gerente` ou `Responsavel`, para acessar o sistema corretamente.
- Se este repositorio for publico, nao deixe senha real nem `SECRET_KEY` no README ou no historico do Git.
