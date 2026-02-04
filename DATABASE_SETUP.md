# InfoRocha Backend - Database Initialization Guide

## Prerequisites

1. **MySQL Server** must be installed and running
2. **Python virtual environment** must be activated
3. **Dependencies** must be installed (`pip install -r requirements.txt`)

## Step 1: Create Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE IF NOT EXISTS inforocha_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Or use the schema.sql file:

```bash
mysql -u root -p < schema.sql
```

## Step 2: Run Alembic Migrations

Generate the initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply the migration:

```bash
alembic upgrade head
```

## Step 3: Load Seed Data

Load the seed data into the database:

```bash
mysql -u root -p inforocha_db < seed_data.sql
```

## Step 4: Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 5: Test Authentication

1. Go to http://localhost:8000/docs
2. Click on "POST /api/v1/auth/login"
3. Click "Try it out"
4. Use these credentials:
   - **username**: vendedor@rocha.com
   - **password**: 123456
5. Click "Execute"
6. Copy the `access_token` from the response
7. Click the "Authorize" button at the top
8. Paste the token and click "Authorize"

Now you can test all protected endpoints!

## Available Test Users

| Email | Password | Role | Legajo |
|-------|----------|------|--------|
| vendedor@rocha.com | 123456 | vendedor | LEG-001 |
| logistica@rocha.com | 123456 | logistica | LEG-002 |
| admin@rocha.com | 123456 | admin | LEG-003 |
| owner@rocha.com | 123456 | owner | LEG-000 |

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Products
- `GET /api/v1/products` - List products (with search & filters)
- `GET /api/v1/products/{id}` - Get product by ID
- `POST /api/v1/products` - Create product (admin/owner only)
- `PUT /api/v1/products/{id}` - Update product (admin/owner only)
- `DELETE /api/v1/products/{id}` - Delete product (admin/owner only)

### Clients
- `GET /api/v1/clients` - List clients (with search & filters)
- `GET /api/v1/clients/{id}` - Get client by ID
- `POST /api/v1/clients` - Create client
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Orders
- `GET /api/v1/orders` - List orders (vendedores see only their own)
- `GET /api/v1/orders/{id}` - Get order by ID
- `POST /api/v1/orders` - Create order
- `PUT /api/v1/orders/{id}` - Update order status
- `DELETE /api/v1/orders/{id}` - Delete order (admin/owner only)

### Call Logs
- `GET /api/v1/call-logs` - List call logs
- `GET /api/v1/call-logs/{id}` - Get call log by ID
- `POST /api/v1/call-logs` - Create call log
- `PUT /api/v1/call-logs/{id}` - Update call log
- `DELETE /api/v1/call-logs/{id}` - Delete call log

## Troubleshooting

### Database Connection Error
- Check that MySQL is running
- Verify credentials in `.env` file
- Ensure database `inforocha_db` exists

### Import Errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### Alembic Errors
- Check that all models are imported in `alembic/env.py`
- Verify `DATABASE_URL` in `.env` is correct
