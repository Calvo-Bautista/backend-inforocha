# 🏢 InfoRocha — Sistema de Gestión Integral

Sistema web de gestión empresarial para **Informática Rocha**, que permite administrar ventas, clientes, productos, pedidos, despachos, usuarios y configuración del sistema.

---

## 📸 Stack Tecnológico

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.11+ | Lenguaje principal |
| **FastAPI** | 0.115 | Framework web / API REST |
| **SQLAlchemy** | 2.0 | ORM |
| **Alembic** | 1.14 | Migraciones de base de datos |
| **MySQL** | 8.0+ | Base de datos relacional |
| **JWT** (python-jose) | — | Autenticación |
| **Pydantic** | 2.10 | Validación de datos |
| **xhtml2pdf** / **Jinja2** | — | Generación de PDFs (remitos, presupuestos) |

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| **Next.js** | 16 | Framework React (App Router) |
| **React** | 19 | UI Library |
| **TypeScript** | 5 | Tipado estático |
| **TailwindCSS** | 4 | Estilos |
| **Radix UI** | — | Componentes accesibles (Dialog, Select, Tabs, etc.) |
| **Recharts** | 2.15 | Gráficos y reportes |
| **React Hook Form** + **Zod** | — | Formularios y validación |
| **Lucide React** | — | Iconografía |
| **Sonner** | — | Notificaciones toast |

---

## 🧩 Módulos Funcionales

| Módulo | Descripción |
|---|---|
| **Dashboard** | Vista general con KPIs y métricas del negocio |
| **Productos** | ABM de productos / insumos |
| **Clientes** | ABM de clientes |
| **Nueva Orden** | Creación de pedidos / órdenes de venta |
| **Mis Pedidos** | Gestión y seguimiento de pedidos |
| **Despachos** | Logística, despacho de órdenes y generación de remitos PDF |
| **Usuarios** | ABM de usuarios con roles y permisos por módulo |
| **Configuración** | Configuración general del sistema |

### Roles de Usuario

| Rol | Descripción |
|---|---|
| `owner` | Propietario — acceso total |
| `admin` | Administrador — gestión completa |
| `vendedor` | Vendedor — gestión de ventas |
| `logistica` | Logística — gestión de despachos |

---

## 📋 Requisitos Previos

- **Python** 3.11+
- **Node.js** 18+ y **npm**
- **MySQL** 8.0+

---

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ROCHA
```

### 2. Backend

```bash
cd backend-inforocha

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
# Editar .env con los datos de tu base de datos
```

**Variables de entorno del backend** (`.env`):

```env
SECRET_KEY=tu-clave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000

# Base de datos
MYSQL_USER=root
MYSQL_PASSWORD=tu-password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=inforocha
```

```bash
# Ejecutar migraciones
alembic upgrade head

# Iniciar el servidor
uvicorn app.main:app --reload
```

El backend estará disponible en:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Frontend

```bash
cd frontmaqueta/informatica-rocha-system

# Instalar dependencias
npm install

# Configurar variables de entorno
copy .env.example .env.local
# Editar .env.local con la URL del backend
```

**Variables de entorno del frontend** (`.env.local`):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

```bash
# Iniciar el servidor de desarrollo
npm run dev
```

El frontend estará disponible en http://localhost:3000.

---

## 🗂️ Estructura del Proyecto

```
ROCHA/
├── backend-inforocha/          # API REST (FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py         # Dependencias de autenticación
│   │   │   └── v1/             # Endpoints v1
│   │   │       ├── auth.py     # Login / JWT
│   │   │       ├── products.py # Productos
│   │   │       ├── clients.py  # Clientes
│   │   │       ├── orders.py   # Órdenes / Pedidos
│   │   │       ├── users.py    # Usuarios
│   │   │       └── config.py   # Configuración del sistema
│   │   ├── core/
│   │   │   ├── config.py       # Settings (Pydantic)
│   │   │   └── security.py     # JWT y hashing
│   │   ├── models/             # Modelos SQLAlchemy
│   │   ├── schemas/            # Schemas Pydantic
│   │   ├── templates/          # Templates Jinja2 (PDFs)
│   │   ├── database.py         # Conexión a BD
│   │   └── main.py             # App principal
│   ├── alembic/                # Migraciones de BD
│   ├── requirements.txt
│   └── .env.example
│
└── frontmaqueta/
    └── informatica-rocha-system/   # Frontend (Next.js)
        ├── app/
        │   ├── page.tsx            # Login
        │   └── dashboard/
        │       ├── page.jsx        # Dashboard principal
        │       ├── productos/      # Módulo Productos
        │       ├── clientes/       # Módulo Clientes
        │       ├── nueva-orden/    # Crear orden
        │       ├── mis-pedidos/    # Gestión de pedidos
        │       ├── despachos/      # Logística y despachos
        │       └── usuarios/       # Gestión de usuarios
        ├── components/
        │   ├── ui/                 # Componentes Radix/shadcn
        │   ├── sidebar.jsx         # Navegación lateral
        │   └── login-form.jsx      # Formulario de login
        ├── contexts/               # React Context (Auth, etc.)
        ├── hooks/                  # Custom hooks
        ├── lib/                    # Utilidades
        ├── package.json
        └── .env.example
```

---

## 🔐 Autenticación

La API utiliza **JWT (JSON Web Tokens)**:

```bash
# Obtener token
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
username=vendedor@rocha.com&password=123456

# Usar token en requests
Authorization: Bearer <token>
```

---

## 📝 API Endpoints

| Recurso | Método | Endpoint | Descripción |
|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/login` | Iniciar sesión |
| | `GET` | `/api/v1/auth/me` | Usuario actual |
| **Products** | `GET/POST` | `/api/v1/products` | Listar / Crear |
| | `PUT/DELETE` | `/api/v1/products/{id}` | Editar / Eliminar |
| **Clients** | `GET/POST` | `/api/v1/clients` | Listar / Crear |
| | `PUT/DELETE` | `/api/v1/clients/{id}` | Editar / Eliminar |
| **Orders** | `GET/POST` | `/api/v1/orders` | Listar / Crear |
| | `PUT/DELETE` | `/api/v1/orders/{id}` | Editar / Eliminar |
| **Users** | `GET/POST` | `/api/v1/users` | Listar / Crear |
| | `PUT/DELETE` | `/api/v1/users/{id}` | Editar / Eliminar |
| **Config** | `GET/PUT` | `/api/v1/config` | Leer / Actualizar config |

> 📖 Documentación interactiva completa disponible en `/docs` (Swagger) una vez iniciado el backend.

---

## 🚀 Deploy

| Componente | Plataforma Sugerida |
|---|---|
| **Backend** | [Render](https://render.com) |
| **Frontend** | [Vercel](https://vercel.com) |
| **Base de datos** | MySQL en Render, PlanetScale o Railway |

Para producción, configurar las variables de entorno en cada plataforma:
- **Backend**: `DATABASE_URL_OVERRIDE`, `SECRET_KEY`, `CORS_ORIGINS`
- **Frontend**: `NEXT_PUBLIC_API_URL`

---

## 📄 Licencia

Propiedad de **Informática Rocha**. Todos los derechos reservados.
