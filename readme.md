# 專案說明：LLM Agent 與檢驗資料管理系統

本專案旨在建置一套可接收感測資料、使用者文字指令，並透過 LLM Agent 解析後將檢驗記錄存入資料庫的系統。

## 目錄結構
```
/data/SQL_demo
│
├─ Memory_database.py        # 資料庫工具：SQLite / MySQL / PostgreSQL 操作類別
├─ ollama_client.py         # Ollama LLM 客戶端封裝
├─ field_checker.py         # 欄位解析與完整性檢查模組
├─ agent_app.py             # FastAPI 服務主程式：HTTP 接口與 Agent 邏輯
├─ client_service.py        # CLI 客戶端服務：呼叫 Agent API
├─ requirements.txt         # Python 依賴套件清單
│
├─ tool_guide.md            # 使用者工具指南（Memory_database 等工具使用方式）
├─ tool_instruction.md      # 工具指令映射與場景流程說明
├─ planning.md              # 專案規劃文件：目標、架構與開發步驟
│
├─ demo.ipynb               # 本地 SQLite 範例 Notebook
├─ demo_remote.ipynb        # 遠端 MySQL 範例 Notebook
│
└─ readme.md                # 本檔案：專案介紹與檔案結構說明
```

## 各檔案說明

### 1. Memory_database.py
- 定義多種資料庫操作類別：
  - `MessageDatabase` / `MessageDatabase_v2`: 本地 SQLite 訊息儲存工具
  - `MessageDatabase_remote`: 遠端 MySQL 訊息操作
  - `SQLiteDatabase`: 簡易 ORM-like SQLite 工具
  - `InspectionDatabase`: SQLite 版齒輪檢驗記錄工具
  - `InspectionDatabasePostgres`: PostgreSQL 版檢驗記錄工具

### 2. ollama_client.py
- 封裝 Ollama LLM API `Client`，提供 `chat` 方法串流與請求。

### 3. field_checker.py
- 定義 `required_fields` 與解析函式，將使用者自然語言任務轉為欄位字典，並回傳缺失欄位列表。

### 4. agent_app.py
- FastAPI Web 應用程式入口
- 定義以下 Endpoint：
  - `/sensor/upload`：接收機台感測資料，呼叫 `InspectionDatabasePostgres` 存儲
  - `/task/submit`：接收使用者文字任務，解析欄位後檢查並存儲，或回報缺少欄位

### 5. requirements.txt
- 定義專案相依套件，例如：
  ```text
  fastapi
  uvicorn[standard]
  psycopg2-binary
  transformers
  ollama-python
  ```

### 6. Documentation
- `tool_guide.md`：工具使用指南
- `tool_instruction.md`：指令映射與流程說明
- `planning.md`：專案規劃與時程表

## 快速啟動
1. 建立虛擬環境並安裝依賴：
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. 啟動服務：
   ```bash
   uvicorn agent_app:app --reload --host 0.0.0.0 --port 8000
   ```
3. 訪問文件：
   - Swagger UI: http://localhost:8000/docs
   - Redoc: http://localhost:8000/redoc

## CLI 客戶端使用
可使用 `client_service.py` 透過終端機呼叫 Agent 服務：
```bash
# 上傳感測資料範例
env AGENT_API_URL=http://localhost:8000 python client_service.py sensor-upload \
  --inspector Alice --inspection-date "2025-05-28T09:30:00" \
  --inspection-order-number WO12345 --work-number WN001 \
  --workstation-number WS-01 --part-number P-987 \
  --part-name 齒輪A --specification "外徑50mm" \
  --measurement-data "49.98,50.02"

# 提交文字任務範例
env AGENT_API_URL=http://localhost:8000 python client_service.py task-submit \
  --text "新增一筆檢驗記錄，檢驗者：Bob，檢驗時間：2025-05-28 10:00，..."
```

---

**更新日期**：2025-05-28
