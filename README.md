# Lu Estilo API

API RESTful construída com FastAPI para gerenciar clientes, produtos, pedidos e autenticação via JWT. Inclui integração com WhatsApp (sandbox Twilio).

## 🚀 Funcionalidades Principais

- **Autenticação completa** (registro, login, refresh token, logout)
- **Gerenciamento de clientes** (CRUD)
- **Gerenciamento de produtos** (CRUD)
- **Gerenciamento de pedidos** (CRUD)
- **Integração com WhatsApp** via API sandbox Twilio
- **Controle de acesso por níveis** (usuário comum e administrador)
- **Comando para alternar status de administrador** de um usuário (toggle admin)

## 📋 Endpoints da API

### 🔐 Autenticação

| Método | Rota | Descrição | Acesso |
|--------|------|-----------|--------|
| POST | `/auth/register` | Registrar novo usuário | Público |
| POST | `/auth/login` | Login e obtenção de token | Público |
| POST | `/auth/refresh` | Refresh token | Token válido |
| POST | `/auth/logout` | Logout | Token válido |

### 👥 Clientes

| Método | Rota | Descrição | Acesso |
|--------|------|-----------|--------|
| GET | `/clients` | Listar clientes | Usuário/Admin |
| POST | `/clients` | Criar cliente | Usuário/Admin |
| GET | `/clients/{id}` | Detalhes cliente | Usuário/Admin |
| PUT | `/clients/{id}` | Atualizar cliente | Usuário/Admin |
| DELETE | `/clients/{id}` | Deletar cliente | **Admin somente** |

### 📦 Produtos

| Método | Rota | Descrição | Acesso |
|--------|------|-----------|--------|
| GET | `/products` | Listar produtos | Usuário/Admin |
| POST | `/products` | Criar produto | **Admin somente** |
| GET | `/products/{id}` | Detalhes produto | Usuário/Admin |
| PUT | `/products/{id}` | Atualizar produto | **Admin somente** |
| DELETE | `/products/{id}` | Deletar produto | **Admin somente** |

### 📋 Pedidos

| Método | Rota | Descrição | Acesso |
|--------|------|-----------|--------|
| GET | `/orders` | Listar pedidos | Usuário/Admin |
| POST | `/orders` | Criar pedido | Usuário/Admin |
| GET | `/orders/{id}` | Detalhes do pedido | Usuário/Admin |
| PUT | `/orders/{id}` | Atualizar pedido | Usuário/Admin |
| DELETE | `/orders/{id}` | Deletar pedido | **Admin somente** |

## ⚙️ Configuração do Ambiente

### 1. Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis de ambiente:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=lu_estilo
POSTGRES_HOST=db
POSTGRES_PORT=5432
JWT_SECRET=seu_segredo_aqui
TWILIO_ACCOUNT_SID=seu_sid_twilio
TWILIO_AUTH_TOKEN=seu_token_twilio
TWILIO_WHATSAPP_SANDBOX_NUMBER=+14155238886
```

### 2. Inicialização com Docker

Rode o Docker Compose para iniciar os containers (Postgres + API):

```bash
docker-compose up --build
```

**A API ficará disponível em:** `http://localhost:8000`

## 📱 Integração WhatsApp - Sandbox Twilio

Para testar a integração com o WhatsApp no ambiente sandbox do Twilio:

1. **Entre no sandbox do Twilio** usando o link:
   ```
   https://api.whatsapp.com/send/?phone=%2B14155238886&text=join+circle-continent&type=phone_number&app_absent=0
   ```

2. **Após entrar**, você poderá receber mensagens da API em seu WhatsApp.

## 👨‍💼 Comando para Toggle Admin

### Via Container Docker

1. **Liste os containers rodando** para descobrir o nome ou ID do container:
   ```bash
   docker ps
   ```

2. **Localize o nome do container** que está rodando a aplicação (na coluna NAMES).

3. **Acesse o container** usando o nome encontrado:
   ```bash
   docker exec -it NOME_DO_CONTAINER bash
   ```

4. **Dentro do container**, rode o script com o e-mail:
   ```bash
   python app/utils/toggle_admin.py usuario@example.com
   ```

> **Nota:** Substitua `usuario@example.com` pelo e-mail real do usuário que deseja alterar.

### Via API (Alternativo)

Caso tenha criado uma rota para isso:

```http
POST /admin/toggle-admin/{user_id}
Authorization: Bearer <token-admin>
```

## 🔒 Autenticação e Autorização

### Headers de Autenticação

As rotas que precisam de autenticação exigem o token JWT no header:

```http
Authorization: Bearer <token>
```

### Níveis de Acesso

- **Usuários comuns:** Podem ver e modificar seus próprios clientes e pedidos
- **Administradores:** Podem criar/deletar produtos e deletar clientes e pedidos

## 🗄️ Banco de Dados

- **Banco:** PostgreSQL rodando em container Docker
- **Porta:** 5432 (mapeada para o host)
- **Acesso:** Use PgAdmin ou outro cliente para acessar via `localhost:5432` com usuário e senha do `.env`

## 📚 Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **JWT** - Autenticação via tokens
- **Twilio** - Integração WhatsApp
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers

## 📞 Suporte

Se precisar de ajuda, é só chamar!