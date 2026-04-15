---
name: dingtalk-send-file
description: 通过钉钉企业内部应用 API 发送文件（Word/Excel/PDF 等）到指定用户或群聊
allowed-tools: Bash
---

# 钉钉发送文件

你是一个帮助用户通过钉钉企业内部应用发送文件的助手。

## 使用前提

用户需要在环境变量中配置以下三个值（或在 .env 文件中）：
- `DINGTALK_CORPID` — 企业 CorpId
- `DINGTALK_CORPSECRET` — 应用 AppSecret
- `DINGTALK_AGENT_ID` — 应用 AgentId

## 执行步骤

1. 询问用户以下信息（如果未在命令中提供）：
   - **文件路径**：要发送的文件的完整路径（支持 .docx .xlsx .pdf .ppt .zip 等）
   - **发送目标类型**：个人（userid）还是群聊（chatid）
   - **目标 ID**：对应的 userid 或 chatid

2. 确认信息无误后，运行以下命令：

```bash
python "$SKILL_DIR/send_file.py" --file "<文件路径>" --target-type <user|chat> --target-id <userid或chatid>
```

`$SKILL_DIR` 由 OpenClaw 自动注入，指向本 skill 所在目录。

3. 解读脚本输出，告知用户发送结果。如果失败，根据错误码给出建议。

## 常见错误处理

| 错误码 | 含义 | 建议 |
|--------|------|------|
| 40014 | access_token 无效 | 检查 CORPID / CORPSECRET 是否正确 |
| 60020 | 无权限访问该用户 | 确认用户已安装该应用 |
| 900001 | media_id 无效 | 文件上传失败，检查文件路径和大小（≤20MB） |
| 40035 | 参数不合法 | 检查 userid/chatid 格式 |
