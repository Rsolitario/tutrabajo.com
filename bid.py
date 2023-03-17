from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from core import Firestore
from datetime import datetime, timedelta
from users import get_current_active_user, User
import json
import uuid
import algunas_exc


class Bid(BaseModel):
    post_owner_id: str
    description: str  # detalles y los pasos
    milestone: dict
    status: bool
    submitdate: str = datetime.now()
    period: int
    amount: float
    author_bid: str | None


class BidDataHide(Bid):
    bidder_id: str | None
    skills: str


router = APIRouter(tags=['Bid'])


def tool_list(arg: dict):
    content = list(map(lambda x: x, arg.keys()))
    return str(content[0])


@router.post('/api/v1/bids/')
async def post(item: Bid,
               current_user: User = Depends(get_current_active_user)):
    user = Firestore()
    id = uuid.uuid1()
    data = item.dict()
    data['bidder_id'] = id.__str__()
    data['skills'] = None       # cambiar por las habilidades del usuario
    data['author_bid'] = current_user.email
    current_post = user.consulta(
        'post', 'post_id', '==', data['post_owner_id'])
    response_query = current_post
    post_id = tool_list(response_query)
    author = response_query[post_id]['author']
    user.writeCollections('users', current_user.email,
                          'bids', data['bidder_id'], data)
    print(current_post)
    #current_post[post_id]['bids'].append(data)
    user.writeCollections('post', data['post_owner_id'], 'bids', data['bidder_id'], data)
    user.write_collections_3('users', author,
                          'post', data['post_owner_id'], 'bids', data['bidder_id'], data)
    return json.dumps(current_post)
