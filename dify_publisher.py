import argparse
import os
import sys
import json
from concurrent import futures

import grpc
from lib.chat_akari_dify import ChatStreamAkariDify

sys.path.append(os.path.join(os.path.dirname(__file__), "akari_chatgpt_bot/lib/grpc"))
import gpt_server_pb2
import gpt_server_pb2_grpc
import voice_server_pb2
import voice_server_pb2_grpc

DIFY_CONFIG_PATH = (
    f"{os.path.dirname(os.path.realpath(__file__))}/config/dify_config.json"
)


class DifyServer(gpt_server_pb2_grpc.GptServerServiceServicer):
    """
    Difyにtextを送信し、返答をvoice_serverに送るgprcサーバ
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self.chat_stream_akari_dify = ChatStreamAkariDify(api_key, base_url)
        voice_channel = grpc.insecure_channel("localhost:10002")
        self.stub = voice_server_pb2_grpc.VoiceServerServiceStub(voice_channel)

    def SetGpt(
        self, request: gpt_server_pb2.SetGptRequest(), context: grpc.ServicerContext
    ) -> gpt_server_pb2.SetGptReply:
        for sentence in self.chat_stream_akari_dify.chat(request.text):
            print(f"Send voice: {sentence}")
            self.stub.SetText(voice_server_pb2.SetTextRequest(text=sentence))
        print("")
        return gpt_server_pb2.SetGptReply(success=True)

    def SendMotion(
        self, request: gpt_server_pb2.SendMotionRequest(), context: grpc.ServicerContext
    ) -> gpt_server_pb2.SendMotionReply:
        success = self.chat_stream_akari_dify.send_reserved_motion()
        return gpt_server_pb2.SendMotionReply(success=success)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ip", help="Dify server ip address", default="127.0.0.1", type=str
    )
    parser.add_argument(
        "--port", help="Dify server port number", default="10001", type=str
    )
    args = parser.parse_args()

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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gpt_server_pb2_grpc.add_GptServerServiceServicer_to_server(
        DifyServer(api_key=api_key, base_url=base_url), server
    )
    server.add_insecure_port(args.ip + ":" + args.port)
    server.start()
    print(f"dify_publisher start. port: {args.port}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
