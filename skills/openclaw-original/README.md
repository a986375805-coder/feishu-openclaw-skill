# openclaw 原版 skill（参考）

本目录收录 openclaw 飞书机器人插件的 9 个原始 skill，供对照参考：

| Skill | 能力 |
|-------|------|
| feishu-bitable | 多维表格增删改查、字段类型与公式 |
| feishu-calendar | 日历日程创建 / 查询 / 修改 / 忙闲查询 |
| feishu-channel-rules | 频道规则与 Markdown 语法 |
| feishu-create-doc | 从 Lark-flavored Markdown 创建云文档 |
| feishu-fetch-doc | 读取云文档内容 |
| feishu-im-read | 消息读取 / 话题 / 搜索 / 资源下载 |
| feishu-task | 任务创建 / 列表 / 完成 / 清单 |
| feishu-troubleshoot | 常见问题排查（feishu_doctor） |
| feishu-update-doc | 更新云文档（覆盖 / 追加） |

**重要**：这些 skill 调用的是 openclaw 网关自带的 MCP 工具
（`feishu_mcp_*`、`feishu_calendar_*`、`feishu_task_*`、`feishu_im_*` 等），
它们**不是**标准飞书开放平台 API，不能脱离 openclaw 独立使用。

需要在任意环境直连飞书 API 使用时，请使用仓库根目录的
`scripts/feishu_cli.py`（纯标准库，填 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 即用）。

两者能力对应关系：
- 原版 MCP 工具功能更全（如 Markdown→文档、忙闲查询、话题回复），需要 openclaw 网关
- 直连版覆盖常用操作（消息收发 / Bitable / 日历 / 任务 / 云文档基础），任何环境可跑
