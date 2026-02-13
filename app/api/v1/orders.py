from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from sqlalchemy import func
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.client import Client
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStats
from app.api.deps import get_current_user
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from fastapi.responses import Response, StreamingResponse
import io
import os

def format_currency(value):
    if value is None:
        return "$ 0"
    return f"$ {value:,.0f}".replace(",", ".")

router = APIRouter()


def generate_order_number(db: Session) -> str:
    """Generate a unique order number"""
    # Get current year
    year = datetime.now().year
    
    # Count orders for this year
    count = db.query(Order).filter(
        Order.order_number.like(f"ORD-{year}-%")
    ).count()
    
    # Generate new order number
    order_number = f"ORD-{year}-{count + 1:03d}"
    return order_number


@router.get("/stats", response_model=OrderStats)
async def get_order_stats(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated order statistics.
    """
    query = db.query(Order)
    
    # Filter by user role
    if current_user.role == UserRole.VENDEDOR:
        query = query.filter(Order.seller_id == current_user.id)

    # Filter by date
    if month:
        query = query.filter(func.extract('month', Order.order_date) == month)
    if year:
        query = query.filter(func.extract('year', Order.order_date) == year)
        
    # Total count
    total_orders = query.count()
    
    # Total revenue
    total_revenue = query.with_entities(func.sum(Order.total)).scalar() or 0
    
    # Count by status
    status_query = db.query(
        Order.status, func.count(Order.status)
    )

    if month:
        status_query = status_query.filter(func.extract('month', Order.order_date) == month)
    if year:
        status_query = status_query.filter(func.extract('year', Order.order_date) == year)
    
    if current_user.role == UserRole.VENDEDOR:
        status_query = status_query.filter(Order.seller_id == current_user.id)
        
    status_counts = status_query.group_by(Order.status).all()
    
    by_status = {
        "pendiente": 0,
        "preparacion": 0,
        "enviado": 0,
        "entregado": 0
    }
    
    for status_enum, count in status_counts:
        # Handle both Enum objects and string values
        status_key = status_enum.value if hasattr(status_enum, 'value') else str(status_enum)
        if status_key in by_status:
            by_status[status_key] = count

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "by_status": by_status
    }


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[OrderStatus] = None,
    search: Optional[str] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of orders.
    Vendedores only see their own orders.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by order status
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of orders
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(Order).options(
        joinedload(Order.client),
        joinedload(Order.items).joinedload(OrderItem.product)
    )
    
    # Vendedores only see their own orders
    if current_user.role == UserRole.VENDEDOR:
        query = query.filter(Order.seller_id == current_user.id)
    
    # Filter by date
    if month:
        query = query.filter(func.extract('month', Order.order_date) == month)
    if year:
        query = query.filter(func.extract('year', Order.order_date) == year)

    # Filter by status
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    # Filter by search (Order ID, Order Number, or Client Name)
    if search:
        search_filter = f"%{search}%"
        # Join with Client to search by client name
        query = query.join(Client, isouter=True) # Left join to include orders without clients if any (though unlikely)
        query = query.filter(
            (Order.order_number.ilike(search_filter)) |
            (Client.name.ilike(search_filter))
        )
    
    # Order by date descending
    query = query.order_by(Order.order_date.desc())
    
    # Calculate total count before pagination
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific order by ID.
    
    Args:
        order_id: Order ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Order data
        
    Raises:
        HTTPException: If order not found or access denied
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Vendedores can only see their own orders
    if current_user.role == UserRole.VENDEDOR and order.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return order


@router.get("/{order_id}/remito")
async def generate_remito(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF remito for an order.
    
    Args:
        order_id: Order ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        PDF file stream
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Vendedores can only see their own orders
    if current_user.role == UserRole.VENDEDOR and order.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get logo base64
    logo_path = None
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    possible_paths = [
        # User requested specific logo: logofondonegro.png
        r"c:\Users\bauti\OneDrive\Desktop\proyectos\ROCHA\frontmaqueta\informatica-rocha-system\public\logofondonegro.png",
        # User requested specific logo: Nombre.png at project root
        r"c:\Users\bauti\OneDrive\Desktop\proyectos\ROCHA\Nombre.png",
        # New location: public folder in frontend
        r"c:\Users\bauti\OneDrive\Desktop\proyectos\ROCHA\frontmaqueta\informatica-rocha-system\public\Nombre.png",
        os.path.join(base_dir, "Nombre.png"),
        os.path.join(os.path.dirname(base_dir), "Nombre.png"),
        # Fallbacks just in case
        os.path.join(base_dir, "app", "static", "Logo.png"), 
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logo_path = path
            break

    logo_base64 = ""
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("remito.html")

    # Render HTML
    html_content = template.render(
        order=order,
        logo_base64=logo_base64,
        format_currency=format_currency
    )

    # Generate PDF
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    
    if pisa_status.err:
        raise HTTPException(status_code=500, detail="Error generating PDF")

    pdf_file.seek(0)
    
    filename = f"Remito-{order.order_number}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order.
    
    Args:
        order: Order data with items
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created order
    """
    # Generate order number
    order_number = generate_order_number(db)
    
    # Create order (exclude items from dict)
    order_data = order.model_dump(exclude={"items"})
    db_order = Order(
        **order_data,
        order_number=order_number,
        seller_id=current_user.id
    )
    db.add(db_order)
    db.flush()  # Get order ID without committing
    
    # Create order items and update stock
    for item in order.items:
        # Get product to update stock
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        # Check sufficient stock
        if product.stock < item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock}, Requested: {item.quantity}"
            )
            
        # Deduct stock
        product.stock -= item.quantity
        db.add(product)
        
        db_item = OrderItem(
            **item.model_dump(),
            order_id=db_order.id
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an order (typically just status).
    
    Args:
        order_id: Order ID
        order: Updated order data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated order
        
    Raises:
        HTTPException: If order not found
    """
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an order (admin/owner only).
    
    Args:
        order_id: Order ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If order not found or access denied
    """
    # Only admin and owner can delete orders
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or owner can delete orders"
        )
    
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    db.delete(db_order)
    db.commit()
    
    return None
