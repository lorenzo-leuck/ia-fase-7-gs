"""
Modelo de Usuário
Integração: Banco de Dados + Python + Cybersecurity
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """
    Roles de usuário para RBAC
    """
    USER = "user"  # Colaborador
    MANAGER = "manager"  # Gestor
    ADMIN = "admin"  # Administrador/RH


class User(Base):
    """
    Modelo de Usuário
    
    Armazena informações de autenticação e perfil
    Senhas são armazenadas com hash bcrypt (nunca em texto plano)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    wellbeing_records = relationship("WellbeingRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
