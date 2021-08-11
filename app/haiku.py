import re
import os
import threading
import atexit
import logging
import markovify
from flask import Flask, render_template, jsonify
from hyphenate import hyphenate_word
import redis
from waitress import serve


logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%d-%b-%y %H:%M:%S")

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST"),
    port=os.environ.get("REDIS_PORT"),
    charset="utf-8",
    decode_responses=True,
)

with open("linus.txt") as f:
    text = f.read()


text_model = markovify.Text(text)
max_retries = 10000


def capitalize(sentence):
    return re.sub(r"([\w+])", lambda x: x.groups()[0].upper(), sentence, 1, re.UNICODE)

@app.route('/health')
def health_check():
    try:
        redis_client.ping()
        return jsonify({'status': 'up', 'redis': 'connected'}), 200
    except redis.exceptions.ConnectionError:
        return jsonify({'status': 'down', 'redis': 'disconnected'}), 503


@app.route("/")
def haiku():
    first = redis_client.srandmember("linus5")
    second = redis_client.srandmember("linus7")
    third = redis_client.srandmember("linus5")
    return render_template("index.html", haiku=[first, second, third])


def generate_haiku():
    def get_haiku_lines():
        expected_syllables = [5, 7]

        app.logger.info(f"Starting {max_retries} iterations to generate haiku lines")
        for i in range(max_retries):
            sentence = text_model.make_short_sentence(
                25, min_words=2, max_words=10, test_output=False
            )
            if sentence:
                sentence = capitalize(re.sub(".$", "", sentence))
                tokens = [hyphenate_word(token) for token in sentence.split()]
                syllables = sum([len(token) for token in tokens])
                if syllables in expected_syllables:
                    redis_client.sadd(f"linus{syllables}", sentence)
        app.logger.info(
            f"Done. Current counts: "
            f"5 syllables {redis_client.scard('linus5')}, "
            f"7 syllables {redis_client.scard('linus7')}"
        )

    get_haiku_lines()

    haiku_thread = threading.Timer(3600, generate_haiku, ())
    haiku_thread.start()


def init_thread():
    global haiku_thread
    haiku_thread = threading.Timer(0, generate_haiku, ())
    haiku_thread.start()


def interrupt():
    global haiku_thread
    haiku_thread.cancel()


if __name__ == "__main__":
    init_thread()
    atexit.register(interrupt)
    serve(app, host="0.0.0.0", port=5000)
