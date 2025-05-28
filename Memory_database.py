import uuid
import sqlite3, os
from datetime import datetime

from transformers import Tool
import sqlite3
import uuid
import os
from datetime import datetime

class MessageDatabase_remote():
    def __init__(self):
        self.conn = None
        self.c = None
        self.create_table()

    def connect(self):
        import mysql.connector
        # 透過環境變數讀取 MySQL 連線參數，避免硬編碼敏感資訊
        mysql_host = os.getenv('MYSQL_HOST', 'your_mysql_host')
        mysql_user = os.getenv('MYSQL_USER', 'your_mysql_user')
        mysql_password = os.getenv('MYSQL_PASSWORD', 'your_mysql_password')
        mysql_port = int(os.getenv('MYSQL_PORT', '3306'))
        self.conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            port=mysql_port,
            charset='utf8mb4'
        )
        # 使用 dictionary=True 以返回字典格式
        self.c = self.conn.cursor(dictionary=True)

    def create_table(self):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            session_id TEXT NOT NULL,
            group_id TEXT NOT NULL, 
            role TEXT NOT NULL, 
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        ) CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
        ''')
        self.close()

    def add_message(self, session_id, group_id, role, content):
        timestamp = datetime.now().isoformat()
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        INSERT INTO messages (session_id, group_id, role, content, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ''', (session_id, group_id, role, content, timestamp))
        self.conn.commit()
        self.close()

    def get_messages_by_session(self, session_id):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=%s
        ''', (session_id,))
        retrieved_messages = [{"role": role, "content": content} for role, content, timestamp in self.c.fetchall()]
        self.close()
        return retrieved_messages
    
    def get_messages_by_group(self, session_id, group_id):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=%s AND group_id=%s
        ''', (session_id, group_id))
        retrieved_messages = [{"role": role, "content": content} for role, content, timestamp in self.c.fetchall()]
        self.close()
        return retrieved_messages
        
    def get_last_messages(self, session_id, group_id):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=%s AND group_id=%s
        ORDER BY id DESC LIMIT 2
        ''', (session_id, group_id))
        results = self.c.fetchall()
        messages = []
        if results:
            for r in reversed(results):
                messages.append({"role": r['role'], "content": r['content'], "timestamp": r['timestamp']})
            self.close()
            return messages
        self.close()
        return None

    def delete_messages_by_session(self, session_id):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        DELETE FROM messages WHERE session_id=%s
        ''', (session_id,))
        self.conn.commit()
        self.close()

    def delete_messages_by_group(self, session_id, group_id):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        DELETE FROM messages WHERE session_id=%s AND group_id=%s
        ''', (session_id, group_id))
        self.conn.commit()
        self.close()

    def delete_all_messages(self):
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute('''
        DELETE FROM messages
        ''')
        self.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.c = None

    # 提供游標與連線物件的屬性
    @property
    def cursor(self):
        return self.c

    @property
    def connection(self):
        return self.conn

    # 新增：取得對話的系統訊息（role = 'system'），作為對話名稱
    def get_system_message(self, session_id, group_id):
        sql = """
        SELECT id, content FROM messages 
        WHERE session_id=%s AND group_id=%s AND role='system'
        ORDER BY id ASC LIMIT 1
        """
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute(sql, (session_id, group_id))
        result = self.c.fetchone()
        self.close()
        return result

    # 新增：更新對話的系統訊息內容
    def update_system_message(self, session_id, group_id, new_content):
        sys_msg = self.get_system_message(session_id, group_id)
        if not sys_msg:
            return
        sql = "UPDATE messages SET content=%s WHERE id=%s"
        self.connect()
        self.c.execute('USE demo_db')
        self.c.execute(sql, (new_content, sys_msg['id']))
        self.conn.commit()
        self.close()

# 其他版本（v2 與 Call_memory_tool）保持不變
# 以下程式碼與您的原始內容保持不動
class MessageDatabase_v2:
    def __init__(self, db_path='../database/chat_messages.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.c = None
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')

    def add_message(self, session_id, role, content):
        timestamp = datetime.now().isoformat()
        self.c.execute('''
        INSERT INTO messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (session_id, role, content, timestamp))
        self.conn.commit()

    def get_messages_by_session(self, session_id):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ''', (session_id,))
        retrieved_messages = [{"role": role, "content": content} for role, content, timestamp in self.c.fetchall()]
        return retrieved_messages
        
    def get_last_messages(self, session_id):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ORDER BY id DESC LIMIT 2
        ''', (session_id,))
        results = self.c.fetchall()
        if results:
            messages = []
            for role, content, timestamp in reversed(results):
                messages.append({"role": role, "content": content, "timestamp": timestamp})
            return messages
        return None

    def delete_messages_by_session(self, session_id):
        self.c.execute('''
        DELETE FROM messages WHERE session_id=?
        ''', (session_id,))
        self.conn.commit()

    def delete_all_messages(self):
        self.c.execute('''
        DELETE FROM messages
        ''')
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.c = None
            
class MessageDatabase:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.c = None
        self.session_id = None
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')

    def add_message(self, role, content):
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        self.c.execute('''
        INSERT INTO messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (self.session_id, role, content, timestamp))
        self.conn.commit()

    def get_messages_by_session(self):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ''', (self.session_id,))
        retrieved_messages = [{"role": role, "content": content} for role, content, timestamp in self.c.fetchall()]
        return retrieved_messages

    def get_last_message(self):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ORDER BY id DESC LIMIT 1
        ''', (self.session_id,))
        result = self.c.fetchone()
        if result:
            role, content, timestamp = result
            return {"role": role, "content": content, "timestamp": timestamp}
        return None

    def last_role_is_user(self):
        self.c.execute('''
        SELECT role FROM messages WHERE session_id=?
        ORDER BY id DESC LIMIT 1
        ''', (self.session_id,))
        result = self.c.fetchone()
        if result and result[0] == 'user':
            return True
        return False

    def get_last_user_and_assistant_messages(self):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ORDER BY id DESC LIMIT 2
        ''', (self.session_id,))
        results = self.c.fetchall()
        if len(results) == 2:
            return [
                {"role": results[1][0], "content": results[1][1], "timestamp": results[1][2]},
                {"role": results[0][0], "content": results[0][1], "timestamp": results[0][2]}
            ]
        return None

    def delete_messages_by_session(self):
        self.c.execute('''
        DELETE FROM messages WHERE session_id=?
        ''', (self.session_id,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.c = None

class Call_memory_tool(Tool):
    name = "Call_memory_tool"
    description = f"""Call_memory_tool"""
    inputs = {
        "query": {
            "type": "string",
            "description": f"Use the query string to call the related messages from memory database",
        }
    }
    output_type = "string"
    
    def __init__(self, llmsearch_engine, **kwargs):
        super().__init__(**kwargs)
        self.db = MessageDatabase(db_path="/data/myfcu/EARMP_AI/earmp_2025/database/chat_messages.db")
        self.llmsearch_engine = llmsearch_engine

    def set_session_id(self, session_id):
        self.db.session_id = session_id
        return self.db.session_id
    
    def add_message(self, id, text):
        self.db.connect()
        self.db.add_message(id, text)
        self.db.close()

    def get_last_user_and_assistant_messages(self):
        self.db.connect()
        result = str(self.db.get_last_user_and_assistant_messages())
        self.db.close()
        return result

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a session_id"
        self.db.connect()
        outquery = str(self.db.get_messages_by_session())
        self.db.close()
        if outquery=='[]':
            return 'No record found'
        messages = [
            {"role": "user", "content": f"""您將獲得一篇長文訊息。現在，訊息開始：
- **訊息內容：** {outquery}

訊息到此結束。

接下來，請按照給予的指示完成任務。
你會得到一個與訊息相關的問題。

### 問題：{query}
### 指示：
1.你對所有訊息有一個大致的理解。
2. 線索應以文字片段的形式呈現，這些片段將有助於回答問題。
3. 輸出只線索。
4. 請用中文回答。
5.根據訊息的內容，直接回答問題。如果沒有絕對相關資料，請回覆無紀錄。
6. 不要包含答案以外的任何額外內容。
"""}
        ]
        outquery = self.llmsearch_engine.generate_text(messages)
        return outquery

class SQLiteDatabase:
    def __init__(self, db_path='chat_db.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.c = None
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def add_message(self, session_id, role, content):
        timestamp = datetime.now().isoformat()
        self.c.execute('''
        INSERT INTO messages (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (session_id, role, content, timestamp))
        self.conn.commit()

    def get_messages_by_session(self, session_id):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages WHERE session_id=?
        ''', (session_id,))
        return [{"role": role, "content": content, "timestamp": timestamp}
                for role, content, timestamp in self.c.fetchall()]

    def get_last_messages(self, session_id, limit=2):
        self.c.execute('''
        SELECT role, content, timestamp FROM messages
        WHERE session_id=?
        ORDER BY id DESC LIMIT ?
        ''', (session_id, limit))
        results = self.c.fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]}
                for r in reversed(results)]

class InspectionDatabase:
    def __init__(self, db_path='inspection.db'):
        import os
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        self.db_path = db_path
        self.conn = None
        self.c = None
        self.connect()
        self.create_table()

    def connect(self):
        import sqlite3
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS gear_inspection_data_static_inspection (
            id INTEGER PRIMARY KEY,
            inspector TEXT,
            inspection_date TIMESTAMP,
            inspection_order_number TEXT,
            work_number TEXT,
            workstation_number TEXT,
            part_number TEXT,
            part_name TEXT,
            specification TEXT,
            measurement_data TEXT,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def add_inspection(self, inspector, inspection_date, inspection_order_number,
                       work_number, workstation_number, part_number,
                       part_name, specification, measurement_data):
        self.c.execute('''
        INSERT INTO gear_inspection_data_static_inspection (
            inspector, inspection_date, inspection_order_number,
            work_number, workstation_number, part_number,
            part_name, specification, measurement_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inspector, inspection_date, inspection_order_number,
            work_number, workstation_number, part_number,
            part_name, specification, measurement_data
        ))
        self.conn.commit()

    def get_inspection_by_id(self, record_id):
        self.c.execute('''
        SELECT * FROM gear_inspection_data_static_inspection WHERE id=?
        ''', (record_id,))
        row = self.c.fetchone()
        return row

    def get_inspections_by_inspector(self, inspector):
        self.c.execute('''
        SELECT * FROM gear_inspection_data_static_inspection WHERE inspector=?
        ''', (inspector,))
        return self.c.fetchall()

    def delete_inspection_by_id(self, record_id):
        self.c.execute('''
        DELETE FROM gear_inspection_data_static_inspection WHERE id=?
        ''', (record_id,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.c = None

class InspectionDatabasePostgres:
    def __init__(self, dsn):
        # dsn 範例："dbname=test user=postgres password=secret host=localhost port=5432"
        self.dsn = dsn
        self.conn = None
        self.c = None
        self.connect()
        self.create_table()

    def connect(self):
        import psycopg2
        self.conn = psycopg2.connect(self.dsn)
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS gear_inspection_data_static_inspection (
            id SERIAL PRIMARY KEY,
            inspector TEXT,
            inspection_date TIMESTAMP,
            inspection_order_number TEXT,
            work_number TEXT,
            workstation_number TEXT,
            part_number TEXT,
            part_name TEXT,
            specification TEXT,
            measurement_data TEXT,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def add_inspection(self, inspector, inspection_date, inspection_order_number,
                       work_number, workstation_number, part_number,
                       part_name, specification, measurement_data):
        self.c.execute('''
        INSERT INTO gear_inspection_data_static_inspection (
            inspector, inspection_date, inspection_order_number,
            work_number, workstation_number, part_number,
            part_name, specification, measurement_data
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            inspector, inspection_date, inspection_order_number,
            work_number, workstation_number, part_number,
            part_name, specification, measurement_data
        ))
        self.conn.commit()

    def get_inspection_by_id(self, record_id):
        self.c.execute('SELECT * FROM gear_inspection_data_static_inspection WHERE id=%s', (record_id,))
        return self.c.fetchone()

    def get_inspections_by_inspector(self, inspector):
        self.c.execute('SELECT * FROM gear_inspection_data_static_inspection WHERE inspector=%s', (inspector,))
        return self.c.fetchall()

    def delete_inspection_by_id(self, record_id):
        self.c.execute('DELETE FROM gear_inspection_data_static_inspection WHERE id=%s', (record_id,))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.c.close()
            self.conn.close()
            self.conn = None
            self.c = None
