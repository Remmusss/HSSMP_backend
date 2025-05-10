from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta, UTC, date
from typing import Any, Dict, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt


def response(code=200, status="success", message="", data="", metadata={}):
    return JSONResponse(
        jsonable_encoder(
            {
                "status": status, 
                "message": message, 
                "data": data, 
                "metadata": metadata}
        ),
        status_code=code,
    )

# SECRET_KEY = "sao-cung-duoc"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)


# # JWT token functions
# def create_access_token(
#     data: Dict[str, Any], expires_delta: Optional[timedelta] = None
# ) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(UTC) + (
#         expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def decode_jwt_token(token):
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         return None


# def auto_serialize(obj):
#     if isinstance(obj, list):
#         return [auto_serialize(item) for item in obj]
#     elif isinstance(obj, dict):
#         return {key: auto_serialize(value) for key, value in obj.items()}
#     elif isinstance(obj, (datetime, date)):
#         return obj.isoformat()
#     elif hasattr(obj, "__table__"):  # SQLAlchemy model
#         return {
#             col.name: auto_serialize(getattr(obj, col.name))
#             for col in obj.__table__.columns
#         }
#     else:
#         return obj


