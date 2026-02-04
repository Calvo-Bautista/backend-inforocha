from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.call_log import CallLog
from app.models.user import User
from app.schemas.call_log import CallLogCreate, CallLogUpdate, CallLogResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[CallLogResponse])
async def get_call_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of call logs.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        client_id: Filter by client ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of call logs
    """
    query = db.query(CallLog)
    
    # Filter by client if specified
    if client_id:
        query = query.filter(CallLog.client_id == client_id)
    
    # Order by call date descending
    query = query.order_by(CallLog.call_date.desc())
    
    call_logs = query.offset(skip).limit(limit).all()
    return call_logs


@router.get("/{call_log_id}", response_model=CallLogResponse)
async def get_call_log(
    call_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific call log by ID.
    
    Args:
        call_log_id: Call log ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Call log data
        
    Raises:
        HTTPException: If call log not found
    """
    call_log = db.query(CallLog).filter(CallLog.id == call_log_id).first()
    if not call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call log not found"
        )
    return call_log


@router.post("/", response_model=CallLogResponse, status_code=status.HTTP_201_CREATED)
async def create_call_log(
    call_log: CallLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new call log.
    
    Args:
        call_log: Call log data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created call log
    """
    # Create new call log with current user as seller
    db_call_log = CallLog(
        **call_log.model_dump(),
        seller_id=current_user.id
    )
    db.add(db_call_log)
    db.commit()
    db.refresh(db_call_log)
    
    return db_call_log


@router.put("/{call_log_id}", response_model=CallLogResponse)
async def update_call_log(
    call_log_id: int,
    call_log: CallLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a call log.
    
    Args:
        call_log_id: Call log ID
        call_log: Updated call log data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated call log
        
    Raises:
        HTTPException: If call log not found
    """
    db_call_log = db.query(CallLog).filter(CallLog.id == call_log_id).first()
    if not db_call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call log not found"
        )
    
    # Update call log fields
    update_data = call_log.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_call_log, field, value)
    
    db.commit()
    db.refresh(db_call_log)
    
    return db_call_log


@router.delete("/{call_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call_log(
    call_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a call log.
    
    Args:
        call_log_id: Call log ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If call log not found
    """
    db_call_log = db.query(CallLog).filter(CallLog.id == call_log_id).first()
    if not db_call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call log not found"
        )
    
    db.delete(db_call_log)
    db.commit()
    
    return None
