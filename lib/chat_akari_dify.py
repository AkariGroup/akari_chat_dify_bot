import grpc
import json
import os
import sys
from typing import Generator, List, Union

from gpt_stream_parser import force_parse_json
from .dify_client.client import ChatClient

sys.path.append(os.path.join(os.path.dirname(__file__), "grpc"))
import motion_server_pb2
import motion_server_pb2_grpc

class ChatStreamAkariDify(object):
    """
    Difyを使用して会話を行うためのクラス。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        motion_host: str = "127.0.0.1",
        motion_port: str = "50055",
    ) -> None:
        """クラスの初期化メソッド。

        Args:
            api_key (str): 使用するDifyのアプリのAPI key。
            base_url (str): 使用するDifyのアプリのBase URL。
            motion_host (str, optional): モーションサーバーのホスト名。デフォルトは"127.0.0.1"。
            motion_port (str, optional): モーションサーバーのポート番号。デフォルトは"50055"。
        """

        self.last_char = ["、", "。", "！", "!", "?", "？", "\n", "}"]
        self.api_key = api_key
        self.base_url = base_url
        self.chat_client = ChatClient(self.api_key, self.base_url)
        motion_channel = grpc.insecure_channel(motion_host + ":" + motion_port)
        self.motion_stub = motion_server_pb2_grpc.MotionServerServiceStub(
            motion_channel
        )
        self.cur_motion_name = ""

    def chat(self, query: str) -> Generator[str, None, None]:
        """Difyを使用して会話を行う。

        Args:
            query (str): 会話のquery入力。現在はquery textの入力のみサポート。

        Returns:
            Generator[str, None, None]): 返答を順次生成する。現状はtext出力のみサポート。

        """
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
                ans = line.get("answer")
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

    def send_reserved_motion(self) -> bool:
        """予約されたモーションを送信するメソッド。

        Returns:
            bool: モーションが送信されたかどうかを示すブール値。

        """
        print(f"send motion {self.cur_motion_name}")
        if self.cur_motion_name == "":
            try:
                self.motion_stub.ClearMotion(motion_server_pb2.ClearMotionRequest())
            except BaseException:
                print("Failed to send to motion server")
            return False
        try:
            self.motion_stub.SetMotion(
                motion_server_pb2.SetMotionRequest(
                    name=self.cur_motion_name, priority=3, repeat=False, clear=True
                )
            )
            self.cur_motion_name = ""
        except BaseException:
            print("setMotion error!")
            return False
        return True
