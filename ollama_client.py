"""
Ollama LLM 客戶端封裝
"""
from ollama import Client
import os

class OllamaClient:
    def __init__(self, host: str = None, model: str = 'gemma3:4b-it-qat'):
        """
        初始化 Ollama 客戶端
        :param host: Ollama 服務地址
        :param model: 要使用的模型名稱
        """
        # 從環境變數讀取 Ollama 服務地址，預設 None
        self.host = host or os.getenv('OLLAMA_HOST', 'your_ollama_host:port')
        self.client = Client(host=self.host)
        self.model = model

    def chat_stream(self, messages: list) -> str:
        """
        使用串流方式呼叫 Ollama，逐 chunk 回應並累積輸出
        :param messages: 對話訊息列表
        :return: 完整回應文字
        """
        content = ''
        for chunk in self.client.chat(model=self.model, messages=messages, stream=True):
            piece = chunk.message.content
            content += piece
            print(piece, end='', flush=True)
        return content

    def generate(self, messages: list) -> str:
        """
        使用非串流方式呼叫 Ollama，獲取完整回應
        :param messages: 對話訊息列表
        :return: 完整回應文字
        """
        response = self.client.chat(model=self.model, messages=messages)
        return response.message.content
