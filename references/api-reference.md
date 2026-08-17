# 飞书 API 参考

所有端点基于 `https://open.feishu.cn`，请求头 `Authorization: Bearer <tenant_access_token>`。
官方文档：https://open.feishu.cn/document

## 认证

### 获取 tenant_access_token
```
POST /open-apis/auth/v3/tenant_access_token/internal
Body: {"app_id": "cli_xxx", "app_secret": "xxx"}
```
返回 `data.tenant_access_token`，有效期约 2 小时。

## IM 消息

### 发送消息
```
POST /open-apis/im/v1/messages?receive_id_type=chat_id
Body: {
  "receive_id": "oc_xxx",
  "msg_type": "text",
  "content": "{\"text\":\"你好\"}"
}
```
`receive_id_type` 支持 `open_id`（私聊 ou_xxx）/ `chat_id`（群聊 oc_xxx）。
`msg_type` 常用：text、post（富文本）、image、interactive（卡片）。
- text content：`{"text":"内容"}`
- post content：`{"zh_cn":{"title":"标题","content":[[{"tag":"text","text":"正文"}]]}}`

### 读取消息
```
GET /open-apis/im/v1/messages?container_id_type=chat&container_id=oc_xxx&page_size=20
```

### 搜索消息（需用户身份，CLI 未实现）
官方端点：`POST /open-apis/search/v2/message`（旧版，需 `search:message` scope）；
新版参考：`im-v1/message/search`。
搜索类接口要求用户身份（`user_access_token`，OAuth），本 CLI 使用应用身份无法调用，
故不提供 `search-messages` 子命令；如需搜索请参考原版 openclaw skill（`feishu-im-read`）。

### 下载消息资源（图片/文件/音频/视频）
```
GET /open-apis/im/v1/messages/{message_id}/resources/{file_key}?type=image
```
`type` 取 `image`（img_xxx）或 `file`（file_xxx）。消息正文中的资源标记：
- 图片：`![image](img_xxx)` → type=`image`
- 文件/音频/视频：`<file key="file_xxx" .../>` 等 → type=`file`
文件上限 100MB；不支持下载表情包和卡片内资源。

## 日历 Calendar

Base URL：`/open-apis/calendar/v4/calendars/primary`（应用主日历）

### 查看日程
```
GET .../events?start_time=<epoch秒>&end_time=<epoch秒>&page_size=50
```
不带时间范围则返回当前主日历日程。

### 创建日程
```
POST .../events
Body: {
  "summary": "周会",
  "description": "说明",
  "start_time": {"timestamp": "1784440800"},
  "end_time": {"timestamp": "1784444400"}
}
```
时间参数使用 epoch 秒（脚本内 `parse_dt` 支持 ISO-8601 自动转换）。

## 任务 Task

Base URL：`/open-apis/task/v2`

### 创建任务
```
POST /open-apis/task/v2/tasks
Body: {"summary": "写周报", "due": {"timestamp": "..."}}
```

### 查看任务
```
GET /open-apis/task/v2/tasks?page_size=50&completed=false
```
`completed` 取 `true`/`false`。只能访问自己是成员的任务。

### 更新任务
```
PATCH /open-apis/task/v2/tasks/{task_guid}
Body: {"summary": "新标题", "update_fields": ["summary"]}
```
标记完成：`{"completed": true, "update_fields": ["completed"]}`。
改截止：`{"due": {"timestamp": "..."}, "update_fields": ["due"]}`。

## 云文档 Docx

Base URL：`/open-apis/docx/v1`

### 创建文档
```
POST /open-apis/docx/v1/documents
Body: {"title": "会议纪要"}
```
返回 `document.document_id`（doxcnXXX）与 `url`。

### 读取正文
```
GET /open-apis/docx/v1/documents/{document_id}/raw_content
```
返回 `document.content` 纯文本正文。

### 追加段落（文本块）
```
POST /open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children
Body: {"children": [{"block_type": 2, "text": {"elements": [{"text_run": {"content": "第一段"}}]}}]}
```
`document_id` 即根块 id。`block_type=2` 为文本块。

## 错误码

响应 JSON 的 `code` 字段：
- `0` 成功
- `99991672` 应用未开通对应权限（`msg` 中会列出缺失的 scope，按提示补开）
- `99991661`/`99991663` 无权限或应用未开通对应权限
- `99991668`/`99991669` token 无效/过期（重新获取）
- `1254011` 等 4 位码：多为参数错误，看 `msg`

## 权限清单（开发者后台「权限管理」）

| 权限 | 作用 |
|------|------|
| im:message | 读取消息 |
| im:message:send_as_bot | 以机器人身份发消息 |
| im:chat | 读取群信息 |
| bitable:app | 多维表格读写 |
| bitable:app:readonly | 多维表格只读 |
| calendar:calendar | 日历读写 |
| calendar:calendar.event | 日历日程读写 |
| calendar:calendar.event:create | 创建日程 |
| task:task:write | 任务读写 |
| task:task:read | 任务只读 |
| docx:document | 云文档读写 |
| docx:document:create | 创建云文档 |

## 多维表格 Bitable

Base URL：`/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}`

### 列出记录（search 已替代 list）
```
POST .../records/search
Body: {"page_size": 50}
```

### 过滤查询
```
POST .../records/search
Body: {
  "filter": {
    "conjunction": "and",
    "conditions": [
      {"field_name": "状态", "operator": "is", "value": ["待办"]}
    ]
  },
  "page_size": 50
}
```
常用 operator：is、isNot、contains、doesNotContain、isEmpty、isNotEmpty、isGreater、isLess。

### 新建记录
```
POST .../records
Body: {"fields": {"标题": "值", "数字": 1, "状态": "待办"}}
```

### 更新记录
```
PUT .../records/{record_id}
Body: {"fields": {"状态": "已完成"}}
```

### 删除记录
```
DELETE .../records/{record_id}
```

### 字段类型值格式
| 字段类型 | 传值 |
|---------|------|
| 文本 | 字符串 `"你好"` |
| 数字 | 数值 `42` 或字符串 `"42"` |
| 单选 | 字符串 `"选项1"` |
| 多选 | 字符串数组 `["选项1","选项2"]` |
| 日期 | 毫秒时间戳 `1674206443000` |
| 人员 | 数组 `[{"id":"ou_xxx"}]` |
| 复选框 | 布尔 `true` / `false` |

## 错误码

响应 JSON 的 `code` 字段：
- `0` 成功
- `99991672` 应用未开通对应权限（`msg` 中会列出缺失的 scope，按提示补开）
- `99991661`/`99991663` 无权限或应用未开通对应权限
- `99991668`/`99991669` token 无效/过期（重新获取）
- `1254011` 等 4 位码：多为参数错误，看 `msg`

## 权限清单（开发者后台「权限管理」）

| 权限 | 作用 |
|------|------|
| im:message | 读取消息 |
| im:message:send_as_bot | 以机器人身份发消息 |
| im:chat | 读取群信息 |
| bitable:app | 多维表格读写 |
| bitable:app:readonly | 多维表格只读 |
| calendar:calendar | 日历读写 |
| calendar:calendar.event | 日历日程读写 |
| calendar:calendar.event:create | 创建日程 |
| task:task:write | 任务读写 |
| task:task:read | 任务只读 |
| docx:document | 云文档读写 |
| docx:document:create | 创建云文档 |
