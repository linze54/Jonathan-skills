---
name: openclaw-wechat-post-workflow
description: Coordinate OpenClaw WeChat Official Account article production when a user submits a project brief, DOCX briefing, article draft, screenshots with revision notes, or asks to create, preview, revise, approve, or post a WeChat public-account article. Use this skill to first check the brief for likely typos, wording issues, contradictions, missing context, or unreasonable content, ask whether to adjust, then create a tracked task, notify the configured DingTalk group, and orchestrate xuan-docx-to-wechat-html for HTML generation and baoyu-post-to-wechat for sending HTML to the WeChat Official Account draft box.
---

# OpenClaw WeChat Post Workflow

Use this skill as the workflow controller for WeChat Official Account article production. Do not replace the specialist skills:

- Use `xuan-docx-to-wechat-html` to convert a brief, DOCX, or article material into WeChat-compatible HTML.
- Use `baoyu-post-to-wechat` to send HTML, Markdown, or plain text to the WeChat Official Account draft box.

## Core Rule

Always treat each article as a tracked task, not a one-off chat. Before creating a new formal task from newly submitted source material, run a preflight brief review and ask whether to adjust possible issues. Create the task only after the requester confirms the material should proceed, with or without adjustments.

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
- `group_notification_record`

Use the status vocabulary and schema in `references/task-schema.md` when exact fields or status transitions are needed.

## Intake

When the user submits a brief, DOCX, copied text, images, or a request like "help me publish this as a WeChat article":

1. Acknowledge immediately.
2. Review the submitted content for likely typos, awkward wording, contradictions, missing facts, unclear names, date/time issues, and unreasonable claims.
3. Reply with a concise list of possible issues and ask whether to adjust them before production.
4. Do not create the formal `task_id` yet unless the user explicitly asks to skip review or the content is already approved.
5. After the user confirms how to handle the issues, create the task id, extract missing operational fields, and proceed.

Suggested acknowledgement:

```text
已收到。我先检查了简报，发现以下可能需要确认的地方：
1. ...
2. ...
请问是否需要我先按这些建议调整？确认后我再创建推文任务并继续生成公众号排版。
```

If no obvious issues are found, still ask for confirmation before task creation:

```text
已收到。我未发现明显错别字或不合理表述。请确认是否按当前材料创建推文任务并继续生成公众号排版。
```

## Preflight Brief Review

Run this review before creating a new task:

- Typos, homophones, missing words, duplicate words, and punctuation errors.
- Awkward wording, overly informal phrasing, or expressions unsuitable for a public account article.
- Inconsistent project names, organization names, people names, dates, times, locations, or numbers.
- Missing key event facts, such as time, place, organizer, target audience, activity result, or call to action.
- Claims that sound exaggerated, unsupported, sensitive, or inappropriate for the organization.
- Text that should likely be shortened, split, or converted into clearer article sections.

Classify review output as:

- `must_confirm`: likely factual or sensitive issue that needs the requester to confirm.
- `suggested_edit`: wording, style, or readability improvement that can be applied with permission.
- `no_issue`: no obvious problem found.

Do not silently rewrite source material before confirmation. If the requester agrees to adjust, summarize the intended corrections first when the changes affect facts, names, dates, or numbers.

After confirmation:

- If the requester approves adjustments, use the corrected material as `source_materials`.
- If the requester rejects adjustments, preserve the original material.
- Then create `task_id`, set status to `received`, send the configured group notification, and continue the production sequence.

## Group Notification

After a formal task is created, send exactly one notification message to this group:

```text
群 ID: cidJ2H2iPXrxZ436MXaO2e20A==
群名: 测试
```

Message content:

```text
{requester_name} 创建了推文《{article_title_or_project_name}》，推文编号：{task_id}。
```

Rules:

- Use the one-on-one chat counterpart's display name as `requester_name`.
- Use the article title when known; otherwise use the project name or brief subject.
- Send the notification only after `task_id` exists.
- Do not send duplicate notifications for the same `task_id`.
- Record the result in `group_notification_record`, including target group id, target group name, message text, sent status, sent time, and any error.
- If the group message tool or channel is unavailable, do not block article production. Record the failure and tell the operator that group notification failed.

## Production Sequence

Execute the skills in this order:

1. Prepare source material.
2. Confirm preflight review handling and create the task id.
3. Send the configured group notification.
4. Call `xuan-docx-to-wechat-html`.
5. Validate the returned HTML at a practical level.
6. Call `baoyu-post-to-wechat`.
7. Send or request a WeChat preview.
8. Wait for approval or revision notes.

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
- `awaiting_preflight_confirmation`
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
