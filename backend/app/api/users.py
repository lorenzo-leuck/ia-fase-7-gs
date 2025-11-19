"""
Endpoints de Usuários
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna perfil do usuário autenticado"""
    user_id = int(user['sub'])
    db_user = db.query(User).filter(User.id == user_id).first()
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role.value,
        "is_active": db_user.is_active
    }
