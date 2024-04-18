#!/bin/bash
# -*- coding: utf-8 -*-
## シェルオプション
set -e           # コマンド実行に失敗したらエラー
set -u           # 未定義の変数にアクセスしたらエラー
set -o pipefail  # パイプのコマンドが失敗したらエラー（bashのみ）

ip=$1

echo ${ip}


(
cd ../
 . venv/bin/activate

 gnome-terminal --title="voicevox_server" -- bash -ic "python3 akari_chatgpt_bot/voicevox_server.py --voicevox_local --voicevox_host ${ip}"
 gnome-terminal --title="dify_publisher" -- bash -ic "python3 dify_publisher.py"
 gnome-terminal --title="speech_publisher" -- bash -ic "python3 akari_chatgpt_bot/speech_publisher.py --timeout 0.8"
)
