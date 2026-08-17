---
name: feishu-openclaw
description: |
  飞书机器人操作 skill：通过飞书开放平台 API 直接收发 IM 消息、读写多维表格(Bitable)、
  管理日历日程、任务、云文档。基于 openclaw 的飞书机器人能力提炼，脱离 openclaw 独立可用
  （零第三方依赖，纯标准库 Python）。

  **必须触发场景**：
  (1) 用户提到「飞书」「发到飞书」「飞书群里说一下」「飞书表格」「多维表格」
  (2) 需要向飞书群/人发消息、读取飞书群消息
  (3) 需要读写飞书多维表格（Bitable）数据
  (4) 需要在飞书日历建日程/查日程、管理飞书任务、创建/读取云文档
  (5) 用户说「用飞书机器人」或其别名

  **凭据要求**：运行前必须设置环境变量 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`，
  或提供凭据文件路径。密钥绝不硬编码。
  **权限要求**：日历/任务/云文档 API 需在飞书开放平台为应用额外开通对应权限（见本文档）。
---

# 飞书机器人（feishu-openclaw）

> 基于 openclaw 飞书机器人能力提炼的独立 skill。直连 `open.feishu.cn` API，
> 不依赖 openclaw 网关，任何有 Python 3.8+ 的机器都能用。

## 凭据（必读）

两种方式，任选其一：

1. **环境变量**（推荐）：
   ```powershell
   $env:FEISHU_APP_ID = "cli_xxxx"
   $env:FEISHU_APP_SECRET = "xxxx"
   ```
2. **凭据文件**：把 `credentials.example.json` 复制为 `credentials.json` 并填入，
   运行时通过 `FEISHU_CREDENTIALS_FILE` 指向它：
   ```powershell
   $env:FEISHU_CREDENTIALS_FILE = "D:\path\to\credentials.json"
   ```

> ⚠️ 安全提醒：`FEISHU_APP_SECRET` 属于敏感凭据，禁止写进代码、日志、聊天记录或 Git 历史。
> 机器人在飞书开放平台创建：https://open.feishu.cn/app
> 需要应用具备对应权限（发消息 / 多维表格读写 / 日历 / 任务 / 云文档），并在「权限管理」里开通 + 发布版本。

## 权限清单

| 能力 | 需开通的 scope | 备注 |
|------|---------------|------|
| 发/读消息 | `im:message`、`im:message:send_as_bot`、`im:chat` | 机器人能力 |
| 多维表格 | `bitable:app`、`bitable:app:readonly` | 写操作需写权限 |
| 日历日程 | `calendar:calendar`、`calendar:calendar.event` | create 还需 `calendar:calendar.event:create` |
| 任务 | `task:task:write`、`task:task:read` | 仅能访问自己是成员的任务 |
| 云文档 | `docx:document`、`docx:document:create` | 需额外开通才能调用 |

开通方式：飞书开放平台 → 应用 → 「权限管理」→ 搜索对应 scope → 开通 → 创建版本发布。
未开通时脚本会返回 `code=99991672 Access denied` 并附上缺失的 scope，可按提示补开。

## 常用 ID 获取

| 目标 | 怎么拿 |
|------|--------|
| 群 chat_id (`oc_xxx`) | 飞书群里「设置 → 群设置 → 群信息」，或通过机器人事件消息的 `chat_id` |
| 用户 open_id (`ou_xxx`) | 通过机器人事件消息的 `sender` 字段 |
| Bitable app_token | 表格地址 `.../base/bascXXXX` 中的 `bascXXXX`，或脚本里的 `FEISHU_APP_TOKEN` |
| Bitable table_id | 表格地址 `.../table/tblXXXX` 中的 `tblXXXX` |

## 脚本用法

脚本：`scripts/feishu_cli.py`，所有输出为 JSON。

```powershell
# 1. 测试凭据连通性（获取 tenant_access_token）
python scripts/feishu_cli.py token

# 2. 发文本消息到群（内容从 stdin 传入，避免命令行编码问题）
"大家好" | python scripts/feishu_cli.py send-text oc_xxxxxxxx

# 3. 发富文本消息（标题 + 多行正文）
"日报标题" | python scripts/feishu_cli.py send-post oc_xxxxxxxx 日报标题

# 4. 读取某群的最近消息
python scripts/feishu_cli.py read-messages oc_xxxxxxxx

# 5. 列出多维表格记录
python scripts/feishu_cli.py bitable-list bascXXXX tblXXXX

# 6. 按过滤条件查询记录
python scripts/feishu_cli.py bitable-search bascXXXX tblXXXX '{"conjunction":"and","conditions":[{"field_name":"状态","operator":"is","value":["待办"]}]}'

# 7. 新建记录（fields 为 JSON）
python scripts/feishu_cli.py bitable-create bascXXXX tblXXXX '{"标题":"新记录","状态":"待办"}'

# 8. 更新记录
python scripts/feishu_cli.py bitable-update bascXXXX tblXXXX recXXXXX '{"状态":"已完成"}'

# 9. 删除记录
python scripts/feishu_cli.py bitable-delete bascXXXX tblXXXX recXXXXX

# 10. 下载消息中的图片/文件
python scripts/feishu_cli.py fetch-resource om_XXXX img_v3_XXXX image out.png

# 11. 查看主日历日程（可选时间范围 START,END）
python scripts/feishu_cli.py calendar-list
python scripts/feishu_cli.py calendar-list "2026-08-17T00:00:00+08:00,2026-08-24T00:00:00+08:00"

# 12. 创建日历日程
python scripts/feishu_cli.py calendar-create "周会" "2026-08-18T10:00:00+08:00" "2026-08-18T11:00:00+08:00" "会议说明"

# 13. 创建任务
python scripts/feishu_cli.py task-create "写周报" "2026-08-20T18:00:00+08:00"

# 14. 查看待办/已完成任务
python scripts/feishu_cli.py task-list
python scripts/feishu_cli.py task-list done

# 15. 更新任务（改标题/标记完成/改截止时间）
python scripts/feishu_cli.py task-update 任务GUID '{"summary":"新标题"}'
python scripts/feishu_cli.py task-update 任务GUID '{"completed":true}'
python scripts/feishu_cli.py task-update 任务GUID '{"due":"2026-08-25T12:00:00+08:00"}'

# 16. 创建云文档
python scripts/feishu_cli.py doc-create "会议纪要"

# 17. 读取云文档正文
python scripts/feishu_cli.py doc-get doxcnXXXX

# 18. 向云文档追加段落（内容从 stdin）
"第一段" | python scripts/feishu_cli.py doc-append doxcnXXXX
```

> 跨会话**消息搜索**需要用户身份授权（user_access_token，OAuth），本 CLI 使用应用身份无法完成；
> 需要搜索时请参考 `skills/openclaw-original/feishu-im-read/`（原版 skill，基于 openclaw 网关）。
> 部分能力（日历/任务/云文档）需在飞书开放平台为应用开通对应 scope（见下方「权限清单」）。

## 执行流程

```
Step 1  确认凭据：FEISHU_APP_ID / FEISHU_APP_SECRET 已设置（没有则引导用户设置）
Step 2  确认目标：群 chat_id / open_id / app_token / table_id
Step 3  调用脚本执行操作
Step 4  解析 JSON 结果返回给用户
```

**约定**：
- 向飞书**发消息是敏感操作**，先和用户确认接收对象与内容，再执行
- 不确定 chat_id / app_token 时先问用户，不要猜测
- 脚本输出为 JSON，成功时 `ok=true`，失败时 `ok=false` + `error`

## 目录

```
SKILL.md                 本文件
scripts/feishu_cli.py    飞书 API CLI（纯标准库）
credentials.example.json 凭据模板（勿提交真实密钥）
references/api-reference.md  飞书 API 端点与字段格式参考
skills/openclaw-original/     openclaw 原版 9 个 skill 参考实现（依赖 openclaw MCP 网关，仅作参考）
```
