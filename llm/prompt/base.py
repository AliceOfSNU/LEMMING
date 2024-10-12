from typing import List

class Prompter:
    def __init__(self) -> None:
        pass
    
    # warmup model at application startup
    def warmup_prompt(self) -> str:
        pass

    def prompt_generate_sentences(self, word :str) -> str:
        pass

    def prompt_generate_paragraph(self, keyword:str) -> str:
        pass


