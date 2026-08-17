# 飞书机器人 opencode Skill

把 openclaw 的飞书机器人能力提炼成独立的 opencode skill：直连飞书开放平台 API，
收发 IM 消息、读写多维表格（Bitable）。零第三方依赖，纯 Python 标准库。

## 特性

- 发送文本 / 富文本消息到飞书群
- 读取群聊最近消息
- 多维表格记录：列出 / 过滤查询 / 新建 / 更新 / 删除
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
```

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
```

## License

MIT
