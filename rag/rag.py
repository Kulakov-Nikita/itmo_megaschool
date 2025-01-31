from rag.searcher import Searcher
from rag.summarizer import Summarizer
import re

class RAG:
    def __init__(self, seacher_folder_id, seacher_api_token, sammarizer_api_token):
        self.searcher = Searcher(FOLDER_ID=seacher_folder_id, API_TOKEN=seacher_api_token)
        self.summarizer = Summarizer(api_token=sammarizer_api_token)

    def process(self, question: str) -> tuple[str, int, list[str]]:
        answer_text, links = self.searcher.search(question)
        if re.findall(r"\d+\s*[.:;,-]\s*", question):
            self.summarizer.process(question, answer_text)
            print("\n=================\n")
            return answer_text, self.summarizer.get_result(), links
        else:
            return answer_text, -1, links