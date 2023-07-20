from fastapi import FastAPI, Path
from typing import Annotated 
from starlette import status

app = FastAPI()

@app.get("/hello/{name}", status_code = status.HTTP_200_OK)
async def hello_word(name: Annotated[str, Path(min_length=3)]) -> str:
    return f"Hello {name.capitalize()}"

