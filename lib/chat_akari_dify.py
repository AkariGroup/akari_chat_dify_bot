import json
import os
import sys
from typing import Generator, List, Union

from gpt_stream_parser import force_parse_json
from .dify_client.client import ChatClient


class ChatStreamAkariDify(object):
    """
    Difyを使用して会話を行うためのクラス。
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        """クラスの初期化メソッド。"""

        self.last_char = ["、", "。", "！", "!", "?", "？", "\n", "}"]
        self.api_key = api_key
        self.base_url = base_url
        self.chat_client = ChatClient(self.api_key, self.base_url)

    def chat(self, query: str) -> Generator[str, None, None]:
        # Create Chat Message using ChatClient
        chat_response = self.chat_client.create_chat_message(
            inputs={}, query=query, user="user_id", response_mode="streaming"
        )
        chat_response.raise_for_status()
        full_response = ""
        real_time_response = ""
        for line in chat_response.iter_lines(decode_unicode=True):
            line = line.split("data:", 1)[-1]
            if line.strip():
                line = json.loads(line.strip())
                ans = line.get('answer')
                if ans is not None:
                    full_response += ans
                    real_time_response += ans
                    for index, char in enumerate(real_time_response):
                        if char in self.last_char:
                            pos = index + 1  # 区切り位置
                            sentence = real_time_response[:pos]  # 1文の区切り
                            real_time_response = real_time_response[pos:]  # 残りの部分
                            # 1文完成ごとにテキストを読み上げる(遅延時間短縮のため)
                            yield sentence
                            break
                        else:
                            pass
        yield real_time_response
