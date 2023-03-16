from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import users, bounding, post
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
#app.include_router(libros.router)
app.include_router(bounding.router)
app.include_router(post.router)

app.mount("/static", StaticFiles(directory="static"),
                                 name="static")

@app.get("/")
async def home():
    return "hola FastAPI"