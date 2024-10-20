# this file contains tests that checks the generation pipeline,
# both for sentences and paragrpahs, works properly.

from typing import List, Dict
import os
import csv
import asyncio
import Lemming
import time

TEST_OUTPUT_DIR = "unittests/outputs"
def write_to_csv(title: str, data: List[List[str]]):
    with open(os.path.join(TEST_OUTPUT_DIR, title), "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)


async def test_generate_sentences():
    words = ["動く","移す","話す","抱く"]
    await asyncio.sleep(1.0)
    data = [["word", "sentence"]]

    lemming = Lemming.LemmingService()

    # create some tasks
    tasks = []
    startup = time.time()
    for i in range(50):
        tasks.append(asyncio.create_task(lemming.generate_sentences("動く")))
        await asyncio.sleep(0.05)

    # wait for all tasks to complete
    tasks_results = await asyncio.gather(*tasks)

    # see results
    for results in tasks_results:
        print(results)

    await lemming.shutdown()

    sum = 0.0
    for t in lemming.durations:
        sum += t
    print(f"mean latency: {sum/len(lemming.durations)}")
    print(lemming.durations)

    sum = 0.0
    for bs in lemming.batch_sizes:
        sum += bs
    print(f"mean batch size: {sum/len(lemming.batch_sizes)}")
    print(lemming.batch_sizes)

    sum = 0.0
    for qs in lemming.q_sizes:
        sum += qs
    print(f"mean queue size: {sum/len(lemming.q_sizes)}")
    print(lemming.q_sizes)

def test_parser():
    import language.morphemes as morph
    sent = "『work』, 『you』を使って例文を3つ作ってください。"
    tagged = morph.get_morphemes(sent)
    tagged = morph.filter_trivial(tagged)
    for tag in tagged:
        print(tag)

def test_furigana():
    import language.morphemes as morph
    sent = "接続詞とは、品詞の一つで、自立語で活用がなく、文と文、節と節、句と句、語と語をつなぎそれらの関係を示す語です。"
    tagged = morph.get_morphemes(sent)
    tagged = morph.filter_trivial(tagged)
    tagged = morph.filter_kanji(tagged)
    furiganas = morph.get_yomi(tagged)
    for tag in furiganas:
        print(tag)

def test_lemmatization():
    import language.morphemes as morph
    from language.grammar import PartOfSpeech
    sent = "海が荒れて雷鳴がとどろくような時に, 単独で接続語になります"
    tagged = morph.get_morphemes(sent)
    tagged = morph.filter_trivial(tagged)
    tagged = morph.filter_pos(tagged, remove_pos=[PartOfSpeech.AUX_VERB, PartOfSpeech.NOUN_PARTICLE, PartOfSpeech.OTHER])
    dictforms = morph.get_dictform(tagged)
    for tag in dictforms:
        print(tag)
#if __name__ == "__main__":
#asyncio.run(test_generate_sentences())
#test_parser()
#test_furigana()
test_lemmatization()