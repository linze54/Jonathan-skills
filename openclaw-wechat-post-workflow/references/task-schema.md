# Task Schema And Statuses

Use this reference when orchestrating WeChat Official Account article tasks.

## Minimal Task Object

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

## Status Vocabulary

- `awaiting_preflight_confirmation`: Source material was received and reviewed, but the requester has not yet confirmed whether to adjust possible issues. A formal task may not exist yet.
- `received`: Source materials were received and a task exists.
- `html_generating`: The article is being converted into WeChat-compatible HTML.
- `html_generated`: HTML exists and is ready to post.
- `draft_posting`: HTML is being sent to the WeChat Official Account draft box.
- `draft_created`: A WeChat draft was created or updated.
- `waiting_review`: A preview was sent or requested, and reviewer confirmation is pending.
- `revision_requested`: The reviewer requested changes.
- `revision_in_progress`: Changes are being applied.
- `approved_for_publish`: The reviewer approved the preview.
- `published`: The article was confirmed as published.
- `failed_html_generation`: HTML generation failed.
- `failed_draft_posting`: Draft creation or update failed.
- `failed_preview`: Preview delivery failed.

## Transition Rules

```text
awaiting_preflight_confirmation
-> received
-> group_notification_sent
```

Then:

```text
received
-> html_generating
-> html_generated
-> draft_posting
-> draft_created
-> waiting_review
```

From `waiting_review`:

```text
waiting_review -> approved_for_publish
waiting_review -> revision_requested
```

From `revision_requested`:

```text
revision_requested -> revision_in_progress
revision_in_progress -> html_generated
```

Failure states can be retried after the operator resolves the cause:

```text
failed_html_generation -> html_generating
failed_draft_posting -> draft_posting
failed_preview -> waiting_review
```

## Revision Note Format

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

## Group Notification

Target group:

```text
群 ID: cidJ2H2iPXrxZ436MXaO2e20A==
群名: 测试
```

Message template:

```text
{requester_name} 创建了推文《{article_title_or_project_name}》，推文编号：{task_id}。
```

Record format:

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

## Operator Messages

Preflight issues found:

```text
已收到。我先检查了简报，发现以下可能需要确认的地方：
1. ...
2. ...
请问是否需要我先按这些建议调整？确认后我再创建推文任务并继续生成公众号排版。
```

No obvious issues:

```text
已收到。我未发现明显错别字或不合理表述。请确认是否按当前材料创建推文任务并继续生成公众号排版。
```

Received:

```text
已收到，已创建推文任务 {task_id}。当前状态：待生成 HTML。
```

Group notification:

```text
{requester_name} 创建了推文《{article_title_or_project_name}》，推文编号：{task_id}。
```

HTML generated:

```text
{task_id} 的公众号排版 HTML 已生成，正在发送到公众号草稿箱。
```

Draft created:

```text
{task_id} 的公众号草稿已创建，正在发送预览给 {wechat_preview_user}。
```

Revision summary:

```text
已收到 {task_id} 的修改意见，我整理为：
1. ...
2. ...
我会生成新版本并重新发送预览。
```

Approved:

```text
{task_id} 已由 {approved_by} 确认，可进入待推送状态。建议由新媒体负责人进行最终推送。
```
