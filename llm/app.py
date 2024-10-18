from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import List, Union

import Lemming

app = FastAPI()

# service
lemming = Lemming.LemmingService()

# models
class ParamsGenerateSentences(BaseModel):
    words: List[str]

class ResultGenerateSentences(BaseModel):
    count: int
    sentences: List[str]

# routes
@app.route("/")
async def hello_world():
    return "<p>Hello, Welcome to LEMMING 0.1</p>"

@app.post("/generate_sentences", response_model = list[ResultGenerateSentences])
async def generate_sentences_api(params: ParamsGenerateSentences):
    result = lemming.generate_sentences(params.words)
    return result

@app.post("/echo", response_model = list[str] )
async def echo_api(params: ParamsGenerateSentences):
    words = params.words
    return words