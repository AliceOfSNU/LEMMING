from .base import Prompter
class Llama2JPPrompter(Prompter):
    def __init__(self, tokenizer) -> None:
        super().__init__()
        self.tokenizer = tokenizer
        # add chat_template
        llama_2_template = \
            "{% for message in messages %}" \
                "{% if message['role'] == 'user' %}"  \
                    "{{ bos_token + '[INST] ' + message['content'].strip() + ' [/INST] ' }}"\
                "{% elif message['role'] == 'system' %}"\
                    "{{ '<<SYS>>\\n' + message['content'].strip() + '\\n<</SYS>>\\n\\n' }}"\
                "{% elif message['role'] == 'assistant' %}"\
                    "{{ ' '  + message['content'].strip() + ' ' + eos_token }}"\
                "{% endif %}"\
            "{% endfor %}"
        self.tokenizer.chat_template = llama_2_template
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
        
    def prompt_generate_sentences_fewshot(self, word:str) -> str:
        # few shot learning(in context learning) with instruction + examples
        SYSTEM_WARMUP = "あなたは誠実で優秀な日本人のアシスタントです。"
        INSTRUCTION = "make three sentences in Japanese using the word {word}."
        EXAMPLE = \
            "1. 新しい環境に慣れるのには時間がかかります。\n"\
            "2. 毎日練習して、次第に英語を話すことに慣れてきました。\n"\
            "3. 韓国での生活にもすぐに慣れました。\n"
        chats = [
            {"role": "system", "content": SYSTEM_WARMUP},
            {"role": "user", "content": INSTRUCTION.format(word="慣れる")},
            {"role": "assistant", "content": EXAMPLE},
            {"role": "user", "content": INSTRUCTION.format(word=word)},
        ]
        return self.tokenizer.apply_chat_template(chats, tokenize=False)
        
    