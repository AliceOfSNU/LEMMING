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

lemming = Lemming.LemmingService()

async def test_generate_sentences():
    words = ["動く","移す","話す","抱く"]
    await asyncio.sleep(1.0)
    data = [["word", "sentence"]]

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

async def test_parse_quiz():
    sent = """#出力形式に従って、4択式のクイズを作成します。
#問題1:
問題: マイクロプラスチックは、どのようなプラスチック片のことですか?
選択肢:
1. 大きなプラスチック片
2. 5ミリメートル以下の小さなプラスチック片
3. 使用済みのプラスチック片
4. 新品のプラスチック片
問題2:
マイクロプラスチックは、どのような経路で人体に摂取されることが懸念されていますか。

選択肢:
1. 空気中の浮遊物を吸引すること
2. 水道水や海産物を通じて
3. 食物連鎖を通じて海洋生物を食べること
4. 工業廃棄物を直接摂取すること"""

    # Expected output 
    # 
    # [{
    #   "question": "マイクロプラスチックは、どのようなプラスチック片のことですか"
    #   "choices": [
    #       "大きなプラスチック片",
    #       "5ミリメートル以下の小さなプラスチック片",
    #       ... ]
    # },
    # { .. }]
    
    pipeline = GenerativeQuizPipeline(lemming.generate)
    output = pipeline.parser.parse(sent)
    print(output)

async def test_reading_pipeline():
    # make
    quizbuilder = ReadingComprehensionPipeline(lemming.generate)
    quiz = await quizbuilder.generate("マイクロプラスチック")
    await lemming.shutdown()





#if __name__ == "__main__":
#asyncio.run(test_generate_sentences())
#test_parser()
#test_furigana()
#test_lemmatization()
#test_parse_quiz