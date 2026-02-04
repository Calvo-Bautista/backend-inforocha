from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
async def get_clients(
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
    
    Args:
        client_id: Client ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Client data
        
    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()
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
    
    Args:
        client: Client data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created client
        
    Raises:
        HTTPException: If legajo already exists
    """
    # Check if legajo already exists (if provided)
    if client.legajo:
        existing_client = db.query(Client).filter(Client.legajo == client.legajo).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this legajo already exists"
            )
    
    # Create new client
    db_client = Client(**client.model_dump())
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
