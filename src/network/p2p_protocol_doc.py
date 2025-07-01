p2p_protocol_doc = """
# 客户端-客户端 P2P 通信接口文档

## 1. 通信方式
- 协议：TCP Socket
- 数据格式：JSON（每条消息为一条完整的JSON字符串）
- 加密方式：消息内容用AES对称加密，AES密钥用RSA公钥加密协商

## 2. 消息结构
### 2.1 发送/接收消息
{
    "timestamp": 1710000000,                // int, Unix时间戳
    "message": {
        "type": "text",                     // string, 消息类型（如 'text', 'picture'）
        "content": "base64/aes密文"         // string, 用AES加密后的消息内容（base64编码）
    },
    "sender": "alice@example.com",          // string, 发送者邮箱
    "receiver": "bob@example.com"           // string, 接收者邮箱
}

## 3. P2P通信流程
### 3.1 建立P2P连接
1. 获取对方公网IP和P2P端口（通过服务器API /user/get_peer）
2. 客户端调用 add_peer(email, ip, port)，将好友加入本地P2P管理器
3. 建立TCP连接，发送方用socket连接对方的IP和端口

### 3.2 密钥协商与加密
1. 获取对方公钥（通过服务器API /user/public_key）
2. 生成对称密钥（如16字节AES密钥）
3. 用对方公钥加密AES密钥，作为密钥协商消息单独发送（或在第一条消息中带上）
4. 聊天内容用AES加密，base64编码后填入 message.content 字段

### 3.3 消息发送
- 发送方将上述JSON结构通过socket发送给对方
- 每条消息为一条完整的JSON字符串

### 3.4 消息接收与解密
1. 接收方收到消息后：
   - 如果是密钥协商消息，用私钥解密获得AES密钥
   - 如果是普通消息，用协商好的AES密钥解密 message.content 字段，获得明文内容

## 4. 特殊消息类型
### 4.1 密钥协商消息（可选）
{
    "timestamp": 1710000000,
    "message": {
        "type": "key_exchange",
        "content": "base64/rsa加密的AES密钥"
    },
    "sender": "alice@example.com",
    "receiver": "bob@example.com"
}
- 首次通信时，发送方先发送此类型消息，协商AES密钥

## 5. 错误与状态
- P2P通信本身不返回HTTP状态码，建议在消息结构中增加 status 字段用于错误提示（如解密失败、对方不在线等）
- 失败时可回退到服务器转发

## 6. 示例流程
1. Alice 获取 Bob 的IP、端口、公钥
2. Alice 生成AES密钥，用Bob公钥加密，发送key_exchange消息
3. Bob收到后用私钥解密，保存AES密钥
4. Alice用AES加密消息内容，发送普通消息
5. Bob用AES密钥解密消息内容

## 7. 端到端安全说明
- 消息内容全程加密，只有通信双方能解密
- AES密钥协商通过RSA公钥加密，防止中间人窃取

## 8. 典型代码片段（伪代码）

# 发送方
# 生成AES密钥
aes_key = generate_aes_key()
# 用对方公钥加密AES密钥
encrypted_key = rsa_encrypt(aes_key, peer_public_key)
send_json({
    "timestamp": now(),
    "message": {"type": "key_exchange", "content": base64(encrypted_key)},
    "sender": my_email,
    "receiver": peer_email
})
# 发送加密消息
ciphertext = aes_encrypt("你好", aes_key)
send_json({
    "timestamp": now(),
    "message": {"type": "text", "content": base64(ciphertext)},
    "sender": my_email,
    "receiver": peer_email
})

# 接收方
if message['message']['type'] == 'key_exchange':
    aes_key = rsa_decrypt(base64_decode(message['message']['content']), my_private_key)
elif message['message']['type'] == 'text':
    plaintext = aes_decrypt(base64_decode(message['message']['content']), aes_key)
""" 