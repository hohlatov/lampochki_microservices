from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import schemas
import security


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login", response_model=schemas.TokenResponse)
@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest):

    if not security.authenticate_user(
        data.login,
        data.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = security.create_access_token({
        "sub": data.login,
        "role": "admin"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }