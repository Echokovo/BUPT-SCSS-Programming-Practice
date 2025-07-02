"""
安全聊天客户端接口文档
====================

统一 Response 结构
{
    "status": "int, 状态码",
    "message": "string, Debug信息", 
    "data": "object, 响应内容"
}

C/S接口中登录后附带 token 的方式
可参考 https://blog.csdn.net/weixin_45081575/article/details/135890083

url = 'http://127.0.0.1:5000/protected'
headers = {
    'Authorization': f'Bearer {token}'
}
resp = requests.get(url, headers=headers)
"""

# ================== 前后端接口（前端对后端请求）==================

FRONTEND_BACKEND_INTERFACES = {
    "用户注册": {
        "URL": "/register",
        "Method": "POST",
        "Request": {
            "data": {
                "user_id": "string, 用户名",
                "password": "string, 密码", 
                "email": "string, 用户邮箱"
            }
        },
        "Responses": {
            "200": "注册成功",
            "400": "用户名不合法",
            "409": "用户名已存在"
        }
    },
    
    "用户登录": {
        "URL": "/login",
        "Method": "POST", 
        "Request": {
            "data": {
                "user_id": "string, 用户名",
                "password": "string, 用户密码"
            }
        },
        "Responses": {
            "200": "登录成功",
            "401": "密码错误", 
            "404": "用户不存在"
        }
    },
    
    "获取通讯录": {
        "URL": "/contacts",
        "Method": "GET",
        "Response": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "contacts": [
                        {
                            "user_id": "string, 用户名",
                            "flag": "bool, 好友状态位"
                        }
                    ]
                }
            }
        }
    },
    
    "添加好友": {
        "URL": "/contacts",
        "Method": "POST",
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Responses": {
            "200": "添加成功",
            "404": "好友不存在",
            "409": "已提交好友"
        }
    },
    
    "删除好友": {
        "URL": "/contacts", 
        "Method": "DELETE",
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Responses": {
            "200": "删除成功",
            "404": "好友不存在"
        }
    },
    
    "判断是否在线": {
        "URL": "/online",
        "Method": "POST",
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Responses": {
            "200": "在线",
            "400": "用户名不合法或非好友关系"
        }
    },
    
    "获取公钥": {
        "URL": "/public_key",
        "Method": "POST", 
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Responses": {
            "200": {
                "status": "int, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "public_key": "string, 朋友公钥"
                }
            }
        }
    },
    
    "即时通讯": {
        "URL": "/chat",
        "Method": "POST",
        "Request": {
            "data": {
                "friend_id": "string, 接收者用户名",
                "message": {
                    "type": "string, 消息类型['text', 'picture', 'secret', 'steg_picture']",
                    "content": "string, 消息内容"
                },
                "use_steganography": "bool, 是否使用隐写术（可选，默认false）",
                "steg_img_template": "string, 隐写模板图片路径（当use_steganography为true时必需）"
            }
        },
        "Response": {
            "200": "发送成功",
            "404": "发送失败",
            "400": "隐写参数错误"
        }
    },
    
    "聊天历史查询": {
        "URL": "/history",
        "Method": "POST",
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Response": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "length": "int, 消息数组长度",
                    "messages": [
                        {
                            "timestamp": "int, Unix时间戳",
                            "sender": "string, 发送者用户名",
                            "receiver": "string, 接收者用户名", 
                            "message": {
                                "type": "string, 消息类型['text', 'picture', 'secret']",
                                "content": "string, 消息内容"
                            }
                        }
                    ]
                }
            }
        }
    }
}

# ================== C/S 接口文档（客户端对服务器请求）==================

CLIENT_SERVER_INTERFACES = {
    "用户注册": {
        "URL": "/register",
        "Method": "POST",
        "Request": {
            "data": {
                "user_id": "string, 用户名",
                "password": "string, 密码",
                "email": "string, 用户邮箱"
            }
        },
        "Responses": {
            "200": "注册成功",
            "400": "参数不合法",
            "409": "用户名已存在"
        }
    },
    
    "用户登录": {
        "URL": "/login",
        "Method": "POST",
        "Request": {
            "data": {
                "user_id": "string, 用户名",
                "password": "string, 用户密码",
                "public_key": "string, 用户公钥",
                "ip": "string, 用户ip",
                "port": "int, 用户监听的端口"
            }
        },
        "Responses": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "token": "string, 登陆token"
                }
            },
            "400": "参数不合法",
            "401": "密码错误",
            "404": "用户不存在",
            "409": "用户已登陆"
        }
    },
    
    "获取通讯录": {
        "URL": "/contacts",
        "Method": "GET(token)",
        "Responses": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": [
                    {
                        "user_id": "string, 用户名",
                        "flag": "bool, 好友为True 好友申请为 False"
                    }
                ]
            },
            "404": "用户不存在"
        }
    },
    
    "添加好友": {
        "URL": "/contacts",
        "Method": "POST(token)",
        "Request": {
            "data": {
                "friend_id": "string, 好友名"
            }
        },
        "Responses": {
            "200": "添加成功",
            "400": "参数不合法",
            "404": "用户不存在",
            "409": "好友已添加"
        }
    },
    
    "删除好友": {
        "URL": "/contacts",
        "Method": "DELETE(token)",
        "Request": {
            "data": {
                "friend_id": "string, 好友名"
            }
        },
        "Responses": {
            "200": "删除成功",
            "404": "用户不存在",
            "409": "好友不存在"
        }
    },
    
    "判断是否在线": {
        "URL": "/online",
        "Method": "POST(token)",
        "Request": {
            "data": {
                "friend_id": "string, 好友名"
            }
        },
        "Responses": {
            "199": "好友离线",
            "200": "好友在线",
            "400": "参数不合法",
            "403": "非好友关系",
            "404": "好友不存在"
        }
    },
    
    "获取公钥": {
        "URL": "/public_key",
        "Method": "POST(token)",
        "Request": {
            "data": {
                "friend_id": "string, 好友名"
            }
        },
        "Responses": {
            "199": "好友离线",
            "200": {
                "status": "int, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "public_key": "string, 好友公钥"
                }
            },
            "400": "参数不合法",
            "403": "非好友关系",
            "404": "好友不存在"
        }
    },
    
    "即时通讯": {
        "URL": "/chat",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "friend_id": "string, 接收者用户名",
                "message": {
                    "type": "string, 消息类型['text', 'picture', 'secret', 'steg_picture']",
                    "content": "string, 消息内容"
                },
                "use_steganography": "bool, 是否使用隐写术（可选，默认false）",
                "steg_img_template": "string, 隐写模板图片路径（当use_steganography为true时必需）"
            }
        },
        "Response": {
            "200": "发送成功",
            "404": "发送失败",
            "400": "隐写参数错误"
        }
    },
    
    "聊天历史查询": {
        "URL": "/history",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "friend_id": "string, 朋友名"
            }
        },
        "Response": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "length": "int, 消息数组长度",
                    "messages": [
                        {
                            "timestamp": "int, Unix时间戳",
                            "sender": "string, 发送者用户名",
                            "receiver": "string, 接收者用户名",
                            "message": {
                                "type": "string, 消息类型['text', 'picture', 'secret']",
                                "content": "string, 消息内容"
                            }
                        }
                    ]
                }
            }
        }
    },
    
    "心跳包": {
        "URL": "/heartbeat",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "user_id": "string, 用户名"
            }
        },
        "Response": {
            "200": "心跳成功"
        }
    },
    
    "注册P2P节点": {
        "URL": "/user/register_p2p",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "user_id": "string, 用户名",
                "ip": "string, 节点IP",
                "port": "int, 节点端口"
            }
        },
        "Response": {
            "200": "注册成功"
        }
    },
    
    "获取P2P节点": {
        "URL": "/user/get_peer",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "user_id": "string, 目标用户名"
            }
        },
        "Response": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "ip": "string, 节点IP",
                    "port": "int, 节点端口"
                }
            }
        }
    },
    
    "申请好友": {
        "URL": "/friend/apply",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "friend_id": "string, 好友用户名"
            }
        },
        "Response": {
            "200": "申请成功"
        }
    },
    
    "获取好友申请": {
        "URL": "/friend/requests",
        "Method": "GET",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Response": {
            "200": {
                "status": "integer, 状态码",
                "message": "string, Debug信息",
                "data": {
                    "requests": [
                        {
                            "user_id": "string, 申请者用户名",
                            "timestamp": "int, 申请时间戳"
                        }
                    ]
                }
            }
        }
    },
    
    "处理好友申请": {
        "URL": "/friend/handle",
        "Method": "POST",
        "Headers": {
            "Authorization": "Bearer {token}"
        },
        "Request": {
            "data": {
                "friend_id": "string, 好友用户名",
                "accept": "bool, 是否接受"
            }
        },
        "Response": {
            "200": "处理成功"
        }
    }
}

# ================== 状态码说明 ==================

STATUS_CODES = {
    199: "好友离线",
    200: "成功",
    400: "请求参数错误/参数不合法",
    401: "未授权/密码错误/需要登录或token无效",
    403: "非好友关系",
    404: "资源不存在/用户不存在/好友不存在",
    409: "冲突（如用户名已存在、好友已添加、好友不存在、用户已登陆）",
    500: "服务器内部错误"
}

# ================== 消息类型说明 ==================

MESSAGE_TYPES = {
    "text": "文本消息",
    "picture": "图片消息",
    "secret": "加密消息",
    "steg_picture": "隐写图片消息"
}

# ================== 使用示例 ==================

def get_interface_examples():
    """获取接口使用示例"""
    examples = {
        "注册示例": {
            "curl": 'curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d \'{"data": {"user_id": "alice", "password": "123456", "email": "alice@example.com"}}\'',
            "python": '''
import requests
data = {
    "user_id": "alice",
    "password": "123456", 
    "email": "alice@example.com"
}
response = requests.post("http://localhost:5000/register", json={"data": data})
print(response.json())
'''
        },
        
        "登录示例": {
            "curl": 'curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d \'{"data": {"user_id": "alice", "password": "123456"}}\'',
            "python": '''
import requests
data = {
    "user_id": "alice",
    "password": "123456"
}
response = requests.post("http://localhost:5000/login", json={"data": data})
result = response.json()
if result["status"] == 200:
    token = result["data"]["token"]
    print(f"登录成功，token: {token}")
'''
        },
        
        "发送消息示例": {
            "curl": 'curl -X POST http://localhost:5000/chat -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d \'{"data": {"friend_id": "bob", "message": {"type": "text", "content": "Hello!"}}}\'',
            "python": '''
import requests
headers = {"Authorization": f"Bearer {token}"}
data = {
    "friend_id": "bob",
    "message": {
        "type": "text",
        "content": "Hello!"
    }
}
response = requests.post("http://localhost:5000/chat", json={"data": data}, headers=headers)
print(response.json())
'''
        }
    }
    return examples

if __name__ == "__main__":
    print("安全聊天客户端接口文档")
    print("=" * 50)
    print("\n前后端接口数量:", len(FRONTEND_BACKEND_INTERFACES))
    print("C/S接口数量:", len(CLIENT_SERVER_INTERFACES))
    print("\n状态码说明:")
    for code, desc in STATUS_CODES.items():
        print(f"  {code}: {desc}")
    print("\n消息类型说明:")
    for msg_type, desc in MESSAGE_TYPES.items():
        print(f"  {msg_type}: {desc}") 
