# TOOLS.md - 本机环境速查（部署后按实际情况填写）

本文件是**你的环境专属信息**，避免每次接任务都要探索文件系统。Skills 定义工具怎么用，这里定义你的环境特例。

## Shell / 执行环境
- shell: `exec` 工具的实际 shell（Windows 为 PowerShell 5.1，Linux/macOS 为 bash；启动时先探测确认，以实际为准）
- 可用运行时：Node.js / Python（版本以实际环境为准，填这里）

## 工作区与同事路径
| 角色 | 工作区路径 |
|------|-----------|
| product-agent（本 agent） | `~/.openclaw/workspace-product` |
| data-agent（数据分析师） | `~/.openclaw/workspace-data` |
| frontend-agent（前端工程师） | `~/.openclaw/workspace-frontend` |

- 项目实际文件：`workspace-frontend/projects/<项目>/`（如有，填实际路径）
- 飞书插件 skill 目录：`~/.openclaw/extensions/feishu-openclaw-plugin/skills/`

## 项目速查
- 具体项目：见本工作区 `projects/<项目名>/context.md`（权威上下文，先读它）。

## 常用操作
- 列目录：`Get-ChildItem <path> -Force`（Windows）或 `ls -la <path>`（Linux/macOS）
- 读文件：`Get-Content <path>` / `cat <path>`
- 各 agent 专属脚本：见各自 scripts/ 目录

## Git（仅当你确实需要提交/推送时）
- git 路径与代理设置：按实际环境填写（示例：Windows 下 push 可能需要 `-c http.proxy=http://127.0.0.1:7890`）

## 群聊协作
- 在群里 @ 同事的格式：`<at user_id="对方user_id">对方名字</at>`（写在回复末尾）
- 发文档/表格类产物前，先读飞书 channel-rules skill（`feishu-channel-rules/SKILL.md`）确认格式规范。

## 边界提醒
- 不把凭据/私密信息写入任何会被群共享的文件。
- 涉及真实版本名、福利、日期等数字：必须核实来源（从关联文章提取/查证）才能写，不能编。