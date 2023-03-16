from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from datetime import datetime
from core import Firestore
import http

router = APIRouter(tags=['inboundig'])



class Email(BaseModel):
    email: str
    date: datetime = datetime.utcnow()


class Click(BaseModel):
    count: int
    date: datetime = datetime.utcnow()


@router.post("/email/{email}", status_code=http.HTTPStatus.OK)
async def email(email: str, request: Request):
    ip = request.client.host
    search = Firestore()
    search.escribir('inbounding', email,  {'email': email,
                                           'date': datetime.utcnow(),
                                           'ip': ip})
    research = search.consulta('inbounding', 'email', '==', email)
    if research is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se guardo el email"
        )
    return research[email]
