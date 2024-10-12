from .base import Prompter
class Llama2JPPrompter(Prompter):
    def __init__(self, tokenizer) -> None:
        super().__init__()
        self.tokenizer = tokenizer
        self.INST_BEGIN_TOKEN, self.INST_END_TOKEN = "[INST]", "[/INST]"
        self.SYSTEM_BEGIN_TOKEN, self.SYSTEM_END_TOKEN = "<<SYS>>\n", "\n<</SYS>>\n\n"

    def warmup_prompt(self) -> str:
        SYSTEM_WARMUP = "あなたは誠実で優秀な日本人のアシスタントです。"
        return "{bos_token}{b_inst} {system}{e_inst} ".format(
            bos_token=self.tokenizer.bos_token,
            b_inst=self.INST_BEGIN_TOKEN,
            system=f"{self.SYSTEM_BEGIN_TOKEN}{SYSTEM_WARMUP}{self.SYSTEM_END_TOKEN}",
            e_inst=self.INST_END_TOKEN,
        )
    
    def warmup_generate_sentences(self) -> str:
        SYSTEM_WARMUP = "あなたは誠実で優秀な日本人のアシスタントです。"
        return "{bos_token}{b_inst} {system}{e_inst} ".format(
            bos_token=self.tokenizer.bos_token,
            b_inst=self.INST_BEGIN_TOKEN,
            system=f"{self.SYSTEM_BEGIN_TOKEN}{SYSTEM_WARMUP}{self.SYSTEM_END_TOKEN}",
            e_inst=self.INST_END_TOKEN,
        )

    def prompt_generate_sentences(self, word:str) -> str:
        prompt_format = "{bos_token}{b_inst} make three sentences in Japanese using the word {word}. {e_inst} "
        return prompt_format.format(
            bos_token=self.tokenizer.bos_token,
            b_inst=self.INST_BEGIN_TOKEN,
            word=word,
            e_inst=self.INST_END_TOKEN,
        )

    def warmup_generate_paragraph(self) -> str:
        return self.warmup_generate_sentences()

    def prompt_generate_paragraph(self, keyword:str) -> str:
        prompt_format = "{bos_token}{b_inst} write a short paragraph about {keyword}, using easy vocabulary. {e_inst} "
        return prompt_format.format(
            bos_token=self.tokenizer.bos_token,
            b_inst=self.INST_BEGIN_TOKEN,
            keyword = keyword,
            e_inst=self.INST_END_TOKEN,
        )
        

    