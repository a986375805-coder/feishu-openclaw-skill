# 飞书机器人 opencode Skill

把 openclaw 的飞书机器人能力提炼成独立的 opencode skill：直连飞书开放平台 API，
收发 IM 消息、读写多维表格（Bitable）、管理日历日程、任务、云文档。
零第三方依赖，纯 Python 标准库。

## 特性

- 发送文本 / 富文本消息到飞书群
- 读取群聊最近消息、跨会话搜索、下载消息中的图片/文件
- 多维表格记录：列出 / 过滤查询 / 新建 / 更新 / 删除
- 日历：创建日程、按时间范围查看日程
- 任务：创建 / 查看（待办与已完成）/ 更新（改标题、标记完成、改截止时间）
- 云文档：创建 / 读取正文 / 追加段落
- 凭据从环境变量或凭据文件读取，无硬编码密钥
- 跨平台（Windows / macOS / Linux，Python 3.8+）

## 安装

1. 把 `SKILL.md`、`scripts/`、`credentials.example.json` 放入你的 opencode skills 目录
   （默认 `~/.config/opencode/skills/feishu-openclaw/`），或按 cocoloop 方式安装。
2. 设置凭据：
   ```bash
   export FEISHU_APP_ID="cli_xxxx"
   export FEISHU_APP_SECRET="xxxx"
   ```
3. 验证：
   ```bash
   python scripts/feishu_cli.py token
   ```

## 飞书应用配置

1. 在 https://open.feishu.cn/app 创建「企业自建应用」
2. 添加机器人能力
3. 在「权限管理」开通所需权限：
   - 发消息：`im:message`、`im:message:send_as_bot`
   - 读消息：`im:message`、`im:chat`
   - 多维表格：`bitable:app`、`bitable:app:readonly`（如需要写则开通写权限）
   - 日历：`calendar:calendar`、`calendar:calendar.event`（含 create 权限）
   - 任务：`task:task:write`、`task:task:read`
   - 云文档：`docx:document`、`docx:document:create`
4. 创建版本并发布，等待审核通过

## 快速使用

```bash
# 发文本消息到群
echo "大家好" | python scripts/feishu_cli.py send-text oc_xxxxxxxx

# 发富文本（标题 + 多行正文）
echo "标题行" | python scripts/feishu_cli.py send-post oc_xxxxxxxx "周报标题"

# 读群消息
python scripts/feishu_cli.py read-messages oc_xxxxxxxx

# 多维表格：列出记录
python scripts/feishu_cli.py bitable-list bascXXXX tblXXXX

# 多维表格：新建记录
python scripts/feishu_cli.py bitable-create bascXXXX tblXXXX '{"标题":"新记录"}'

# 多维表格：按条件查询
python scripts/feishu_cli.py bitable-search bascXXXX tblXXXX '{"conjunction":"and","conditions":[{"field_name":"状态","operator":"is","value":["待办"]}]}'

# 日历：查看主日历日程（可带时间范围）
python scripts/feishu_cli.py calendar-list
python scripts/feishu_cli.py calendar-list "2026-08-17T00:00:00+08:00,2026-08-24T00:00:00+08:00"

# 日历：创建日程
python scripts/feishu_cli.py calendar-create "周会" "2026-08-18T10:00:00+08:00" "2026-08-18T11:00:00+08:00"

# 任务：创建
python scripts/feishu_cli.py task-create "写周报" "2026-08-20T18:00:00+08:00"

# 任务：查看待办 / 标记完成
python scripts/feishu_cli.py task-list
python scripts/feishu_cli.py task-update 任务GUID '{"completed":true}'

# 云文档：创建 / 读取 / 追加
python scripts/feishu_cli.py doc-create "会议纪要"
python scripts/feishu_cli.py doc-get doxcnXXXX
echo "第一段" | python scripts/feishu_cli.py doc-append doxcnXXXX
```

> 日历 / 任务 / 云文档未开通对应 scope 时，脚本会返回 `code=99991672 Access denied`，
> 按提示到飞书开放平台补开权限即可（见上文「飞书应用配置」）。

## 安全说明

- `app_secret` 是敏感凭据，只会出现在环境变量/凭据文件中，绝不会出现在本仓库
- 发消息为敏感操作，AI 调用前应先确认发送对象与内容
- 建议为 skill 单独创建飞书应用并最小化授权，不要复用生产环境的高权限应用

## 项目结构

```
SKILL.md                  skill 定义
scripts/feishu_cli.py     API CLI
credentials.example.json  凭据模板
references/               参考文档
skills/openclaw-original/ openclaw 原版 skill 参考（依赖其 MCP 网关，仅供对照）
agents/                   OpenClaw 多 agent 团队模板（产品/数据/前端三个飞书机器人）
  ├── _shared/             统一治理准则 + openclaw.json 配置片段
  ├── product-agent/       产品分析师（终审拍板者）
  ├── data-agent/          数据分析师
  └── frontend-agent/      前端工程师（含 taste/web-clone 等审美与复刻方法论）
```

## 多机器人团队（agents/）

如果你在跑 OpenClaw 多 agent（产品分析 / 数据分析 / 前端实现三个 bot 在飞书群协作），
直接使用 `agents/` 下的模板：每个 `workspace/` 复制到 `~/.openclaw/workspace-<agent>` 即可开箱即用，
内含统一治理（决策分级 L1-L4 + 产品分析师终审拍板）、长期记忆与自我进化机制、防超时任务协议。

详见 [`agents/README.md`](agents/README.md)。

## License

MIT
