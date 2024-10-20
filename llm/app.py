from fastapi import Body, FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Union

import Lemming
from language.morphemes import YomiWord, LemmaWord

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    app.state.lemming = Lemming.LemmingService()
    print("successfully init model")
    yield
    # on shutdown
    await app.state.lemming.shutdown() 
    print("successfully teared down model")

app = FastAPI(lifespan = lifespan)

# models
class ParamsGenerateSentences(BaseModel):
    word: str

class ResultGenerateSentences(BaseModel):
    count: int
    sentences: List[str]
    furiganas: List[List[YomiWord]]
    dictforms: List[List[LemmaWord]]

# routes
@app.route("/")
async def hello_world():
    return "<p>Hello, Welcome to LEMMING 0.1</p>"

@app.post("/generate_sentences", response_model = ResultGenerateSentences)
async def generate_sentences_api(params: ParamsGenerateSentences):
    result = await app.state.lemming.generate_sentences(params.word)
    result = await app.state.lemming.analyze_morphemes(result)
    if result["status"] == 0:
        result = {
            "count": len(result["sentences"]), 
            "sentences": result["sentences"],
            "furiganas": result["furiganas"],
            "dictforms": result["dictforms"]
        }
    else:
        raise HTTPException(status_code=504, detail="Server heavily loaded. maybe try later.")

    return result

@app.post("/echo", response_model = str )
async def echo_api(params: ParamsGenerateSentences):
    words = params.word
    return words


