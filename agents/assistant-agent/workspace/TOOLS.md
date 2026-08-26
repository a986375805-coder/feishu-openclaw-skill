# TOOLS.md - 本机环境速查（部署后按实际情况填写）

## Shell
- Windows PowerShell 5.1；禁止 bash 语法（`&&`/`ls`/`$()`）。
- 可用：python、node、npm、git。

## openclaw 命令（核心）
- 注册提醒：`openclaw cron add --name <任务名> --cron "分 时 * * *" --channel feishu --to oc_ddcc7f9d59d22e9fd098defd406fefb6 --message "<提醒内容>" --agent assistant-agent`
  - 示例：每天9点 → `--cron "0 9 * * *"`
  - 每周一9点 → `--cron "0 9 * * 1"`
  - 一次性(X分钟后) → `--at Xm`
- 查看提醒：`openclaw cron list`
- 立即运行（调试）：`openclaw cron run <job_id>`
- 删除提醒：`openclaw cron rm <job_id>`
- 网关状态：`openclaw gateway status`

## 新闻早报
- 技能：`skill/`（scripts/news_digest.py 负责抓取）
- 抓取脚本：`python skill/scripts/news_digest.py fetch --limit 12`
- 数据源：TechCrunch AI / The Verge AI / MIT Tech Review / HackerNews（联网抓取）
- 中文摘要：由 agent（LLM）对抓取结果生成

## 网关
- 日志：`C:\tmp\clawdbot\clawdbot-YYYY-MM-DD.log`
- 端口：18789