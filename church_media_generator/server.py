from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Church Media Generator API is running"}