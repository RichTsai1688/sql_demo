# Tool + Agent 專案規劃

本專案旨在建置一套 Tool 與 Agent 架構，針對使用者輸入的任務（Task）自動解析並呼叫對應工具，實現齒輪檢驗記錄的管理與補足欄位檢查。

---

## 1. User Task → Memory_database Tool 指令映射

### 1.1 需求
使用者輸入自然語言任務，例如：
```
新增一筆檢驗記錄，檢驗者：Alice，檢驗時間：2025-05-28 09:30，
工單號：WO12345，工作站編號：WS-01，零件編號：P-987，
零件名稱：齒輪A，規格：外徑50mm，測量數據：49.98,50.02
```

### 1.2 解析邏輯
1. 以正則表達式或 LLM 將欄位值對應到：
   - `inspector`
   - `inspection_date`
   - `inspection_order_number`
   - `work_number`
   - `workstation_number`
   - `part_number`
   - `part_name`
   - `specification`
   - `measurement_data`
2. 構造對應 Python 呼叫：
   ```python
   insp_db = InspectionDatabase(db_path='...')
   insp_db.add_inspection(
       inspector, inspection_date, inspection_order_number,
       work_number, workstation_number, part_number,
       part_name, specification, measurement_data
   )
   ```

---

## 2. Ollama Client

**初始化 Ollama Client**：  
```python
import os
from ollama import Client
# 從環境變數讀取 Ollama 服務地址，避免硬編碼
ollama_host = os.getenv('OLLAMA_HOST', 'your_ollama_host:port')
client = Client(host=ollama_host)
```

- **範例：串流回應**  
```python
for chunk in client.chat(
        model='gemma3:4b-it-qat',
        messages=[{'role':'user','content':'我今天工作了6小時'}],
        stream=True):
    print(chunk.message.content, end='', flush=True)
```

---

## 3. 欄位完整性檢查功能

### 3.1 功能說明
檢查使用者任務中是否缺少檢驗記錄所需欄位，並回饋缺失列表。

### 3.2 實作要點
1. 欄位清單：
   ```python
   required_fields = [
       'inspector', 'inspection_date', 'inspection_order_number',
       'work_number', 'workstation_number', 'part_number',
       'part_name', 'specification', 'measurement_data'
   ]
   ```
2. 解析任務文本，逐一比對是否出現。
3. 回傳格式：
   ```json
   {
     "ok": false,
     "missing_fields": ["workstation_number", ...]
   }
   ```

---

**存檔路徑**：`/data/SQL_demo/tool_instruction.md`  
**更新日期**：2025-05-28
