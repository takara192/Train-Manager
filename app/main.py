from fastapi import FastAPI
from common.database import lifespan
from routes import  user_route, ticket_route, check_in_out_route
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:63342",
    "http://localhost:63343",
    "http://localhost:63344",
    "http://localhost:63345",
]

app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_route.router)

app.include_router(ticket_route.router)

app.include_router(check_in_out_route.router)