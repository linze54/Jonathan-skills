---
name: dingtalk-get-attendance
description: 批量获取钉钉企业内部人员考勤打卡记录，输出为 CSV/Excel 供后续处理
allowed-tools: Bash
---

# 钉钉批量获取考勤记录

你是一个帮助用户批量拉取钉钉考勤数据的助手。

## 使用前提

与 dingtalk-send-file 共用同一份凭证，读取同目录下的 `.env` 文件或环境变量：
- `DINGTALK_CORPID`
- `DINGTALK_CORPSECRET`

（考勤接口不需要 AGENT_ID）

## 执行步骤

1. 询问用户以下信息（如果未在命令中提供）：
   - **开始日期**：格式 YYYY-MM-DD，例如 2025-04-01
   - **结束日期**：格式 YYYY-MM-DD，例如 2025-04-30（单次最多 31 天）
   - **人员范围**：全员（留空）或指定 userid 列表（逗号分隔）
   - **输出文件路径**（可选，默认输出到当前目录 `attendance_YYYYMMDD.csv`）

2. 确认信息后，运行脚本：

```bash
python "$SKILL_DIR/get_attendance.py" --date-from <开始日期> --date-to <结束日期> --userids <userid1,userid2,...> --output <输出文件路径.csv>
```

`--userids` 和 `--output` 为可选参数，不需要时直接省略。`$SKILL_DIR` 由 OpenClaw 自动注入，指向本 skill 所在目录。

3. 脚本会分批拉取（每批最多 50 人 × 31 天），完成后输出 CSV 文件路径和记录总数。

4. 告知用户结果，并提示可用 `/dingtalk-send-file` 将 CSV 发送到钉钉。

## 输出字段说明

| 字段 | 含义 |
|------|------|
| userId | 员工 ID |
| userName | 员工姓名 |
| workDate | 考勤日期 |
| checkTime | 打卡时间 |
| checkType | 打卡类型（OnDuty=上班 / OffDuty=下班） |
| locationResult | 位置结果（Normal/Outside/NotSigned） |
| approveId | 关联审批单 ID（如有） |
| sourceType | 打卡来源（ATM/BEACON/DING_ATM 等） |

## 常见错误处理

| 错误码 | 含义 | 建议 |
|--------|------|------|
| 40014 | access_token 无效 | 检查 CORPID / CORPSECRET |
| 49002 | 应用无考勤权限 | 在钉钉开放平台为应用开通「考勤」权限 |
| 10004 | 参数错误 | 检查日期格式是否为 YYYY-MM-DD |
