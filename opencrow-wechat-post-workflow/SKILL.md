---
name: opencrow-wechat-post-workflow
description: Coordinate OpenCrow/OpenClaw WeChat Official Account article production when a user submits a project brief, DOCX briefing, article draft, screenshots with revision notes, or asks to create, preview, revise, approve, or post a WeChat public-account article. Use this skill to orchestrate the existing xuan-docx-to-wechat-html skill for HTML generation and baoyu-post-to-wechat skill for sending HTML to the WeChat Official Account draft box, while tracking task status, versions, preview confirmation, and revision loops.
---

# OpenCrow WeChat Post Workflow

Use this skill as the workflow controller for WeChat Official Account article production. Do not replace the specialist skills:

- Use `xuan-docx-to-wechat-html` to convert a brief, DOCX, or article material into WeChat-compatible HTML.
- Use `baoyu-post-to-wechat` to send HTML, Markdown, or plain text to the WeChat Official Account draft box.

## Core Rule

Always treat each article as a tracked task, not a one-off chat. Create or identify the task before calling either production skill.

Required task fields:

- `task_id`
- `project_name`
- `requester`
- `wechat_preview_user`
- `source_materials`
- `current_status`
- `current_version`
- `html_artifact`
- `wechat_draft_id_or_url`
- `revision_notes`
- `approval_record`

Use the status vocabulary and schema in `references/task-schema.md` when exact fields or status transitions are needed.

## Intake

When the user submits a brief, DOCX, copied text, images, or a request like "help me publish this as a WeChat article":

1. Acknowledge immediately.
2. Create a task id.
3. Extract missing operational fields from context when possible.
4. Ask only for fields that block execution, such as missing source material, target account, preview recipient, or publication deadline.
5. Set status to `received`.

Suggested acknowledgement:

```text
已收到，已创建推文任务 {task_id}。我会先生成公众号排版 HTML，然后发送到公众号草稿箱并发起预览确认。
```

## Production Sequence

Execute the skills in this order:

1. Prepare source material.
2. Call `xuan-docx-to-wechat-html`.
3. Validate the returned HTML at a practical level.
4. Call `baoyu-post-to-wechat`.
5. Send or request a WeChat preview.
6. Wait for approval or revision notes.

Do not call `baoyu-post-to-wechat` before HTML exists unless the user explicitly asks to post plain text or Markdown.

## HTML Generation

Before using `xuan-docx-to-wechat-html`, pass enough intent for the target article style:

- Project or activity name.
- Intended audience.
- Whether the brief should be rewritten, polished, or preserved closely.
- Required sections, fixed footer, QR code, contact info, or organizational signature.
- Image placement and caption expectations.

After generation, set status to `html_generated` and save or record the HTML artifact path/content reference.

If HTML generation fails:

- Preserve the original materials.
- Report a short human-readable failure reason.
- Set status to `failed_html_generation`.
- Offer one concrete recovery action, such as retrying with simplified source text or asking for the DOCX again.

## Draft Posting

Use `baoyu-post-to-wechat` after the HTML is available.

Provide:

- HTML artifact or HTML content.
- Title.
- Author or organization name when known.
- Digest/summary when known.
- Cover image when provided.
- Target WeChat Official Account if multiple accounts exist.

After successful posting:

- Record the draft id, URL, or any returned identifier.
- Set status to `draft_created`.
- Trigger preview delivery when supported.

If draft posting fails:

- Set status to `failed_draft_posting`.
- Report whether the likely cause is login/session, account permission, HTML validation, image upload, or unknown.
- Do not claim the draft was saved unless the posting skill returned a success result.

## Preview And Approval

After draft creation, send the preview to the responsible reviewer or ask the posting skill/system to send it.

Set status to `waiting_review`.

Interpret reviewer replies:

- Approval phrases such as `确认`, `可以`, `发吧`, `没问题`, `通过` mean the task can move to `approved_for_publish`.
- Revision phrases, screenshots, marked images, or text changes move the task to `revision_requested`.
- Ambiguous replies should be summarized back and confirmed before changing status.

Do not final-publish automatically unless the user explicitly configured that behavior. Prefer notifying the new-media operator that the task is approved and ready to publish.

## Revision Loop

When revision notes arrive:

1. Attach every note to the current task.
2. Summarize the requested changes as a checklist.
3. Decide whether to edit the current HTML directly or regenerate HTML with `xuan-docx-to-wechat-html`.
4. Increment version: `v1`, `v2`, `v3`.
5. Repost or update the WeChat draft with `baoyu-post-to-wechat`.
6. Send a new preview.

Use direct HTML edits for small text changes. Regenerate HTML for structural rewrites, extensive shortening, image reordering, or style changes.

When screenshots are provided, do not pretend exact marked regions were understood unless image interpretation is available. Convert screenshots into explicit revision notes and ask for clarification if the marked area cannot be mapped to article text.

## Multi-Project Handling

When multiple projects or reviewers are active:

- Never mix revision notes across tasks.
- If a reviewer sends "改一下第二段" without a clear active task, identify the likely task and ask for confirmation.
- Include `task_id`, project name, and current status in every progress update.
- Provide daily or on-demand summaries grouped by status.

## Progress Updates

Send short progress updates at meaningful milestones:

- `received`
- `html_generating`
- `html_generated`
- `draft_posting`
- `draft_created`
- `waiting_review`
- `revision_requested`
- `approved_for_publish`
- `failed_*`

For long operations, send a "still processing" message rather than staying silent.

## Search Tool Note

This workflow does not require web search. If article production requires fact checking and `web_search` is failing, use `web_fetch` directly with reliable search/result pages or ask the operator to provide the source material. Do not block the article workflow on `web_search` unless current web verification is essential.
