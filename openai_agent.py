"""
使用 OpenAI Agents Python 架構所建立的 Agent
包含兩個工具：感測資料上傳 與 文字任務提交
"""
import os
from openai_agents import Agent, Tool
from openai_agents.models.litellm import LiteLLM
from typing import Any, Dict, List

from ollama_client import OllamaClient
from Memory_database import InspectionDatabasePostgres
from field_checker import parse_inspection_text, check_required_fields

# 初始化 LLM（LiteLLM 包裝 OllamaClient）
ollama_host = os.getenv('OLLAMA_HOST', 'your_ollama_host:port')
ollama = OllamaClient(host=ollama_host)
llm = LiteLLM(backend=ollama)

# 初始化資料庫工具
dsn = os.getenv('INSPECTION_DSN', 'dbname=test_gear user=postgres password=secret host=localhost port=5432')
db_tool = InspectionDatabasePostgres(dsn=dsn)

# 定義感測資料上傳工具
class SensorUploadTool(Tool):
    name = "sensor_upload"
    description = "上傳機台感測資料至資料庫"

    def run(self, arguments: Dict[str, Any]) -> str:
        data = arguments
        db_tool.add_inspection(
            data['inspector'], data['inspection_date'], data['inspection_order_number'],
            data['work_number'], data['workstation_number'], data['part_number'],
            data['part_name'], data['specification'], data['measurement_data']
        )
        return "Sensor data stored successfully"

# 定義文字任務提交工具
class TaskSubmitTool(Tool):
    name = "task_submit"
    description = "解析使用者文字任務並存儲，或回報缺失欄位"

    def run(self, arguments: Dict[str, Any]) -> str:
        text = arguments.get('text', '')
        parsed = parse_inspection_text(text)
        missing = check_required_fields(parsed)
        if missing:
            return f"Missing fields: {missing}"
        db_tool.add_inspection(
            parsed['inspector'], parsed['inspection_date'], parsed['inspection_order_number'],
            parsed['work_number'], parsed['workstation_number'], parsed['part_number'],
            parsed['part_name'], parsed['specification'], parsed['measurement_data']
        )
        return "Task processed and data stored"

# 組裝 Agent
tools: List[Tool] = [SensorUploadTool(), TaskSubmitTool()]
agent = Agent(llm=llm, tools=tools)  

if __name__ == '__main__':
    # CLI 測試範例
    result = agent.run(input_text="請上傳一筆檢驗記錄，檢驗者：Alice...工單號：WO123")
    print(result)
