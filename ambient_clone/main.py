from fastapi import FastAPI

from ambient_clone.routers import auth, data, users

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(data.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
