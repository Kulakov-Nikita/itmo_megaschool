import requests
import json
import re


class Searcher:
    def __init__(self, FOLDER_ID, API_TOKEN):
        self.FOLDER_ID = FOLDER_ID
        self.API_TOKEN = API_TOKEN
        self.SEARCH_API_GENERATIVE = f"https://ya.ru/search/xml/generative?folderid={self.FOLDER_ID}"

    def search(self, question):
        headers = {"Authorization": f"Api-Key {self.API_TOKEN}"}
        data = {
                "messages": [
                {
                        "content": question,
                        "role": "user"
                    }
                ],
                "url": ""
            }

        response = requests.post(self.SEARCH_API_GENERATIVE, headers=headers, json=data)
        answer = json.loads(response.text)["message"]["content"]

        link_num = set()
        for i in re.findall(r"\[[0-9]*\]", answer):
            link_num.add(int(i[1:-1]))

        if len(link_num) > 3:
            link_num = list(link_num)[:3]
        else:
            link_num = list(link_num)


        all_links = json.loads(response.text)["links"]
        links = [all_links[i-1] for i in link_num]

        return answer, links
    