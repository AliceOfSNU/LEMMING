from typing import List, NamedTuple, Tuple
from .base import Prompter
class Llama2JPPrompter(Prompter):
    def __init__(self) -> None:
        super().__init__()
        
    def prompt_generate_sentences(self, word:str) -> List[str]:
        # few shot learning(in context learning) with instruction + examples
        SYSTEM_WARMUP = "あなたは誠実で優秀な日本人のアシスタントです。"
        INSTRUCTION = "make three sentences in Japanese using the word {word}."
        EXAMPLE = \
            "1. 新しい環境に慣れるのには時間がかかります。\n"\
            "2. 毎日練習して、次第に英語を話すことに慣れてきました。\n"\
            "3. 韓国での生活にもすぐに慣れました。\n"
        prompts = [
            {"role": "system", "content": SYSTEM_WARMUP},
            {"role": "user", "content": INSTRUCTION.format(word="慣れる")},
            {"role": "assistant", "content": EXAMPLE},
            {"role": "user", "content": INSTRUCTION.format(word=word)},
        ]
        return prompts
        
class Llama3JPPrompter(Prompter):
    def __init__(self) -> None:
        super().__init__()
        
    def prompt_generate_sentences(self, word:str) -> List[str]:
        # few shot learning(in context learning) with instruction + examples
        SYSTEM_WARMUP = "あなたは誠実で優秀な日本人のアシスタントです。特に指示が無い場合は、常に日本語で回答してください。"
        INSTRUCTION = "『{word}』を使って例文を3つ作ってください。"
        EXAMPLE = \
            "1. 新しい環境に慣れるのには時間がかかります。\n"\
            "2. 毎日練習して、次第に英語を話すことに慣れてきました。\n"\
            "3. 韓国での生活にもすぐに慣れました。\n"
        prompts = [
            {"role": "system", "content": SYSTEM_WARMUP},
            {"role": "user", "content": INSTRUCTION.format(word="慣れる")},
            {"role": "assistant", "content": EXAMPLE},
            {"role": "user", "content": INSTRUCTION.format(word=word)},
        ]
        return prompts