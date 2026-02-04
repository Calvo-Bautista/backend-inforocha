# Plan de Desarrollo Backend - Informática Rocha
## Stack: FastAPI + MySQL

---

## 🎯 Estrategia Recomendada

### **Empezar con la Base de Datos primero**

**Razones:**
1. ✅ La BD define la estructura de datos (fuente de verdad)
2. ✅ Evita refactorizaciones costosas del backend
3. ✅ Ya tienes los datos mock muy claros en el frontend
4. ✅ El backend se construye alrededor del esquema de BD

**Workflow óptimo:**
```
Diseño BD → Crear BD → Backend FastAPI → Integrar Frontend
```

---

## 🗄️ Esquema de Base de Datos

### Tablas Principales

#### 1. **users** - Usuarios del Sistema
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('vendedor', 'logistica', 'admin', 'owner') NOT NULL,
    legajo VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_legajo (legajo),
    INDEX idx_role (role)
);
```

#### 2. **clients** - Clientes/Compradores
```sql
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    legajo VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address TEXT,
    industry VARCHAR(255),
    maquinas TEXT,
    tipo_cliente ENUM('alta', 'media', 'baja'),
    proveedor_actual VARCHAR(255),
    status ENUM('active', 'prospect') DEFAULT 'prospect',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_tipo_cliente (tipo_cliente)
);
```

#### 3. **products** - Productos
```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    category ENUM('toner', 'cartucho', 'drum', 'repuesto') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_category (category),
    INDEX idx_stock (stock)
);
```

#### 4. **orders** - Órdenes de Compra
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    client_id INT NOT NULL,
    seller_id INT NOT NULL,
    order_date DATE NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    discount DECIMAL(12, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    shipping DECIMAL(10, 2) DEFAULT 0,
    shipping_discount BOOLEAN DEFAULT FALSE,
    total DECIMAL(12, 2) NOT NULL,
    factura_a BOOLEAN DEFAULT FALSE,
    status ENUM('pendiente', 'preparacion', 'enviado', 'entregado') DEFAULT 'pendiente',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_order_number (order_number),
    INDEX idx_client_id (client_id),
    INDEX idx_seller_id (seller_id),
    INDEX idx_status (status),
    INDEX idx_order_date (order_date)
);
```

#### 5. **order_items** - Items de Órdenes
```sql
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);
```

#### 6. **call_logs** - Registro de Llamadas
```sql
CREATE TABLE call_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    seller_id INT NOT NULL,
    call_date DATE NOT NULL,
    industry VARCHAR(255),
    uses_printers BOOLEAN DEFAULT FALSE,
    printer_type VARCHAR(255),
    interested_in_quote BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_client_id (client_id),
    INDEX idx_seller_id (seller_id),
    INDEX idx_call_date (call_date)
);
```

---

## 🐍 Stack Backend: FastAPI

### Tecnologías
```python
# Core
FastAPI          # Framework web moderno y rápido
Uvicorn          # ASGI server
Python 3.11+     # Versión de Python

# Base de Datos
SQLAlchemy       # ORM
PyMySQL          # Driver MySQL
Alembic          # Migraciones

# Autenticación
python-jose      # JWT tokens
passlib          # Hash de passwords
bcrypt           # Algoritmo de hash

# Validación
Pydantic         # Validación de datos (incluido en FastAPI)

# Utilidades
python-dotenv    # Variables de entorno
python-multipart # Form data
```

### Estructura del Proyecto
```
backend-inforocha/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── config.py               # Configuración
│   ├── database.py             # Conexión a BD
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── call_log.py
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── call_log.py
│   │
│   ├── api/                    # Endpoints
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependencias
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── clients.py
│   │       ├── products.py
│   │       ├── orders.py
│   │       └── call_logs.py
│   │
│   ├── core/                   # Lógica central
│   │   ├── __init__.py
│   │   ├── security.py        # JWT, passwords
│   │   └── config.py          # Settings
│   │
│   └── utils/                  # Utilidades
│       ├── __init__.py
│       └── helpers.py
│
├── alembic/                    # Migraciones
│   ├── versions/
│   └── env.py
│
├── tests/                      # Tests
│   ├── __init__.py
│   └── test_api.py
│
├── .env                        # Variables de entorno
├── .env.example
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## 📦 Instalación y Setup

### 1. Crear Proyecto
```bash
# Crear directorio
mkdir backend-inforocha
cd backend-inforocha

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Crear requirements.txt
```

### 2. requirements.txt
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
pymysql==1.1.0
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

```bash
pip install -r requirements.txt
```

### 3. Archivo .env
```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/inforocha_db

# Security
SECRET_KEY=tu-secret-key-super-segura-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Informática Rocha API
DEBUG=True
API_V1_PREFIX=/api/v1

# CORS
FRONTEND_URL=http://localhost:3000
```

---

## 🚀 Código Base FastAPI

### app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, clients, products, orders, call_logs

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API para sistema de gestión de ventas"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
app.include_router(clients.router, prefix=f"{settings.API_V1_PREFIX}/clients", tags=["clients"])
app.include_router(products.router, prefix=f"{settings.API_V1_PREFIX}/products", tags=["products"])
app.include_router(orders.router, prefix=f"{settings.API_V1_PREFIX}/orders", tags=["orders"])
app.include_router(call_logs.router, prefix=f"{settings.API_V1_PREFIX}/call-logs", tags=["call-logs"])

@app.get("/")
def root():
    return {"message": "Informática Rocha API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### app/core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    FRONTEND_URL: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### app/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/core/security.py
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

---

## 📋 Plan de Implementación

### Fase 1: Base de Datos (1-2 días)
- [ ] Crear base de datos MySQL
- [ ] Ejecutar script de creación de tablas
- [ ] Configurar Alembic para migraciones
- [ ] Crear script de seed con datos de prueba
- [ ] Verificar relaciones y constraints

### Fase 2: Setup Backend (1 día)
- [ ] Crear proyecto FastAPI
- [ ] Configurar estructura de carpetas
- [ ] Instalar dependencias
- [ ] Configurar variables de entorno
- [ ] Configurar conexión a BD
- [ ] Crear modelos SQLAlchemy

### Fase 3: Autenticación (1-2 días)
- [ ] Implementar registro de usuarios
- [ ] Implementar login (JWT)
- [ ] Implementar middleware de autenticación
- [ ] Proteger rutas con dependencias
- [ ] Testing de autenticación

### Fase 4: Endpoints CRUD (2-3 días)
- [ ] Products CRUD
- [ ] Clients CRUD
- [ ] Orders CRUD
- [ ] Call Logs CRUD
- [ ] Users CRUD (admin)

### Fase 5: Testing (1 día)
- [ ] Probar todos los endpoints con Postman
- [ ] Documentar API (Swagger automático)
- [ ] Verificar validaciones
- [ ] Testing de errores

### Fase 6: Integración Frontend (2-3 días)
- [ ] Crear servicio API en frontend
- [ ] Migrar autenticación
- [ ] Migrar cada módulo
- [ ] Testing end-to-end

**Total estimado: 8-12 días**

---

## 🎯 Próximos Pasos

### Opción 1: Diseño Completo de BD
Puedo crear:
- ✅ Script SQL completo de creación
- ✅ Diagrama ER en Mermaid
- ✅ Script de seed con datos del mock
- ✅ Documentación de relaciones

### Opción 2: Setup Completo del Backend
Puedo crear:
- ✅ Estructura completa del proyecto
- ✅ Todos los archivos base
- ✅ Modelos SQLAlchemy
- ✅ Schemas Pydantic
- ✅ Endpoints básicos

### Opción 3: Ambas en Paralelo
- ✅ Diseñar BD + Setup backend simultáneamente
- ✅ Workflow más rápido

---

## 💡 Ventajas de FastAPI

✅ **Documentación automática** (Swagger UI en `/docs`)
✅ **Validación automática** con Pydantic
✅ **Type hints** nativos de Python
✅ **Alto rendimiento** (comparable a Node.js)
✅ **Async/await** nativo
✅ **Fácil testing**
✅ **Excelente para APIs REST**

---

## 🚀 ¿Empezamos?

**Recomiendo empezar con:**
1. Crear el script SQL completo de la BD
2. Crear la base de datos en MySQL
3. Setup del proyecto FastAPI
4. Implementar modelos y conexión

**¿Por dónde quieres arrancar?**
