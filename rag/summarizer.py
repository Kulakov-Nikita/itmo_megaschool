import requests
import uuid
import json


class Summarizer:
    def __init__(self, api_token):
        self.api_token = api_token
        self.auth_key = 0
        self.result = ""

    def process(self):
        pass

    def auth(self):
        print("auth")
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload='scope=GIGACHAT_API_PERS'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid1()),
        'Authorization': f'Basic {self.api_token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)

        self.auth_key = json.loads(response.text)["access_token"]


    def process(self, question: str, answer: str):
        if self.send_message(f"Вопрос: {question}\n Ответ: {answer}\n Напиши только одно число, соответствующее номеру правильного ответа.") == 1:
            self.auth()
            self.send_message(f"Вопрос: {question}\n Ответ: {answer}\n Напиши только одно число, соответствующее номеру правильного ответа.")

    
    def get_result(self) -> str:
        print(f"GigaChat len: {len(json.loads(self.result))}")
        return json.loads(self.result)["choices"][0]["message"]["content"]

    def send_message(self, message: str) -> int:
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

        payload = json.dumps({
        "model": "GigaChat",
        "messages": [
            {
            "role": "user",
            "content": message
            }
        ],
        "stream": False,
        "repetition_penalty": 1
        })
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.auth_key}'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        try:
            if json.loads(response.text)["status"] == 401:
                return 1
        except Exception as e:
            print(e)
        finally:
            self.result = response.text
