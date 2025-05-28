"""
FastAPI 服務主程式：HTTP 接口與 Agent 邏輯
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from Memory_database import InspectionDatabasePostgres
from field_checker import parse_inspection_text, check_required_fields
from ollama_client import OllamaClient

# 初始化 FastAPI
app = FastAPI(title="LLM Agent 檢驗資料管理系統")

# 環境變數讀取 DSN
DEFAULT_DSN = os.getenv('INSPECTION_DSN', 'dbname=test_gear user=postgres password=secret host=localhost port=5432')
# 建立資料庫工具
db_tool = InspectionDatabasePostgres(dsn=DEFAULT_DSN)
# 建立 LLM 客戶端
llm_client = OllamaClient()

# Pydantic models
class SensorData(BaseModel):
    inspector: str
    inspection_date: str  # ISO 格式
    inspection_order_number: str
    work_number: str
    workstation_number: str
    part_number: str
    part_name: str
    specification: str
    measurement_data: str

class TaskRequest(BaseModel):
    text: str

class TaskResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
    missing_fields: Optional[List[str]] = None

@app.post('/sensor/upload', response_model=TaskResponse)
def sensor_upload(data: SensorData):
    """
    接收機台感測資料，直接存入 PostgreSQL
    """
    try:
        db_tool.add_inspection(
            data.inspector, data.inspection_date, data.inspection_order_number,
            data.work_number, data.workstation_number, data.part_number,
            data.part_name, data.specification, data.measurement_data
        )
        return TaskResponse(ok=True, message="Sensor data stored successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/task/submit', response_model=TaskResponse)
def task_submit(req: TaskRequest):
    """
    接收使用者文字任務，解析欄位後檢查並存儲，或回報缺少欄位
    """
    text = req.text
    parsed = parse_inspection_text(text)
    missing = check_required_fields(parsed)
    if missing:
        return TaskResponse(ok=False, missing_fields=missing,
                            message=f"Missing fields: {missing}")
    # 所有欄位齊全，進行存儲
    try:
        db_tool.add_inspection(
            parsed['inspector'], parsed['inspection_date'], parsed['inspection_order_number'],
            parsed['work_number'], parsed['workstation_number'], parsed['part_number'],
            parsed['part_name'], parsed['specification'], parsed['measurement_data']
        )
        return TaskResponse(ok=True, message="Task processed and data stored.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
