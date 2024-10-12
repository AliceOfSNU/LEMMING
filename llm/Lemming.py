from prompt.Llama2JP_prompter import Llama2JPPrompter
from model.Llama2JPModel import Llama2JPModel
from typing import List, NamedTuple, Tuple
import re

class LemmingService:
    def __init__(self):
        self.model = Llama2JPModel()
        self.prompter = Llama2JPPrompter(self.model.tokenizer)

        # run warmup
        _ = self.model.generate(self.prompter.warmup_prompt())

    def generate_sentences(self, words: List[str]) -> List[dict]:
        results = []
        for word in words:
            prompt = self.prompter.prompt_generate_sentences(word)
            model_output = self.model.generate(prompt)
            # extract actual sentences from generated output
            sentences = re.split("\n[0-9][. ]*", model_output)
            sentences = [sent.strip() for sent in sentences[1:]]
            # place the sentences into a result object, and append that object to list
            results.append({"count": len(sentences), "sentences": sentences})
        return results

    def generate_paragraph(self, subject: List[str]) -> List[dict]:
        raise NotImplementedError()
    
