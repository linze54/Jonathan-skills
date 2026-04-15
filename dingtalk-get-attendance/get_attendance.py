#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉企业内部应用 - 批量获取考勤打卡记录
API: POST https://oapi.dingtalk.com/attendance/list
限制: 每次最多 50 个 userid，日期跨度最多 31 天
"""

import os
import sys
import csv
import json
import argparse
import time
from datetime import datetime, timedelta
import requests

# ── 配置 ───────────────────────────────────────────────────────────────────

def load_env_file():
    # 先找同目录 .env，再找 send-file 旁边的 .env（共用凭证）
    candidates = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", "dingtalk-send-file", ".env"),
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())
            break

load_env_file()

CORPID     = os.environ.get("DINGTALK_CORPID", "")
CORPSECRET = os.environ.get("DINGTALK_CORPSECRET", "")
BASE_URL   = "https://oapi.dingtalk.com"

BATCH_USER  = 50   # 每批最多 50 个用户
PAGE_SIZE   = 50   # 每页记录数

# ── API 封装 ───────────────────────────────────────────────────────────────

def get_access_token() -> str:
    resp = requests.get(
        f"{BASE_URL}/gettoken",
        params={"corpid": CORPID, "corpsecret": CORPSECRET},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"获取 access_token 失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
    return data["access_token"]


def get_all_userids(access_token: str) -> list:
    """获取企业全部在职员工 userid 列表"""
    url = f"{BASE_URL}/topapi/smartwork/hrm/employee/queryonjob"
    userids = []
    offset = 0
    size = 50
    while True:
        payload = {"status_list": "2,3,5", "offset": offset, "size": size}
        resp = requests.post(
            url,
            params={"access_token": access_token},
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode", 0) != 0:
            raise RuntimeError(f"获取员工列表失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
        result = data.get("result", {})
        page_list = result.get("data_list", [])
        userids.extend([u["userid"] for u in page_list])
        if not result.get("next_cursor"):
            break
        offset += size
        time.sleep(0.2)
    return userids


def get_user_names(access_token: str, userids: list) -> dict:
    """批量获取用户姓名，返回 {userid: name}"""
    names = {}
    for i in range(0, len(userids), 100):
        batch = userids[i:i+100]
        resp = requests.post(
            f"{BASE_URL}/topapi/v2/user/listbyid",
            params={"access_token": access_token},
            json={"userids": ",".join(batch)},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for u in data.get("result", {}).get("list", []):
            names[u["userid"]] = u.get("name", "")
        time.sleep(0.2)
    return names


def fetch_attendance(access_token: str, userids: list, date_from: str, date_to: str) -> list:
    """
    分批拉取考勤记录。
    date_from / date_to 格式: YYYY-MM-DD
    返回所有打卡记录列表。
    """
    url = f"{BASE_URL}/attendance/list"
    all_records = []

    # 按 BATCH_USER 分批
    for i in range(0, len(userids), BATCH_USER):
        batch_ids = userids[i:i+BATCH_USER]
        offset = 0
        while True:
            payload = {
                "workDateFrom": f"{date_from} 00:00:00",
                "workDateTo":   f"{date_to} 23:59:59",
                "userIdList":   batch_ids,
                "offset":       offset,
                "limit":        PAGE_SIZE,
                "isI18n":       False,
            }
            resp = requests.post(
                url,
                params={"access_token": access_token},
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("errcode", 0) != 0:
                raise RuntimeError(f"获取考勤记录失败: {data.get('errmsg')} (errcode={data.get('errcode')})")

            records = data.get("recordresult", [])
            all_records.extend(records)

            if not data.get("hasMore", False):
                break
            offset += PAGE_SIZE
            time.sleep(0.1)

        print(f"  已处理 {min(i + BATCH_USER, len(userids))}/{len(userids)} 人...", flush=True)
        time.sleep(0.2)

    return all_records


# ── 输出 CSV ───────────────────────────────────────────────────────────────

FIELDS = [
    ("userId",         "员工ID"),
    ("userName",       "员工姓名"),
    ("workDate",       "考勤日期"),
    ("checkTime",      "打卡时间"),
    ("checkType",      "打卡类型"),
    ("locationResult", "位置结果"),
    ("approveId",      "审批单ID"),
    ("sourceType",     "打卡来源"),
    ("planId",         "排班ID"),
    ("planCheckTime",  "计划打卡时间"),
    ("timeResult",     "时间结果"),
]

def write_csv(records: list, names: dict, output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([cn for _, cn in FIELDS])
        for r in records:
            uid = r.get("userId", "")
            row = []
            for key, _ in FIELDS:
                if key == "userName":
                    row.append(names.get(uid, ""))
                else:
                    row.append(r.get(key, ""))
            writer.writerow(row)


# ── 主流程 ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="批量获取钉钉考勤打卡记录")
    parser.add_argument("--date-from", required=True, help="开始日期 YYYY-MM-DD")
    parser.add_argument("--date-to",   required=True, help="结束日期 YYYY-MM-DD")
    parser.add_argument("--userids",   default="",    help="指定 userid，逗号分隔；留空则拉取全员")
    parser.add_argument("--output",    default="",    help="输出 CSV 路径，默认当前目录")
    args = parser.parse_args()

    # 校验配置
    missing = [k for k, v in [("DINGTALK_CORPID", CORPID), ("DINGTALK_CORPSECRET", CORPSECRET)] if not v]
    if missing:
        print(f"[错误] 缺少环境变量: {', '.join(missing)}")
        sys.exit(1)

    # 校验日期
    try:
        d_from = datetime.strptime(args.date_from, "%Y-%m-%d")
        d_to   = datetime.strptime(args.date_to,   "%Y-%m-%d")
    except ValueError:
        print("[错误] 日期格式应为 YYYY-MM-DD")
        sys.exit(1)
    if (d_to - d_from).days > 30:
        print("[错误] 单次查询日期跨度不能超过 31 天")
        sys.exit(1)
    if d_to < d_from:
        print("[错误] 结束日期不能早于开始日期")
        sys.exit(1)

    # 默认输出路径
    output = args.output or f"attendance_{args.date_from}_{args.date_to}.csv".replace("-", "")

    print(f"[1/4] 获取 access_token ...")
    token = get_access_token()

    # 确定 userid 列表
    if args.userids.strip():
        userids = [u.strip() for u in args.userids.split(",") if u.strip()]
        print(f"[2/4] 使用指定用户 {len(userids)} 人")
    else:
        print(f"[2/4] 获取全员在职员工列表 ...")
        userids = get_all_userids(token)
        print(f"      共 {len(userids)} 人")

    print(f"[3/4] 获取员工姓名 ...")
    names = get_user_names(token, userids)

    print(f"[4/4] 拉取考勤记录 {args.date_from} ~ {args.date_to} ...")
    records = fetch_attendance(token, userids, args.date_from, args.date_to)

    write_csv(records, names, output)
    print(f"\n[完成] 共 {len(records)} 条记录，已保存到: {output}")


if __name__ == "__main__":
    main()
