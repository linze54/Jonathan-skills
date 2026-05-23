---
name: openclaw-wechat-post-workflow-zh
description: 当用户提交项目简报、DOCX 简报、推文草稿、截图修改意见，或要求生成、预览、修改、确认、发布微信公众号推文时，使用本 skill 协调 OpenClaw 的公众号推文工作流。本 skill 负责串联 xuan-docx-to-wechat-html 生成公众号 HTML，以及 baoyu-post-to-wechat 将 HTML 发送到微信公众号草稿箱，并管理任务状态、版本、预览确认和修改循环。
---

# OpenClaw 微信公众号推文工作流

本 skill 是公众号推文生产的流程控制器。它不替代已有的专业 skill，而是负责决定何时调用它们、如何记录状态、如何处理预览确认和修改。

- 使用 `xuan-docx-to-wechat-html` 将简报、DOCX、正文材料转换为微信公众号兼容 HTML。
- 使用 `baoyu-post-to-wechat` 将 HTML、Markdown 或纯文本发送到微信公众号后台草稿箱。

## 核心原则

始终把每篇推文当成一个“任务单”，不要当成一次普通聊天。

每个任务至少记录：

- `task_id`：任务编号
- `project_name`：项目名称
- `requester`：发起人或业务负责人
- `wechat_preview_user`：预览接收人
- `source_materials`：原始材料
- `current_status`：当前状态
- `current_version`：当前版本
- `html_artifact`：HTML 文件或内容引用
- `wechat_draft_id_or_url`：公众号草稿 ID 或链接
- `revision_notes`：修改意见
- `approval_record`：确认记录

需要精确字段或状态流转时，读取 `references/task-schema-zh.md`。

## 接收材料

当用户提交简报、DOCX、复制文本、图片，或说“帮我把这篇发成公众号推文”时：

1. 立即回复收到。
2. 创建任务编号。
3. 从上下文中提取项目名称、负责人、预览微信号、发布时间等信息。
4. 只追问会阻塞执行的缺失信息。
5. 将状态设为 `received`。

推荐回复：

```text
已收到，已创建推文任务 {task_id}。我会先生成公众号排版 HTML，然后发送到公众号草稿箱并发起预览确认。
```

## 执行顺序

按以下顺序执行：

1. 整理原始材料。
2. 调用 `xuan-docx-to-wechat-html`。
3. 检查返回的 HTML 是否基本可用。
4. 调用 `baoyu-post-to-wechat`。
5. 发送或请求发送微信预览。
6. 等待负责人确认或提出修改意见。

除非用户明确要求发布纯文本或 Markdown，否则不要在 HTML 生成前调用 `baoyu-post-to-wechat`。

## 生成 HTML

调用 `xuan-docx-to-wechat-html` 前，尽量提供这些信息：

- 项目或活动名称
- 目标读者
- 是否需要润色、改写，还是尽量保留原文
- 固定栏目、二维码、联系方式、机构落款
- 图片位置、图注和封面要求

生成成功后：

- 状态设为 `html_generated`
- 记录 HTML 文件路径或内容引用
- 告知用户正在发送到公众号草稿箱

生成失败时：

- 保留原始材料
- 用人能看懂的话说明失败原因
- 状态设为 `failed_html_generation`
- 给出一个明确恢复动作，例如重新上传 DOCX、改用纯文本、简化材料后重试

## 发送草稿

HTML 可用后，调用 `baoyu-post-to-wechat`。

传入信息包括：

- HTML 文件或 HTML 内容
- 标题
- 作者或机构名称
- 摘要
- 封面图
- 目标公众号账号

发送成功后：

- 记录草稿 ID、链接或返回标识
- 状态设为 `draft_created`
- 如果支持，继续发送预览

发送失败时：

- 状态设为 `failed_draft_posting`
- 判断并说明可能原因：登录失效、权限不足、HTML 不兼容、图片上传失败或未知错误
- 没有收到成功返回时，不要声称草稿已保存

## 预览确认

草稿创建后，将预览发送给负责人，或请求发送预览。

状态设为 `waiting_review`。

解释负责人回复：

- `确认`、`可以`、`发吧`、`没问题`、`通过`：进入 `approved_for_publish`
- 文字修改、截图圈画、图片替换、结构调整：进入 `revision_requested`
- 表达模糊时，先总结理解并请负责人确认，不要直接改状态

除非用户明确配置自动发布，否则不要自动最终推送。默认只把任务标记为“可推送”，由新媒体负责人最后点击发布。

## 修改循环

收到修改意见后：

1. 将每条意见绑定到当前任务。
2. 整理成修改清单。
3. 判断是直接修改 HTML，还是重新调用 `xuan-docx-to-wechat-html`。
4. 版本号递增，例如 `v1`、`v2`、`v3`。
5. 再调用 `baoyu-post-to-wechat` 更新或重建草稿。
6. 再次发送预览。

小范围文字修改优先直接改 HTML。结构重写、大幅删减、图片顺序调整、排版风格改变时，重新生成 HTML。

如果负责人发来截图批注，不能确定圈画位置时，不要假装已经识别。先把截图转成明确修改事项，必要时追问“截图中圈出的内容对应正文哪一段”。

## 多项目处理

同时存在多个项目时：

- 不要把不同项目的修改意见混在一起。
- 如果负责人只说“改一下第二段”，但没有明确任务，先判断最可能任务并请求确认。
- 每次进度更新都带上 `task_id`、项目名和当前状态。
- 可按状态输出待办清单，例如待排版、待预览、待修改、待确认、待推送。

## 进度反馈

在关键节点主动反馈：

- `received`
- `html_generating`
- `html_generated`
- `draft_posting`
- `draft_created`
- `waiting_review`
- `revision_requested`
- `approved_for_publish`
- `failed_*`

长时间任务不要沉默，应发送“仍在处理”的进度消息。

## 搜索工具说明

本工作流不依赖网页搜索。如果推文需要事实核查，而 `web_search` 返回 `fetch failed`，优先用 `web_fetch` 直接打开可靠来源页面，或让操作者补充来源材料。除非当前事实核查是必要环节，否则不要因为 `web_search` 故障阻塞推文生产。
