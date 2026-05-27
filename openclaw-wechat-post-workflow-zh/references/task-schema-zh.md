# 推文任务字段与状态

用于 OpenClaw 编排微信公众号推文任务。

## 最小任务对象

```json
{
  "task_id": "OC-YYYYMMDD-001",
  "project_name": "",
  "requester": "",
  "wechat_preview_user": "",
  "source_materials": [],
  "current_status": "received",
  "current_version": "v1",
  "html_artifact": "",
  "wechat_draft_id_or_url": "",
  "revision_notes": [],
  "group_notification_record": {
    "target_group_id": "cidJ2H2iPXrxZ436MXaO2e20A==",
    "target_group_name": "测试",
    "message": "",
    "sent": false,
    "sent_at": "",
    "error": ""
  },
  "approval_record": {
    "approved": false,
    "approved_by": "",
    "approved_at": "",
    "source_message": ""
  }
}
```

## 状态表

- `awaiting_preflight_confirmation`：已收到并检查材料，但发起人尚未确认是否调整可能问题；此时可以尚未创建正式任务。
- `received`：已收到材料，任务已创建。
- `html_generating`：正在生成微信公众号兼容 HTML。
- `html_generated`：HTML 已生成，准备发送草稿。
- `draft_posting`：正在发送到微信公众号草稿箱。
- `draft_created`：公众号草稿已创建或已更新。
- `waiting_review`：预览已发送或已请求发送，等待负责人确认。
- `revision_requested`：负责人提出修改。
- `revision_in_progress`：正在修改。
- `approved_for_publish`：负责人已确认，可进入待推送状态。
- `published`：确认已发布。
- `failed_html_generation`：HTML 生成失败。
- `failed_draft_posting`：草稿创建或更新失败。
- `failed_preview`：预览发送失败。

## 状态流转

```text
awaiting_preflight_confirmation
-> received
-> group_notification_sent
```

然后：

```text
received
-> html_generating
-> html_generated
-> draft_posting
-> draft_created
-> waiting_review
```

从 `waiting_review` 分支：

```text
waiting_review -> approved_for_publish
waiting_review -> revision_requested
```

从 `revision_requested` 回到生产流程：

```text
revision_requested -> revision_in_progress
revision_in_progress -> html_generated
```

失败后可在问题解决后重试：

```text
failed_html_generation -> html_generating
failed_draft_posting -> draft_posting
failed_preview -> waiting_review
```

## 修改意见格式

```json
{
  "version": "v1",
  "from": "",
  "received_at": "",
  "type": "text|screenshot|image|voice|file",
  "raw_content": "",
  "normalized_request": "",
  "resolved": false
}
```

## 群通知

目标群：

```text
群 ID: cidJ2H2iPXrxZ436MXaO2e20A==
群名: 测试
```

消息模板：

```text
{requester_name} 创建了推文《{article_title_or_project_name}》，推文编号：{task_id}。
```

记录格式：

```json
{
  "target_group_id": "cidJ2H2iPXrxZ436MXaO2e20A==",
  "target_group_name": "测试",
  "message": "",
  "sent": false,
  "sent_at": "",
  "error": ""
}
```

## 常用反馈话术

发现可能问题：

```text
已收到。我先检查了简报，发现以下可能需要确认的地方：
1. ...
2. ...
请问是否需要我先按这些建议调整？确认后我再创建推文任务并继续生成公众号排版。
```

未发现明显问题：

```text
已收到。我未发现明显错别字或不合理表述。请确认是否按当前材料创建推文任务并继续生成公众号排版。
```

收到材料：

```text
已收到，已创建推文任务 {task_id}。当前状态：待生成 HTML。
```

群通知：

```text
{requester_name} 创建了推文《{article_title_or_project_name}》，推文编号：{task_id}。
```

HTML 已生成：

```text
{task_id} 的公众号排版 HTML 已生成，正在发送到公众号草稿箱。
```

草稿已创建：

```text
{task_id} 的公众号草稿已创建，正在发送预览给 {wechat_preview_user}。
```

修改意见：

```text
已收到 {task_id} 的修改意见，我整理为：
1. ...
2. ...
我会生成新版本并重新发送预览。
```

确认通过：

```text
{task_id} 已由 {approved_by} 确认，可进入待推送状态。建议由新媒体负责人进行最终推送。
```
