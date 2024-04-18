import argparse
import json
import time
import os

from lib.chat_akari_dify import ChatStreamAkariDify
from akari_chatgpt_bot.lib.voicevox import TextToVoiceVox

voicevox = False  # 音声合成を使う場合Trueに変更
DIFY_CONFIG_PATH = (
    f"{os.path.dirname(os.path.realpath(__file__))}/config/dify_config.json"
)


def main() -> None:
    if not os.path.isfile(DIFY_CONFIG_PATH):
        print(f"Dify setting file path is not available.")
        return
    api_key: str = ""
    base_url: str = ""
    with open(DIFY_CONFIG_PATH, "r") as dify_json:
        dify_config = json.load(dify_json)
        if "api_key" in dify_config:
            if dify_config["api_key"] != "":
                api_key = dify_config["api_key"]
            else:
                print(f"api_key not found in config/dify_config.json")
                return
        else:
            print(f"api_key not found in config/dify_config.json")
            return
        if "base_url" in dify_config:
            if dify_config["base_url"] != "":
                base_url = dify_config["base_url"]
            else:
                print(f"base_url not found in config/dify_config.json")
                return
        else:
            print(f"base_url not found in config/dify_config.json")
            return
    chat_stream_akri_dify = ChatStreamAkariDify(api_key=api_key, base_url=base_url)
    while True:
        print("文章をキーボード入力後、Enterを押してください。")
        text = input("Input: ")
        # userメッセージの追加
        print(f"User   : {text}")
        print("Dify: ")
        response = ""
        start = time.time()
        for sentence in chat_stream_akri_dify.chat(text):
            response += sentence
            print(sentence, end="", flush=True)
        interval = time.time() - start
        print("")
        print("-------------------------")
        print(f"time: {interval:.2f} [s]")
        print("")


if __name__ == "__main__":
    main()
