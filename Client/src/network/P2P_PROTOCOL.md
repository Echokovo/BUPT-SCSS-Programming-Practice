# P2P接口文档

本节描述客户端与客户端之间（P2P直连）通信的消息协议。
每条消息均为JSON格式，通过加密的socket发送。

---

## 1. 消息发送

**Type**: `SEND_MESSAGE`

**Request:**
```json
{
    "type": "SEND_MESSAGE",
    "data": {
        "sender_id": "string, 发送方用户名",
        "receiver_id": "string, 接收方用户名",
        "content": "string, 消息内容",
        "msg_type": "string, 消息类型（如 text, image, file）",
        "timestamp": "int, 发送时间戳"
    }
}
```

**Response:**
```json
{
    "type": "SEND_MESSAGE_ACK",
    "data": {
        "status": 200,
        "message": "消息已收到"
    }
}
```

---

## 2. 公钥交换

**Type**: `PUBLIC_KEY_EXCHANGE`

**Request:**
```json
{
    "type": "PUBLIC_KEY_EXCHANGE",
    "data": {
        "user_id": "string, 发送方用户名",
        "public_key": "string, 发送方公钥"
    }
}
```

**Response:**
```json
{
    "type": "PUBLIC_KEY_EXCHANGE_ACK",
    "data": {
        "status": 200,
        "message": "公钥已收到"
    }
}
```

---

## 3. 心跳检测

**Type**: `HEARTBEAT`

**Request:**
```json
{
    "type": "HEARTBEAT",
    "data": {
        "user_id": "string, 发送方用户名",
        "timestamp": "int, 当前时间戳"
    }
}
```

**Response:**
```json
{
    "type": "HEARTBEAT_ACK",
    "data": {
        "status": 200,
        "message": "心跳正常"
    }
}
```

---

## 4. 文件/图片传输（可选）

**Type**: `SEND_FILE`

**Request:**
```json
{
    "type": "SEND_FILE",
    "data": {
        "sender_id": "string, 发送方用户名",
        "receiver_id": "string, 接收方用户名",
        "filename": "string, 文件名",
        "filedata": "string, base64编码的文件内容",
        "timestamp": "int, 发送时间戳"
    }
}
```

**Response:**
```json
{
    "type": "SEND_FILE_ACK",
    "data": {
        "status": 200,
        "message": "文件已收到"
    }
}
```

---

## 5. 错误响应

**Type**: `ERROR`

**Response:**
```json
{
    "type": "ERROR",
    "data": {
        "status": 400,
        "message": "错误描述"
    }
}
```

---

## 说明

- 所有P2P消息都应加密传输（建议用对方公钥加密内容）。
- 每条消息都应包含`type`字段，便于区分消息类型。
- 建议所有响应都带`status`和`message`字段，便于调试和错误处理。
- 你可以根据实际需求扩展更多类型。 