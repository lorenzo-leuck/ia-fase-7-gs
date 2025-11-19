"""
Módulo de Segurança (Cybersecurity)
- Autenticação JWT
- Criptografia de dados sensíveis
- Hashing de senhas
- RBAC (Role-Based Access Control)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import base64
import hashlib

from app.core.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

# Encryption for sensitive data (AES-256)
def get_cipher():
    """
    Cria cipher para criptografia simétrica
    Usa AES-256 via Fernet
    """
    # Garante que a chave tenha 32 bytes
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    key_base64 = base64.urlsafe_b64encode(key)
    return Fernet(key_base64)


# Password functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash bcrypt da senha
    """
    return pwd_context.hash(password)


# JWT Token functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria token JWT de acesso
    
    Args:
        data: Dados a serem incluídos no token (user_id, role, etc)
        expires_delta: Tempo de expiração customizado
    
    Returns:
        Token JWT assinado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Cria token JWT de refresh (vida longa)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT
    
    Returns:
        Payload do token
    
    Raises:
        HTTPException: Se token inválido ou expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Encryption functions for sensitive data
def encrypt_data(data: str) -> str:
    """
    Criptografa dados sensíveis (ex: informações de saúde)
    Usa AES-256 via Fernet
    
    Args:
        data: Dados em texto plano
    
    Returns:
        Dados criptografados em base64
    """
    cipher = get_cipher()
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Descriptografa dados sensíveis
    
    Args:
        encrypted_data: Dados criptografados
    
    Returns:
        Dados em texto plano
    """
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_data.encode())
    return decrypted.decode()


# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency para rotas protegidas
    Valida token JWT e retorna dados do usuário
    
    Args:
        credentials: Credenciais HTTP Bearer
    
    Returns:
        Dados do usuário do token
    
    Raises:
        HTTPException: Se token inválido
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    # Verifica se é token de acesso
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    
    return payload


# RBAC - Role-Based Access Control
def require_role(required_role: str):
    """
    Decorator para exigir role específica
    
    Usage:
        @app.get("/admin")
        async def admin_route(user = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = user.get("role", "user")
        
        # Hierarquia de roles: admin > manager > user
        role_hierarchy = {"admin": 3, "manager": 2, "user": 1}
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente"
            )
        
        return user
    
    return role_checker


# Data anonymization for analytics (LGPD/GDPR compliance)
def anonymize_user_data(user_id: int) -> str:
    """
    Anonimiza ID do usuário para análises agregadas
    Usa hash SHA-256 com salt
    
    Args:
        user_id: ID do usuário
    
    Returns:
        Hash anônimo do usuário
    """
    salt = settings.SECRET_KEY[:16]  # Usa parte da secret key como salt
    data = f"{user_id}{salt}".encode()
    return hashlib.sha256(data).hexdigest()[:16]
