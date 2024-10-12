# this file contains tests that checks the generation pipeline,
# both for sentences and paragrpahs, works properly.

from typing import List, Dict
import os
import csv

import Lemming

TEST_OUTPUT_DIR = "unittests/outputs"
def write_to_csv(title: str, data: List[List[str]]):
    with open(os.path.join(TEST_OUTPUT_DIR, title), "w") as f:
        writer = csv.writer(f)
        writer.writerows(data)

lemming = Lemming.LemmingService()

def test_generate_sentences():
    words = ["動く","移す","話す","抱く"]
    result = lemming.generate_sentences(words)
    data = [["word", "sentence"]]
    assert len(result) == len(words)
    for (word, res) in zip(words, result):
        assert res["count"] == len(res["sentences"])
        for sent in res["sentences"]:
            data.append([word, sent])
    write_to_csv("test_generate_sentences.csv", data)

#if __name__ == "__main__":
test_generate_sentences()

