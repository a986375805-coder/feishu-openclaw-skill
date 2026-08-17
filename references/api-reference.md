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
