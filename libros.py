from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from core import Firestore
from users import get_current_active_user, User
from core import Pdf2txt
from datetime import datetime
from pdf2image.exceptions import PDFPageCountError

router = APIRouter(tags=['Documents'])


class Book(BaseModel):
    title: str
    content: str | None
    create_time: datetime = datetime.utcnow()
    user_upload: str | None
    email_upload: str | None


def search_book(title: str):
    return Firestore().consulta('books', 'title', '==', title)

def http_exception_400(exc:str):
    return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc
        )


@router.post('/create')
async def create_book_user(book: Book, path: str, current_user: User = Depends(get_current_active_user)):
    if search_book(book.title):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="El titulo ya se encuentra disponible"
        )
    try:
        Firestore().escribir('books', book.title, {'content': Pdf2txt('static/' + path).convert(),
                                               'title': book.title,
                                               'create_time': book.create_time, 
                                               'user_upload': current_user.username,
                                               'email_upload': current_user.email})
    except PDFPageCountError:
        raise http_exception_400(
            "Couldn't open"
        )
    if not search_book(book.title):
        raise http_exception_400(
            "No se registro el libro"
        )
    title = search_book(book.title)
    return Book(**title[book.title])
