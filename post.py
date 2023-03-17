from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from core import Firestore
from datetime import datetime, timedelta
from users import get_current_active_user, User
import json
import uuid
import algunas_exc


class Post(BaseModel):
    types: str  # fixed project, hourly project, employer job, local jobs
    title: str  # nombre
    description: str  # detalles y los pasos
    skills: str  # habilidades
    how_to_pay: str  # fixed amount, hourly rate
    budget: str  # Presupuesto estimado
    # funciones pagas adicionales para mejorar la experiencia.
    upgrades: str | None
    date_time: str = datetime.utcnow()


class PostDataHide(Post):
    post_id: str | None
    author: str | None


router = APIRouter(tags=['publications'])


def tool_list(arg: dict):
    return list(map(lambda x: x, arg.keys()))


@router.post('/api/v1/post/')
async def post(item: Post,
               current_user: User = Depends(get_current_active_user)):
    user = Firestore()
    id = uuid.uuid1()
    data = {'post_id': id.__str__(),
            'title': item.title,
            'types': item.types,
            'description': item.description,
            'skills': item.skills,
            'how_to_pay': item.how_to_pay,
            'budget': item.budget,
            'upgrades': item.upgrades,
            'author': current_user.email,
            'date_time': item.date_time}
    user.escribir('post', id.__str__(), data)
    user.writeCollections('users', current_user.email,
                          'post', id.__str__(), data)
    response = user.consulta('post', 'post_id', '==', id.__str__())
    return json.dumps(response)


@router.get('/api/v1/post/{post_id}')
async def get_post_id(post_id: str,
                      current_user: User = Depends(get_current_active_user)):
    post = Firestore()
    response = post.consulta('post', 'post_id', '==', post_id)
    return json.dumps(response)


@router.delete("/api/v1/post/delete/{post_id}")
async def delete_post_id(post_id: str,
                         current_user: User = Depends(get_current_active_user)):
    post = Firestore()
    info = post.consulta('post', 'post_id', '==', post_id)
    id = list(map(lambda x: x, info.keys()))

    if info[id[0]]['author'] != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No estas autorizado para esta accion"
        )

    post.deleteDocument('post', post_id)
    post.deleteDocumentinCollections(
        'users', current_user.email, 'post', post_id)
    if post.consulta('post', 'post_id', '==', post_id):
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED, detail="No se pudo eliminar!"
        )
    return json.dumps({'post_id': post_id, 'status': 'Delete'})


@router.put("/api/v1/post/{post_id}")
async def update_post(post_id: str, item: Post, current_user: User = Depends(get_current_active_user)):
    post = Firestore()
    info = post.consulta('post', 'post_id', '==', post_id)
    id = tool_list(info)
    if info[id[0]]['author'] != current_user.email:
        raise algunas_exc.AlgunasExceptions().credentials_exception_global
    post_dict = item.dict()
    post_dict['post_id'] = post_id
    post_dict['author'] = current_user.email
    post.update_field_doc('post', post_id, post_dict)
    post.updateCollections('users', current_user.email,
                           'post', post_id, post_dict)
    return json.dumps(post_dict)
