from fastapi import HTTPException, status

class AlgunasExceptions:
    credentials_exception_global = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )