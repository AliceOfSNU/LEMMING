import MeCab
from collections import namedtuple
from typing import List
import re 
import language.grammar as grammar

tagger = MeCab.Tagger("--node-format=%f%m")
TaggedWord = namedtuple('TaggedWord', 'word, yomi, dictform, pos, start')
YomiWord = namedtuple('YomiWord', 'word, yomi, start')
LemmaWord = namedtuple('LemmaWord', 'word, dictform, start')

def get_morphemes(sent: str) -> List[TaggedWord]:
    parts = tagger.parse(sent)
    parts = parts.split('\n')
    tagged = []
    begin = 0
    for line in parts:
        t = line.split('\t')
        word = t[0]
        idx = sent.find(word, begin)
        begin += len(word)
        if len(t) >= 5:
            tagged.append(TaggedWord(word=word, yomi=t[1], dictform=t[3], pos=t[4], start=idx))
    return tagged

def filter_trivial(tagged: List[TaggedWord]):
    # remove whitespaces, numbers, and special characters.
    filtered = []
    for t in tagged:
        # filter whitespace and special characters
        if re.match("[\s\-!?.,:;<=>\"'@#$%^&*/+()[\]`{|}~0-9A-Za-z]", t.word) is not None: continue
        # filter japanese sentence markers and quotes
        if any(c in t.word for c in ['。', '、', '『', '』']): continue
        filtered.append(t)
    return filtered

def filter_kanji(tagged: List[TaggedWord]) -> List[TaggedWord]:
    # filter only morphemes that contain a kanji character.
    kanji = r'[㐀-䶵一-鿋豈-頻]'
    l_haskanji = []
    for t in tagged:
        if not re.match(kanji, t.word): continue
        l_haskanji.append(t)
    return l_haskanji

def filter_pos(tagged: List[TaggedWord], remove_pos = []):
    # remove certain part of speech, to reduce cluttering
    l_filtered = []
    for t in tagged:
        pos = grammar.parse_from_mecab_pos_str(t.pos)
        if pos in remove_pos: continue
        l_filtered.append(t)
    return l_filtered

def get_yomi(tagged: List[TaggedWord]) -> List[YomiWord]:
    return [YomiWord(word=t.word, yomi=t.yomi, start=t.start) for t in tagged]

def get_dictform(tagged: List[TaggedWord]) -> List[LemmaWord]:
    return [LemmaWord(word=t.word, dictform=t.dictform, start=t.start) for t in tagged]