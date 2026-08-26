# assistant-agent - 日常事务助理（飞书 bot）

一个**日常事务管理机器人**：定时提醒 + 全球 AI 新闻早报。开箱即用模板，配合根目录 `SKILL.md`（飞书直连 API）使用。

## 功能

| 能力 | 说明 |
|------|------|
| 🗓️ **定时提醒** | 群里 @机器人 说"每天9点提醒我晨会""下午3点提醒我喝水""30分钟后提醒我休息"→ 自动注册成 openclaw cron，到点推送到群 |
| 📰 **全球 AI 新闻早报** | 每天 9:00 自动抓取全球 AI 新闻（TechCrunch/The Verge/MIT TR 等）→ 中文摘要 5-10 条 → 发到群；@说"早报"立即生成 |
| 🔎 **轻量查询** | 天气/时间等随口问直接答 |

## 目录结构

```
agents/assistant-agent/
├── README.md                  本文件
├── workspace/                 agent 工作区模板（复制到 ~/.openclaw/workspace-assistant）
│   ├── AGENTS.md / IDENTITY.md / USER.md / SOUL.md / TOOLS.md
│   ├── MEMORY.md / HEARTBEAT.md
│   └── memory/  projects/     记忆与项目上下文（占位）
└── skill/                     assistant-skill（SKILL.md + 脚本）
    └── scripts/
        ├── reminder.py        自然语言提醒 → cron 参数解析
        └── news_digest.py     全球 AI 新闻抓取 → 结构化 JSON
```

## 快速部署

1. **复制 workspace**：
   ```bash
   cp -r agents/assistant-agent/workspace/*  ~/.openclaw/workspace-assistant/
   ```
2. **复制 skill**：
   ```bash
   cp -r agents/assistant-agent/skill  ~/.openclaw/extensions/assistant-skill
   ```
3. **openclaw.json 注册**（参考 `_shared/openclaw-config.snippet.json`）：
   - `agents.list` 加 `assistant-agent`（model 建议 `deepseek/deepseek-v4-flash`）
   - `channels.feishu.accounts` 加：
     ```json
     "assistant": {
       "appId": "<你的飞书应用 AppID>",
       "appSecret": "<你的 AppSecret>",
       "name": "日常事务助理",
       "groupPolicy": "open",
       "enabled": true
     }
     ```
   - `bindings` 加：`{ "agentId": "assistant-agent", "match": { "channel": "feishu", "accountId": "assistant" } }`
   - `groups` 加你的群 chat_id
4. **建 cron 早报任务**：
   ```bash
   openclaw cron add --name daily-ai-news --cron "0 9 * * *" --agent assistant-agent --message "执行每日全球AI新闻早报"
   ```
5. **重启网关**生效。

## 飞书应用配置要求

- 权限：`im:message`、`im:message:send_as_bot`、`im:chat`（可选 `im:resource`）
- 事件订阅：方式选**长连接**，订阅 `im.message.receive_v1`
- **发布版本**后生效
- 把 bot 拉入目标群，群 chat_id 登记进 openclaw.json groups

## 提醒语法支持

| 说法 | 效果 |
|------|------|
| "每天9点提醒我晨会" | 每日 09:00 cron |
| "每天下午2点提醒我午休" | 每日 14:00 cron（时段自动换算） |
| "每周一9点半提醒我周报" | 每周一 09:30 cron |
| "30分钟后提醒我休息" | 一次性，30 分钟后 |
| "明天10点提醒我开会" | 一次性，明天 10:00 |

## 早报执行流程

1. cron 触发 / 用户 @ "早报"
2. agent 运行 `python skill/scripts/news_digest.py fetch --limit 12`
3. agent 用 LLM 对结果做中文摘要 + 去重 + 选 5-10 条
4. 格式化发到群

## License

遵循根仓库 LICENSE（MIT）。