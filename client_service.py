"""
CLI 客戶端服務，用於呼叫 Agent API。
"""
import argparse
import requests
import os

# 服務地址，可從環境變數覆蓋
BASE_URL = os.getenv('AGENT_API_URL', 'http://localhost:8000')


def sensor_upload(args):
    url = f"{BASE_URL}/sensor/upload"
    payload = {
        "inspector": args.inspector,
        "inspection_date": args.inspection_date,
        "inspection_order_number": args.inspection_order_number,
        "work_number": args.work_number,
        "workstation_number": args.workstation_number,
        "part_number": args.part_number,
        "part_name": args.part_name,
        "specification": args.specification,
        "measurement_data": args.measurement_data
    }
    r = requests.post(url, json=payload)
    print(r.json())


def task_submit(args):
    url = f"{BASE_URL}/task/submit"
    payload = {"text": args.text}
    r = requests.post(url, json=payload)
    print(r.json())


def main():
    parser = argparse.ArgumentParser(description="LLM Agent CLI 客戶端")
    subparsers = parser.add_subparsers(dest='command')

    # 感測資料上傳
    sensor_parser = subparsers.add_parser('sensor-upload', help='上傳機台感測資料')
    sensor_parser.add_argument('--inspector', required=True, help='檢驗者名稱')
    sensor_parser.add_argument('--inspection-date', required=True, help='檢驗時間 (ISO 格式)')
    sensor_parser.add_argument('--inspection-order-number', required=True, help='工單號')
    sensor_parser.add_argument('--work-number', required=True, help='工作編號')
    sensor_parser.add_argument('--workstation-number', required=True, help='工作站編號')
    sensor_parser.add_argument('--part-number', required=True, help='零件編號')
    sensor_parser.add_argument('--part-name', required=True, help='零件名稱')
    sensor_parser.add_argument('--specification', required=True, help='規格')
    sensor_parser.add_argument('--measurement-data', required=True, help='測量數據')

    # 使用者任務提交
    task_parser = subparsers.add_parser('task-submit', help='提交文字任務')
    task_parser.add_argument('--text', required=True, help='任務文字描述')

    args = parser.parse_args()
    if args.command == 'sensor-upload':
        sensor_upload(args)
    elif args.command == 'task-submit':
        task_submit(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
