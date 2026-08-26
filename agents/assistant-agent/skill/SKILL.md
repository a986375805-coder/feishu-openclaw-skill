---
name: assistant-skill
description: 日常事务助理技能。定时提醒（把"每天9点提醒我XX""X分钟后提醒我"转成 openclaw cron）与全球 AI 新闻早报（抓取+中文摘要）。当用户说"提醒我""早报""新闻""设个提醒""闹钟""待办提醒"时使用。也可被 cron 定时任务调用执行每日早报。
license: MIT
metadata:
  author: atdy
  version: "1.0.0"
---

# 日常事务助理技能

本技能让"日常助理" bot 具备两个核心能力：**定时提醒**和**全球 AI 新闻早报**。

## 能力一：定时提醒

### 触发时机
用户在群里 @你 说出提醒意图：提醒我 / 提醒 / 到点叫我 / 设个闹钟 / 待办提醒 / 别忘了。

### 解析规则（把自然语言 → cron）

| 用户说法 | cron 表达式 / 参数 |
|---------|-------------------|
| "每天X点提醒我 XX" | `0 X * * *` |
| "每天早上X点 XX" | `0 X * * *` |
| "每周X（周几）X点 XX" | `0 X * * W`（W: 周一=1…周日=7） |
| "X分钟后提醒我 XX" | `--at Xm` |
| "X小时后提醒我 XX" | `--at Xh` |
| "明天X点提醒我 XX" | `--at <明天X点的ISO时间>` |
| "今天X点提醒我 XX" | `--at <今天X点的ISO时间>` |

### 执行命令
**必须带投递目标**（否则 cron 触发时没有群上下文、发不出去）：
```bash
openclaw cron add --name "<简短任务名>" --cron "<5字段表达式>" --channel feishu --to oc_ddcc7f9d59d22e9fd098defd406fefb6 --message "<提醒内容>" --agent assistant-agent
# 一次性任务示例（--at 不加 + 前缀）
openclaw cron add --name "喝水提醒" --at "30m" --channel feishu --to oc_ddcc7f9d59d22e9fd098defd406fefb6 --message "该喝水了 💧" --agent assistant-agent
```

### 成功标准
- 命令执行成功，返回 delivery 含 `channel: feishu` + `to: oc_ddcc7f9d59d22e9fd098defd406fefb6`
- 回复用户确认："已设置 ✓ 每天9:00 提醒你：晨会"

### 取消提醒
用户说"删掉/取消 X 提醒"时：
```bash
openclaw cron list   # 找到对应 job id
openclaw cron rm <job_id>
```
回复确认已删除。

## 能力二：全球 AI 新闻早报

### 触发时机
- **自动**：每天 9:00 由 cron 任务触发本 agent
- **手动**：用户 @"早报" / "新闻早报" / "今天的新闻"

### 执行步骤
1. 联网抓取全球 AI 新闻来源（以下任选组合）：
   - TechCrunch AI：`https://techcrunch.com/category/artificial-intelligence/feed/`
   - The Verge AI：`https://www.theverge.com/rss/ai-artificial-intelligence/index.xml`
   - MIT Technology Review AI：`https://www.technologyreview.com/topic/artificial-intelligence/feed/`
   - Hacker News (AI 相关)：`https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=10`
   - 也可用 web 搜索（搜索"AI news today"）
2. 筛选：选 5-10 条**重要的、非水文**的 AI 新闻（模型发布/融资/产品/政策/行业应用）
3. 每条生成：**标题 + 一句话中文摘要 + 来源链接**
4. 用飞书消息发送到群（格式见下）

### 输出格式（发到群）
```
📰 AI 早报 YYYY-MM-DD
━━━━━━━━━━━━━━
1. 【标题】一句话中文摘要
   🔗 来源链接
2. ...
━━━━━━━━━━━━━━
来源：TechCrunch / The Verge / MIT TR / HN 等
```

### 成功标准
- 抓到 ≥5 条有效新闻
- 每条有标题+中文摘要+真实链接
- 消息成功发到群

### 红线
- 不编造新闻、不编造链接、不编造引用内容。抓不到的来源就跳过。
- 摘要基于原文内容，不夸大、不歪曲。

## 边界
- 复杂产品/数据/前端任务 → 转给群内对应专业 bot。
- 用户要求设置的时间不明确时，反问确认（一句话）。
- 涉及删除已有提醒，先列出确认再删。