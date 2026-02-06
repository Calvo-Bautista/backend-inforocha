from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.config import BusinessConfig
from app.models.user import User, UserRole
from app.schemas.config import ConfigResponse, ConfigUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=ConfigResponse)
async def get_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current system configuration.
    If no configuration exists, creates a default one.
    """
    config = db.query(BusinessConfig).first()
    
    if not config:
        # Create default config if none exists
        config = BusinessConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
        
    return config

@router.put("/", response_model=ConfigResponse)
async def update_config(
    config_update: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update system configuration.
    Only accessible by ADMIN and OWNER roles.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires Admin or Owner privileges"
        )
        
    config = db.query(BusinessConfig).first()
    
    if not config:
        config = BusinessConfig()
        db.add(config)
    
    # Update fields
    for field, value in config_update.model_dump().items():
        setattr(config, field, value)
        
    db.commit()
    db.refresh(config)
    
    return config
