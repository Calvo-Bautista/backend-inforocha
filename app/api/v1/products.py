from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, UploadFile, File
import openpyxl
import io
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of products with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category: Filter by product category
        search: Search in name, description, or SKU
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of products
    """
    query = db.query(Product)
    
    # Filter by category
    if category:
        query = query.filter(Product.category == category)
    
    # Search in description or Articulo
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.description.ilike(search_filter)) |
            (Product.articulo.ilike(search_filter))
        )
    
    # Only show active products by default
    query = query.filter(Product.is_active == True)
    
    # Calculate total count before pagination
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific product by ID.
    
    Args:
        product_id: Product ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Product data
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER]))
):
    """
    Create a new product (admin/owner only).
    
    Args:
        product: Product data
        db: Database session
        current_user: Current authenticated user (must be admin or owner)
        
    Returns:
        Created product
        
    Raises:
        HTTPException: If Articulo already exists
    """
    # Check if Articulo already exists
    existing_product = db.query(Product).filter(Product.articulo == product.articulo).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this Articulo already exists"
        )
    
    # Create new product
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER]))
):
    """
    Update a product (admin/owner only).
    
    Args:
        product_id: Product ID
        product: Updated product data
        db: Database session
        current_user: Current authenticated user (must be admin or owner)
        
    Returns:
        Updated product
        
    Raises:
        HTTPException: If product not found or Articulo already exists
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if new Articulo already exists (if Articulo is being updated)
    if product.articulo and product.articulo != db_product.articulo:
        existing_product = db.query(Product).filter(Product.articulo == product.articulo).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this Articulo already exists"
            )
    
    # Update product fields
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER]))
):
    """
    Delete a product (admin/owner only).
    
    Args:
        product_id: Product ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If product not found
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()
    
    return None


@router.get("/budget/download", response_class=Response)
async def download_budget(
    response: Response,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and download a PDF budget of products.
    
    Args:
        category: Filter by product category
        search: Search in description, or Articulo
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        PDF file stream
    """
    import io
    from xhtml2pdf import pisa
    from jinja2 import Environment, FileSystemLoader
    from datetime import datetime
    import os

    # Query products
    query = db.query(Product)
    
    # Filter by category
    if category and category != 'all':
        query = query.filter(Product.category == category)
    
    # Search in description or Articulo
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.description.ilike(search_filter)) |
            (Product.articulo.ilike(search_filter))
        )
    
    # Only show active products
    query = query.filter(Product.is_active == True)
    
    # Order by category and description
    products = query.order_by(Product.category, Product.description).all()
    
    # Group products by category
    products_by_category = {}
    for product in products:
        cat = product.category or "Sin Categoría"
        if cat not in products_by_category:
            products_by_category[cat] = []
        products_by_category[cat].append(product)
        
    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("presupuesto.html")
    
    # Prepare context
    # Use relative path to app/static for logo (works in any environment)
    import base64
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None  # Disable decompression bomb check for logos
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(base_dir, "static", "logofondonegro.png")
    print(f"[PRESUPUESTO] Logo path: {logo_path}")
    print(f"[PRESUPUESTO] File exists: {os.path.exists(logo_path)}")
    logo_base64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        print(f"[PRESUPUESTO] Logo base64 length: {len(logo_base64)}")
    else:
        print(f"[PRESUPUESTO] WARNING: Logo file not found!")
            
    # Format date in Spanish manually to avoid locale issues
    now = datetime.now()
    days = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    date_str = f"{days[now.weekday()]}, {now.day} de {months[now.month]} de {now.year}"

    context = {
        "date": date_str,
        "products_by_category": products_by_category,
        "logo_base64": logo_base64,
        "vendedor_nombre": current_user.name
    }
    
    # Render HTML
    html_content = template.render(context)
    
    # Generate PDF
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        io.BytesIO(html_content.encode("utf-8")),
        dest=pdf_buffer
    )
    
    if pisa_status.err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating PDF"
        )
        
    pdf_buffer.seek(0)
    
    # Return response
    # Return response
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=presupuesto_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.OWNER]))
):
    """
    Import products from Excel file.
    Owner only.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload .xlsx file")

    try:
        contents = await file.read()
        workbook = openpyxl.load_workbook(io.BytesIO(contents))
        
        products_created = 0
        products_updated = 0
        
        # Flexible sheet matching mapping
        sheet_mapping = {
            "toner": "toner", "toners": "toner",
            "tinta": "cartucho", "tintas": "cartucho", "cartucho": "cartucho", "cartuchos": "cartucho",
            "drum": "drum", "drums": "drum" 
        }

        for sheet_name in workbook.sheetnames:
            normalized_name = sheet_name.lower().strip()
            product_type = sheet_mapping.get(normalized_name)
            
            if not product_type:
                # Try partial matching if exact match fails
                # e.g. "Toner HP" -> "toner"
                if "toner" in normalized_name:
                    product_type = "toner"
                elif "tinta" in normalized_name or "cartucho" in normalized_name:
                    product_type = "cartucho"
                elif "drum" in normalized_name:
                    product_type = "drum"
                else:
                     print(f"Skipping sheet: {sheet_name} (No matching type found)")
                     continue

                
            sheet = workbook[sheet_name]
            
            # Iterate rows, skipping header (row 1)
            for row in sheet.iter_rows(min_row=2, values_only=True):
                # Ensure row has at least 3 columns (A, B, C)
                if not row or len(row) < 3 or not row[0]: 
                    continue
                    
                articulo = str(row[0]).strip()
                description = str(row[1]).strip() if row[1] else ""
                
                try:
                    price_val = row[2]
                    if isinstance(price_val, str):
                        # Handle basic string formatting if present (e.g. "$ 100", "1.000,00")
                        # Assuming clean float from Excel usually, but basic cleanup helps
                        price_val = price_val.replace('$', '').replace('.', '').replace(',', '.').strip()
                    price = float(price_val) if price_val is not None else 0.0
                except (ValueError, AttributeError):
                    price = 0.0
                    
                # Upsert logic
                existing_product = db.query(Product).filter(Product.articulo == articulo).first()
                
                if existing_product:
                    # Update
                    existing_product.description = description
                    existing_product.price = price
                    existing_product.category = product_type
                    # NOT updating stock for existing products to preserve inventory
                    products_updated += 1
                else:
                    # Create
                    new_product = Product(
                        articulo=articulo,
                        description=description,
                        price=price,
                        category=product_type,
                        stock=0, # Initial stock 0
                        is_active=True
                    )
                    db.add(new_product)
                    products_created += 1
                    
        db.commit()
        
        return {
            "message": "Import completed successfully",
            "created": products_created,
            "updated": products_updated
        }
        
    except Exception as e:
        print(f"Error importing products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

