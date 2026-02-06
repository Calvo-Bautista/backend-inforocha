from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of clients with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by client status (active/prospect)
        search: Search in name, phone, address, or legajo
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of clients
    """
    query = db.query(Client)
    
    # RBAC: Filter clients based on user role
    # ADMIN, OWNER, LOGISTICA see all clients
    # VENDEDOR (and others) see only their own clients
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.LOGISTICA]:
        query = query.filter(Client.user_id == current_user.id)
    
    # Filter by status
    if status_filter:
        query = query.filter(Client.status == status_filter)
    
    # Search in multiple fields
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Client.name.ilike(search_filter)) |
            (Client.phone.ilike(search_filter)) |
            (Client.address.ilike(search_filter)) |
            (Client.legajo.ilike(search_filter))
        )
    
    # Calculate total count before pagination
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    clients = query.offset(skip).limit(limit).all()
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific client by ID.
    """
    query = db.query(Client).filter(Client.id == client_id)
    
    # RBAC Check for single client
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.LOGISTICA]:
        query = query.filter(Client.user_id == current_user.id)
        
    client = query.first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new client.
    """
    # Check if legajo already exists (if provided)
    if client.legajo:
        existing_client = db.query(Client).filter(Client.legajo == client.legajo).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this legajo already exists"
            )
    else:
        # Auto-generate legajo: CLI-XXX
        last_client = db.query(Client).filter(Client.legajo.like("CLI-%")).order_by(Client.legajo.desc()).first()
        if last_client and last_client.legajo:
            try:
                # Extract number part
                last_number = int(last_client.legajo.split("-")[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        client.legajo = f"CLI-{new_number:03d}"
    
    # Create new client with current user as owner
    client_data = client.model_dump()
    db_client = Client(**client_data)
    db_client.user_id = current_user.id
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a client.
    
    Args:
        client_id: Client ID
        client: Updated client data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated client
        
    Raises:
        HTTPException: If client not found
    """
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update client fields
    update_data = client.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a client.
    
    Args:
        client_id: Client ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If client not found
    """
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db.delete(db_client)
    db.commit()
    
    return None
