# OpenClaw 多 Agent 团队模板（飞书专用）

一套"开箱即用"的飞书多机器人团队：产品分析、数据分析、前端实现、日常事务助理四个 bot，
带统一治理（拍板权）、长期记忆与自我进化机制。配合本仓库根目录的 `SKILL.md`（飞书直连 API skill）使用。

> 适用范围：OpenClaw（原 Clawdbot）在飞书群里的多 agent 协作场景。
> 特性：多 bot 分工 + 产品分析师终审拍板（GOVERNANCE.md）+ 每人长期记忆（MEMORY/USER/EVOLUTION）+ 项目上下文 + 助理定时提醒/新闻早报。

## 团队构成

| 角色 | 目录 | 职责 | 建议模型 |
|------|------|------|---------|
| 📊 产品分析师（终审） | `product-agent/` | 产品规划/需求/优先级/增长/商业化/拍板。多 agent 分歧时收敛裁决 | 推理强的中档模型（如 deepseek-v4-flash / qwen3.5-flash） |
| 📈 数据分析师 | `data-agent/` | 数据获取/清洗/分析/可视化/生图（matplotlib + 通义万相） | 可带视觉能力（如 qwen3.5-flash） |
| 🎨 前端工程师 | `frontend-agent/` | 页面/组件/视觉实现；网站复刻（taste-skill + web-clone） | 逻辑强的模型（如 deepseek-v4-flash） |
| 🗓️ 日常事务助理 | `assistant-agent/` | 定时提醒（自然语言→cron）+ 全球 AI 新闻早报（每日 9 点自动）+ 轻量查询 | 通用中档模型（如 deepseek-v4-flash） |

## 目录结构

```
agents/
├── README.md                     本文件（部署指南）
├── _shared/
│   ├── GOVERNANCE.md             全队统一治理准则（L1-L4 决策分级 + 拍板权 + 分歧裁决）
│   └── openclaw-config.snippet.json  openclaw.json 片段模板（agent 注册/模型/飞书绑定/权限）
├── product-agent/
│   └── workspace/                产品分析师工作区模板
│       ├── AGENTS.md / IDENTITY.md / USER.md / SOUL.md / TOOLS.md
│       ├── MEMORY.md / EVOLUTION.md / GOVERNANCE.md / HEARTBEAT.md
│       ├── skills/product-decision/   产品决策方法论（reasoning-engine / playbooks / response-examples）
│       └── memory/  projects/         记忆与项目上下文（占位）
├── data-agent/
│   └── workspace/                数据分析师工作区模板
│       ├── AGENTS.md / IDENTITY.md / USER.md / SOUL.md / TOOLS.md
│       ├── MEMORY.md / EVOLUTION.md / GOVERNANCE.md / HEARTBEAT.md
│       ├── skills/datafenxi/         数据分析方法论
│       └── scripts/              数据脚本（generate_image.py 等）
└── frontend-agent/
    └── workspace/                前端工程师工作区模板
        ├── AGENTS.md / IDENTITY.md / USER.md / SOUL.md / TOOLS.md
        ├── MEMORY.md / EVOLUTION.md / GOVERNANCE.md / HEARTBEAT.md
        └── skills/               taste-skill / soft-skill / minimalist-skill / brutalist-skill / web-clone
└── assistant-agent/
    ├── workspace/                日常事务助理工作区模板
    │   └── AGENTS.md / IDENTITY.md / USER.md / SOUL.md / TOOLS.md / MEMORY.md
    └── skill/                    助理技能（SKILL.md + reminder.py + news_digest.py）
```

## 快速部署（3 步）

### 1. 建工作区

把每个 `workspace/` 目录复制到 `~/.openclaw/workspace-<agent>`：

```bash
# Linux/macOS
mkdir -p ~/.openclaw/{workspace-product,workspace-data,workspace-frontend}
cp -r agents/product-agent/workspace/*        ~/.openclaw/workspace-product/
cp -r agents/data-agent/workspace/*           ~/.openclaw/workspace-data/
cp -r agents/frontend-agent/workspace/*       ~/.openclaw/workspace-frontend/

# Windows PowerShell
New-Item -ItemType Directory -Path $env:USERPROFILE\.openclaw\{workspace-product,workspace-data,workspace-frontend} -Force
Copy-Item agents\product-agent\workspace\*    $env:USERPROFILE\.openclaw\workspace-product\ -Recurse -Force
Copy-Item agents\data-agent\workspace\*       $env:USERPROFILE\.openclaw\workspace-data\ -Recurse -Force
Copy-Item agents\frontend-agent\workspace\*   $env:USERPROFILE\.openclaw\workspace-frontend\ -Recurse -Force
```

### 2. 注册 agent 与绑定飞书

编辑 `~/.openclaw/openclaw.json`，参考 `_shared/openclaw-config.snippet.json` 合并：

- `agents.list`：注册 3 个 agent（指定 workspace / agentDir / model）
- `bindings`：把每个 agent 绑定到一个飞书 `accountId`（一个 bot = 一个飞书应用）
- `channels.feishu`：配置飞书应用凭据与群 allowlist
- 在 `~/.openclaw/agents/<agent>/agent/models.json` 配置各 provider 的 API key（dashscope/deepseek/qwen 等；不入库）

### 3. 部署后必做

1. **填 `USER.md`**：把 `身份/业务` 占位改成你的实际情况（最好再补业务红线）。这是记忆的根。
2. **确认治理生效**：三份 `GOVERNANCE.md` 内容一致；产品分析师是终审管理者，data/frontend 服从。
3. **飞书群 @ mention**：各 AGENTS.md 群聊规则里的 `<at user_id="...">` 需替换成实际 bot 的 user_id（在群成员里查）。
4. 首次会话可让 agent 跑一遍自我校对：读 USER/MEMORY/GOVERNANCE 后回你一句话确认理解无误。

## 治理与协作（重点）

- **决策分级**：L1 直接做 / L2 给推荐再执行 / L3 升级用户 / L4 红线即停。
- **拍板**：分歧由产品分析师收敛（2 轮接力上限），具体见 `_shared/GOVERNANCE.md`。
- **记忆**：每人会话结束自动写 `memory/YYYY-MM-DD.md` + 蒸馏进 `MEMORY.md`（见 EVOLUTION.md）。
- **防超时**：任务启动先读 projects 上下文，禁止大海捞针（已在各 AGENTS.md 固化）。

## 模型建议与成本

- 三个 agent 可用同一 provider 的不同档位：产品/前端用推理档，数据可用视觉档。
- 若平台不支持某模型 id，改 `agents.list[].model` 为你的可用模型即可，无需动 workspace。
- 具体 provider 配置见 `_shared/openclaw-config.snippet.json` 注释。

## License

遵循根仓库 LICENSE（MIT）。转发/修改时请保留来源说明。