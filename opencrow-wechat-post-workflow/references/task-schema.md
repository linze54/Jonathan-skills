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
  "approval_record": {
    "approved": false,
    "approved_by": "",
    "approved_at": "",
    "source_message": ""
  }
}
```

## Status Vocabulary

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

## Operator Messages

Received:

```text
已收到，已创建推文任务 {task_id}。当前状态：待生成 HTML。
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
