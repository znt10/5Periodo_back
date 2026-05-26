- Login: `admin@email.com`
- Senha: `UNIFIP@123`

# UniStock API

Backend do sistema UniStock, desenvolvido com Django, Django REST Framework e MySQL.

A API gerencia usuarios, lojas, produtos, estoque e pedidos. A autenticacao usa JWT salvo em cookies HTTP-only.

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

Para parar:

```powershell
docker compose down
```

## Banco de Dados

O projeto usa MySQL. As variaveis ficam em `.env`:

```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

SECRET_KEY=f+c^2ef777*@@(ks2t@!)-lchgc2ad$$u@!z=7ahiz8bcg307a)

DB_ENGINE=django.db.backends.mysql
DB_NAME=p5
DB_USER=root
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=3306

DJANGO_SETTINGS_MODULE=backend.settings



```

No Docker Compose, o backend usa:

```yaml
DB_HOST: host.docker.internal
```

Isso permite que o container acesse o MySQL rodando na sua maquina.

## Inicializacao Automatica

Quando o container sobe, o `entrypoint.sh` executa automaticamente:

```powershell
python manage.py migrate
python manage.py loaddata groups
python manage.py ensure_admin
python manage.py runserver 0.0.0.0:8000
```

Ou seja, ao rodar `docker compose up`, o projeto ja:

- aplica migrations
- carrega os grupos e permissoes
- cria ou atualiza o admin padrao
- sobe o servidor Django

## Usuario Admin Padrao

O Docker Compose cria/atualiza este usuario automaticamente:

```text
email: admin@email.com
senha: UNIFIP@123
grupo: Gerente
is_staff: True
is_superuser: True
```

Login da API:

```text
POST /login/
```

Admin Django:

```text
http://localhost:8000/admin/
```

## Grupos e Permissoes

Os grupos ficam na fixture:

```text
backend/app/fixtures/groups.json
```

Grupos principais:

- `Gerente`
- `Responsavel`

Para carregar manualmente:

```powershell
docker compose exec api python manage.py loaddata groups
```

## IDs Publicos

Os models principais possuem `public_id` em UUID.

A API mostra esse UUID no campo `id`, evitando expor IDs numericos internos.

Exemplo:

```json
{
  "id": "9d543ab7-50a1-11f1-bacf-3c7c3f7b9a64",
  "nome_loja": "Loja Centro"
}
```

Rotas de detalhe tambem usam UUID:

```text
/api/v1/lojas/9d543ab7-50a1-11f1-bacf-3c7c3f7b9a64/
```

## Endpoints Principais

```text
POST /login/
POST /logout/
POST /token/refresh/

GET /api/v1/lojas/
GET /api/v1/produtos/
GET /api/v1/estoque/
GET /api/v1/pedidos/
GET /api/v1/user/me/
POST /api/v1/user/registrar/
```

Documentacao da API:

```text
http://localhost:8000/api/schema/
http://localhost:8000/api/schema/swagger/
```

## Comandos Uteis

Rodar checks:

```powershell
docker compose exec api python manage.py check
```

Criar migrations:

```powershell
docker compose exec api python manage.py makemigrations
```

Aplicar migrations:

```powershell
docker compose exec api python manage.py migrate
```

Abrir shell Django:

```powershell
docker compose exec api python manage.py shell
```

Recriar/atualizar admin padrao:

```powershell
docker compose exec api python manage.py ensure_admin
```

Ver logs:

```powershell
docker compose logs -f
```

## Observacoes

- Prefira rodar comandos Django pelo Docker.
- O ambiente virtual local pode falhar se o `mysqlclient` nao estiver instalado corretamente.
- Usuarios precisam estar em um grupo, como `Gerente` ou `Responsavel`, para acessar o sistema corretamente.
