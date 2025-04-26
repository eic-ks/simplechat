# lambda/index.py
import json
import os
import re  # 正規表現モジュールをインポート
import urllib.request

def lambda_handler(event, context):
    try:
  
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)
        print("Using model:", "my_model")
        
        # 会話履歴を使用
        messages = conversation_history.copy()

        # ユーザーメッセージを追加
        messages.append({
            "role": "user",
            "content": message
        })
        
        # 独自APIサーバー用のリクエストペイロード
        request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
        req = urllib.request.Request(
            f"{NGROK_URL}/generate",
            json=request_payload
        )
        request_payload_json = json.dumps(request_payload).encode()
        req = urllib.request.Request(
            f"{NGROK_URL}/generate",
            request_payload_json,
            headers={'Content-Type': 'application/json'}
        )

        # APIを呼び出し
        # レスポンスを解析
        try:
            with urllib.request.urlopen(req) as response:
              response_body = json.loads(response.read().decode('utf-8'))
        
        #応答の検証
        except urllib.error.HTTPError as err:
            print(err.code)
        except urllib.error.URLError as err:
            print(err.reason)
        
        # アシスタントの応答を取得
        assistant_response = response_body['generated_text']
        
        # アシスタントの応答を会話履歴に追加
        messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
