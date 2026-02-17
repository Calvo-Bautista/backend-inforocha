from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, products, clients, orders, users, config, websocket

# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://26.190.79.61:3000", # Network IP seen in logs
    "*", # Allow all temporarily for development if needed, or stick to specifics
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)


@app.get("/")
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "message": "Bienvenido a InfoRocha Backend API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["Products"])
app.include_router(clients.router, prefix=f"{settings.API_V1_STR}/clients", tags=["Clients"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["Orders"])

app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(config.router, prefix=f"{settings.API_V1_STR}/config", tags=["Configuration"])
app.include_router(websocket.router, prefix=f"{settings.API_V1_STR}", tags=["Websocket"])
