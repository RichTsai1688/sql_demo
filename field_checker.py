"""
欄位解析與完整性檢查模組
提供將使用者自然語言任務轉為欄位字典，並檢查缺失欄位。
"""
import re
from datetime import datetime

# 定義必填欄位
required_fields = [
    'inspector', 'inspection_date', 'inspection_order_number',
    'work_number', 'workstation_number', 'part_number',
    'part_name', 'specification', 'measurement_data'
]

# 欄位對應中文關鍵字
field_patterns = {
    'inspector': r'檢驗者[:：]\s*(?P<value>[^，,]+)',
    'inspection_date': r'檢驗時間[:：]\s*(?P<value>[^，,]+)',
    'inspection_order_number': r'工單號[:：]\s*(?P<value>[^，,]+)',
    'work_number': r'工作號(?:碼)?[:：]\s*(?P<value>[^，,]+)',
    'workstation_number': r'工作站編號[:：]\s*(?P<value>[^，,]+)',
    'part_number': r'零件編號[:：]\s*(?P<value>[^，,]+)',
    'part_name': r'零件名稱[:：]\s*(?P<value>[^，,]+)',
    'specification': r'規格[:：]\s*(?P<value>[^，,]+)',
    'measurement_data': r'測量數據[:：]\s*(?P<value>[^，,]+)'
}


def parse_inspection_text(text: str) -> dict:
    """
    解析使用者文字，提取各欄位值。
    """
    result = {}
    for field, pattern in field_patterns.items():
        match = re.search(pattern, text)
        if match:
            value = match.group('value').strip()
            # 若是日期欄位，嘗試解析為 datetime
            if field == 'inspection_date':
                try:
                    # 支援常見格式
                    result[field] = datetime.fromisoformat(value)
                except Exception:
                    result[field] = value
            else:
                result[field] = value
    return result


def check_required_fields(parsed: dict) -> list:
    """
    檢查 parsed 是否缺少必要欄位，回傳缺失欄位清單。
    """
    missing = [f for f in required_fields if f not in parsed or not parsed.get(f)]
    return missing
