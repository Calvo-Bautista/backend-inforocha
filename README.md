# InfoRocha Backend API

Backend API para el sistema de gestión de ventas de Informática Rocha.

## 🚀 Stack Tecnológico

- **Framework**: FastAPI 0.115.0
- **Database**: MySQL 8.0+
- **ORM**: SQLAlchemy 2.0.36
- **Migrations**: Alembic 1.14.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Python**: 3.11+

## 📋 Requisitos Previos

- Python 3.11 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
cd backend-inforocha
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Database MySQL
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=inforocha_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Crear base de datos

```bash
mysql -u root -p < schema.sql
```

### 7. Ejecutar migraciones

```bash
alembic upgrade head
```

### 8. Cargar datos de prueba

```bash
mysql -u root -p inforocha_db < seed_data.sql
```

## 🏃 Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## 📚 Documentación de la API

La documentación interactiva está disponible en `/docs` una vez que el servidor esté corriendo.

### Usuarios de Prueba

| Email | Password | Role | Descripción |
|-------|----------|------|-------------|
| vendedor@rocha.com | 123456 | vendedor | Vendedor |
| logistica@rocha.com | 123456 | logistica | Logística |
| admin@rocha.com | 123456 | admin | Administrador |
| owner@rocha.com | 123456 | owner | Propietario |

## 🗂️ Estructura del Proyecto

```
backend-inforocha/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependencias de autenticación
│   │   └── v1/
│   │       ├── auth.py          # Endpoints de autenticación
│   │       ├── products.py      # Endpoints de productos
│   │       ├── clients.py       # Endpoints de clientes
│   │       ├── orders.py        # Endpoints de órdenes
│   │       └── call_logs.py     # Endpoints de llamadas
│   ├── core/
│   │   ├── config.py            # Configuración
│   │   └── security.py          # Seguridad (JWT, passwords)
│   ├── models/                  # Modelos SQLAlchemy
│   ├── schemas/                 # Schemas Pydantic
│   ├── database.py              # Conexión a BD
│   └── main.py                  # Aplicación principal
├── alembic/                     # Migraciones
├── schema.sql                   # Schema de BD
├── seed_data.sql                # Datos de prueba
├── requirements.txt             # Dependencias
└── .env                         # Variables de entorno
```

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación.

### Obtener token:

```bash
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=vendedor@rocha.com&password=123456
```

### Usar token:

```bash
GET /api/v1/products
Authorization: Bearer <your-token-here>
```

## 📝 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Usuario actual

### Productos
- `GET /api/v1/products` - Listar productos
- `POST /api/v1/products` - Crear producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}` - Eliminar producto

### Clientes
- `GET /api/v1/clients` - Listar clientes
- `POST /api/v1/clients` - Crear cliente
- `PUT /api/v1/clients/{id}` - Actualizar cliente
- `DELETE /api/v1/clients/{id}` - Eliminar cliente

### Órdenes
- `GET /api/v1/orders` - Listar órdenes
- `POST /api/v1/orders` - Crear orden
- `PUT /api/v1/orders/{id}` - Actualizar orden
- `DELETE /api/v1/orders/{id}` - Eliminar orden

### Llamadas
- `GET /api/v1/call-logs` - Listar llamadas
- `POST /api/v1/call-logs` - Crear llamada
- `PUT /api/v1/call-logs/{id}` - Actualizar llamada
- `DELETE /api/v1/call-logs/{id}` - Eliminar llamada

## 🧪 Testing

Ver la documentación interactiva en `/docs` para probar todos los endpoints.

## 📄 Licencia

Propiedad de Informática Rocha
