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
        # create batch prompt
        prompts = []
        for word in words:
            prompts.append(self.prompter.prompt_generate_sentences(word))
        
        # run through model
        model_outputs = self.model.generate(prompts)

        # extract actual sentences from generated output
        results = []
        for output in model_outputs:
            sentences = re.split("\n[0-9][. ]*", output[0]["generated_text"])
            sentences = [sent.strip() for sent in sentences[1:]]
            # place the sentences into a result object, and append that object to list
            results.append({"count": len(sentences), "sentences": sentences})
        return results

    def generate_paragraph(self, subject: List[str]) -> List[dict]:
        raise NotImplementedError()
    
