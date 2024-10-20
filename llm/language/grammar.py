import re
from enum import Enum

class PartOfSpeech(Enum):
    NOUN = 1 #名詞
    VERB = 2 #動詞
    ADJ = 3 #形容詞
    ADV = 4 #副詞
    NOUN_PARTICLE = 5   #助詞
    CONJUNCTION = 6     #接続詞
    AUX_VERB = 7        #助動詞
    ADNOMINAL = 8       #連体詞
    INTERJECTION = 9    #感動詞
    SUFFIX = 10         #接尾辞
    PREFIX = 11         #接頭詞
    OTHER = 12          #*

pos_to_enum = {
    "名詞": PartOfSpeech.NOUN,
    "動詞": PartOfSpeech.VERB,
    "形容詞": PartOfSpeech.ADJ,
    "副詞": PartOfSpeech.ADV,
    "助詞": PartOfSpeech.NOUN_PARTICLE,
    "接続詞" : PartOfSpeech.CONJUNCTION,
    "助動詞" : PartOfSpeech.AUX_VERB,
    "連体詞" : PartOfSpeech.ADNOMINAL,
    "感動詞" : PartOfSpeech.INTERJECTION,
    "接尾辞" : PartOfSpeech.SUFFIX,
    "接頭詞" : PartOfSpeech.PREFIX,
}

def parse_from_mecab_pos_str(pos_str :str) -> PartOfSpeech:
    category = pos_str.split('-')[0]
    if category in pos_to_enum.keys():
        return pos_to_enum[category]
    else:
        return PartOfSpeech.OTHER
    
