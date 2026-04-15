#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉企业内部应用 - 发送文件脚本
支持发送到个人（userid）或群聊（chatid）
文件大小限制：≤20MB
"""

import os
import sys
import json
import argparse
import mimetypes
import requests

# ── 配置（优先读环境变量，其次读同目录 .env 文件）──────────────────────────

def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_env_file()

CORPID       = os.environ.get("DINGTALK_CORPID", "")
CORPSECRET   = os.environ.get("DINGTALK_CORPSECRET", "")
AGENT_ID     = os.environ.get("DINGTALK_AGENT_ID", "")

BASE_URL = "https://oapi.dingtalk.com"

# ── API 封装 ───────────────────────────────────────────────────────────────

def get_access_token() -> str:
    url = f"{BASE_URL}/gettoken"
    resp = requests.get(url, params={"corpid": CORPID, "corpsecret": CORPSECRET}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"获取 access_token 失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
    return data["access_token"]


def upload_media(access_token: str, file_path: str) -> str:
    """上传文件，返回 media_id（有效期 3 天）"""
    url = f"{BASE_URL}/media/upload"
    # 钉钉 media type：image / voice / video / file
    mime, _ = mimetypes.guess_type(file_path)
    media_type = "file"  # Word/Excel/PDF 等统一用 file
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    if file_size > 20 * 1024 * 1024:
        raise ValueError(f"文件大小 {file_size / 1024 / 1024:.1f}MB 超过钉钉 20MB 限制")

    with open(file_path, "rb") as f:
        files = {"media": (file_name, f, mime or "application/octet-stream")}
        resp = requests.post(
            url,
            params={"access_token": access_token, "type": media_type},
            files=files,
            timeout=60,
        )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"上传文件失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
    return data["media_id"]


def send_to_user(access_token: str, userid: str, media_id: str, file_name: str):
    """发送文件消息给个人（工作通知）"""
    url = f"{BASE_URL}/topapi/message/corpconversation/asyncsend_v2"
    payload = {
        "agent_id": int(AGENT_ID),
        "userid_list": userid,
        "msg": {
            "msgtype": "file",
            "file": {
                "media_id": media_id,
            },
        },
    }
    resp = requests.post(
        url,
        params={"access_token": access_token},
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"发送消息失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
    return data


def send_to_chat(access_token: str, chatid: str, media_id: str, file_name: str):
    """发送文件消息到群聊"""
    url = f"{BASE_URL}/chat/send"
    payload = {
        "chatid": chatid,
        "msg": {
            "msgtype": "file",
            "file": {
                "media_id": media_id,
            },
        },
    }
    resp = requests.post(
        url,
        params={"access_token": access_token},
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise RuntimeError(f"发送消息失败: {data.get('errmsg')} (errcode={data.get('errcode')})")
    return data

# ── 主流程 ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="通过钉钉企业内部应用发送文件")
    parser.add_argument("--file",        required=True, help="要发送的文件路径")
    parser.add_argument("--target-type", required=True, choices=["user", "chat"], help="发送目标类型：user 或 chat")
    parser.add_argument("--target-id",   required=True, help="目标 userid（多个用逗号分隔）或 chatid")
    args = parser.parse_args()

    # 校验配置
    missing = [k for k, v in [("DINGTALK_CORPID", CORPID), ("DINGTALK_CORPSECRET", CORPSECRET), ("DINGTALK_AGENT_ID", AGENT_ID)] if not v]
    if missing:
        print(f"[错误] 缺少环境变量: {', '.join(missing)}")
        print("请在环境变量或 .claude/skills/dingtalk-send-file/.env 文件中配置")
        sys.exit(1)

    # 校验文件
    if not os.path.isfile(args.file):
        print(f"[错误] 文件不存在: {args.file}")
        sys.exit(1)

    file_name = os.path.basename(args.file)
    print(f"[1/3] 获取 access_token ...")
    token = get_access_token()

    print(f"[2/3] 上传文件: {file_name}")
    media_id = upload_media(token, args.file)
    print(f"      media_id: {media_id}")

    print(f"[3/3] 发送到 {args.target_type}: {args.target_id}")
    if args.target_type == "user":
        result = send_to_user(token, args.target_id, media_id, file_name)
    else:
        result = send_to_chat(token, args.target_id, media_id, file_name)

    print(f"\n[成功] 文件 '{file_name}' 已发送！")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
