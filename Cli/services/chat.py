from services.clientAPI import ClientAPI, get_client_api
from services.serverAPI import serverAPI
from config import CLIENT_CONFIG
import time
from datetime import datetime


def chat_service(chat_data):
    client_api = get_client_api()
    data = chat_data.data.dict()
    friend_id = data['friend_id']
    message = data['message']

    # 1. 检查好友是否在线
    status_resp = serverAPI.get_online_status(friend_id)
    if status_resp.get('status') == 199:
        return {"error": "好友不在线"}, 404

    # 2. 获取好友的公钥和连接信息
    pubkey_resp = serverAPI.get_public_key(friend_id)
    if pubkey_resp.get('status') != 200:
        return {"error": "无法获取好友公钥"}, 404

    pubkey_data = pubkey_resp['data']
    peer_host = pubkey_data['ip']
    peer_port = pubkey_data['port']
    public_key = pubkey_data['public_key'].encode()

    # 3. 建立P2P连接（如果尚未连接）
    peer_id = f"{peer_host}:{peer_port}"
    if peer_id not in client_api.peers:
        client_api.connect(peer_host, peer_port)

    # 4. 建立加密会话（如果尚未建立）
    if peer_id not in client_api._session_keys:
        enc_key = client_api.load_peer_public_key(peer_id, public_key)
        # 在实际应用中需要将enc_key发送给好友完成密钥协商
        # 这里简化流程，直接使用好友的公钥建立会话
        client_api.finalize_session_key(peer_id, enc_key)

    # 5. 发送消息
    try:
        # 处理秘密消息（使用隐写术）
        if message['type'] == 'secret':
            # 生成临时图片路径
            carrier_path = "default_carrier.png"
            output_path = f"steg_{int(time.time())}.png"

            client_api.send(
                peer_id,
                message,
                use_steg=True,
                carrier_image=carrier_path,
                output_image=output_path
            )
        else:
            # 发送普通消息
            client_api.send(peer_id, message)

        return {"status": "消息发送成功"}, 200
    except Exception as e:
        return {"error": f"发送失败: {str(e)}"}, 500


def history_service(history_data):
    """
    获取聊天历史记录
    :param history_data: UserHistoryRequest对象
    :return: (result, status_code)
    """
    data = history_data.data.dict()
    friend_id = data['friend_id']
    client_api = get_client_api()

    try:
        # 从本地数据库获取历史记录
        table = messages.ge
        messages = []

        for record in table.all():
            # 转换时间戳格式
            timestamp = int(datetime.fromisoformat(record['timestamp']).timestamp())

            messages.append({
                "timestamp": timestamp,
                "sender": record['sender_id'],
                "receiver": record['receiver_id'],
                "message": record['message']
            })

        # 按时间戳排序
        messages.sort(key=lambda x: x['timestamp'])

        return {
            "status": 200,
            "message": "成功获取历史记录",
            "data": {
                "length": len(messages),
                "messages": messages
            }
        }, 200
    except Exception as e:
        return {
            "status": 500,
            "message": f"获取历史记录失败: {str(e)}",
            "data": None
        }, 500


def decipher_service(decipher_data):
    try:
        data = decipher_data.data.dict()
        timestamp = data['timestamp']
        client_api = get_client_api()

        # 遍历所有会话（peer）以查找匹配时间戳
        for peer_id in client_api._message_dbs:
            table = client_api._get_message_table(peer_id)
            for record in table.all():
                if record.get("timestamp") == timestamp and record.get("image_path"):
                    # 调用ClientAPI提取图像并解密内容
                    result = client_api.extract_stego_by_timestamp(peer_id, timestamp)
                    return {
                        "status": 200,
                        "message": "解密成功",
                        "data": {
                            "plain_text": result
                        }
                    }, 200

        return {
            "status": 404,
            "message": "找不到对应的隐写图片消息",
            "data": None
        }, 404
    except Exception as e:
        return {
            "status": 500,
            "message": f"解密失败: {str(e)}",
            "data": None
        }, 500
