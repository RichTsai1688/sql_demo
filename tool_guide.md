# 工具使用指南

本指南介紹專案中的核心工具 `Memory_database.py` 及其他相關記憶體與資料庫操作工具的使用方式。

---

## 1. 核心工具：MessageDatabase

`MessageDatabase` 位於 `Memory_database.py`，提供本地 SQLite 資料庫的訊息儲存與擷取功能。

### 1.1 初始化
```python
from Memory_database import MessageDatabase

# 指定資料庫檔案路徑（會自動建立資料夾）
mdb = MessageDatabase(db_path='/data/SQL_demo/test_db.db')
```

### 1.2 設定 Session
```python
# 設定目前會話 ID
mdb.session_id = 'your_session_id'
```

### 1.3 新增訊息
```python
mdb.add_message(role='user', content='Hello, world!')
```

### 1.4 讀取訊息
- 擷取所有訊息：
```python
msgs = mdb.get_messages_by_session()
```
- 取得最新一筆訊息：
```python
last = mdb.get_last_message()
```
- 取得最新使用者與助理各一筆：
```python
pair = mdb.get_last_user_and_assistant_messages()
```

### 1.5 刪除訊息
```python
mdb.delete_messages_by_session()
```

---

## 2. 遠端版工具：MessageDatabase_remote

連接到 MySQL（或 MariaDB） 的遠端資料庫示例。

### 2.1 初始化與連線
```python
from Memory_database import MessageDatabase_remote

mdb = MessageDatabase_remote()
```

### 2.2 新增訊息
```python
mdb.add_message(
    session_id='session_123',
    group_id='group_abc',
    role='system',
    content='系統初始化完成'
)
```

### 2.3 擷取訊息
- 擷取所有指定 session 與 group：
```python
msgs = mdb.get_messages_by_group('session_123', 'group_abc')
```
- 擷取最後兩筆：
```python
latest = mdb.get_last_messages('session_123', 'group_abc')
```

### 2.4 系統訊息管理
- 讀取系統訊息：
```python
sys_msg = mdb.get_system_message('session_123', 'group_abc')
```
- 更新系統訊息內容：
```python
mdb.update_system_message('session_123', 'group_abc', new_content='更新後內容')
```

---

## 3. 簡化版工具：MessageDatabase_v2

另一個本地 SQLite 實作，較輕量，功能簡化。

### 基本流程
```python
from Memory_database import MessageDatabase_v2

mdb2 = MessageDatabase_v2(db_path='/data/SQL_demo/db_v2.db')
# 新增
mdb2.add_message('sessionA', 'user', 'Hello V2')
# 讀取
mdb2.get_messages_by_session('sessionA')
# 取得最後兩筆
mdb2.get_last_messages('sessionA')
# 刪除
mdb2.delete_messages_by_session('sessionA')
```

---

## 4. 記憶體工具：Call_memory_tool

結合 LLM search 引擎，將會話記憶轉成 prompt 片段。

### 使用步驟
```python
# 建立工具實例
tool = Call_memory_tool(llmsearch_engine=your_llm)
# 設定 session
tool.set_session_id('sessionA')
# 取得片段（查詢）
clues = tool.forward(query='我要的資訊是什麼？')
```

---

## 5. 通用 SQLite 工具：SQLiteDatabase

最簡單的 ORM-like 封裝，用於快速測試。

### 範例
```python
from Memory_database import SQLiteDatabase

db = SQLiteDatabase(db_path='chat_db.db')
db.add_message('sessX', 'bot', 'Hi')
msgs = db.get_messages_by_session('sessX')
```

---

**存檔路徑**：`/data/SQL_demo/tool_guide.md`  
**更新日期**：2025-05-28
