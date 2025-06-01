# MCP(Model Context Protocol)で配信者(Streamer)をサポートするプロジェクト
Windowsで動かす想定です。

## 機能一覧
 - 全画面キャプチャ
 - Window名の一覧を取得
 - 指定されたWindowのscreen captureを取得
 - OBSのシーンの切り替え
 - OBSのテキスト更新
 - 現在時刻の取得
 - 指定時間待つ
 - 音声の読み上げ
 - ダイアログの表示
 
## 準備
必要なライブラリ
```shell
fastmcp
openai
pywin32
mss
Pillow
pydub
sounddevice
numpy
obsws-python
```

https://www.gyan.dev/ffmpeg/builds/

から ffmpeg-release-essentials.zip をダウンロードが必要。
展開してできたffmpeg.exeとffprobe.exeをパスの通ったフォルダに置く。



https://github.com/remsky/Kokoro-FastAPI

音声の読み上げはKokoro-FastAPIがローカルで動いている想定です。
WSL上でコンテナで動かす場合のコマンドラインは下記です。
```
$ docker run --rm -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

## 実行
stdioでこのMCPを実行します。

## 想定プロンプト
```
TODO
```