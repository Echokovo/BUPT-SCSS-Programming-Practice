from src.core.client import SecureChatClient
import signal
import sys

# 主程序入口：启动客户端，处理系统信号（如Ctrl+C），命令行交互。

def signal_handler(sig, frame):
    print("\nShutting down client...")
    client.stop()
    sys.exit(0)

if __name__ == "__main__":
    client = SecureChatClient()
    client.start()

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Secure Chat Client running. 支持命令: register, login, add, del, search, history, contacts, send, quit")

    while True:
        cmd = input("请输入命令: ").strip()
        if cmd.startswith("register"):
            # 注册: register 用户名 邮箱 密码
            try:
                _, user_id, email, password = cmd.split()
                resp = client.register(user_id, password, email)
                print(resp)
            except Exception:
                print("用法: register 用户名 邮箱 密码")

        elif cmd.startswith("login"):
            # 登录: login 用户名 密码
            try:
                _, user_id, password = cmd.split()
                resp = client.login(user_id, password)
                print(resp)
            except Exception:
                print("用法: login 用户名 密码")

        elif cmd.startswith("add"):
            # 加好友: add 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.add_contact(friend_id)
                print(resp)
            except Exception:
                print("用法: add 用户名")

        elif cmd.startswith("apply"):
            # 申请加好友: apply 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.apply_friend(friend_id)
                print(resp)
            except Exception:
                print("用法: apply 用户名")

        elif cmd == "requests":
            # 查看收到的好友申请
            resp = client.get_friend_requests()
            print(resp)

        elif cmd.startswith("accept"):
            # 同意好友申请: accept 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.handle_friend_request(friend_id, accept=True)
                print(resp)
            except Exception:
                print("用法: accept 用户名")
                
        elif cmd.startswith("reject"):
            # 拒绝好友申请: reject 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.handle_friend_request(friend_id, accept=False)
                print(resp)
            except Exception:
                print("用法: reject 用户名")

        elif cmd.startswith("del"):
            # 删好友: del 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.delete_contact(friend_id)
                print(resp)
            except Exception:
                print("用法: del 用户名")

        elif cmd.startswith("search"):
            # 查用户: search 用户名
            try:
                _, user_id = cmd.split()
                resp = client.search_user(user_id)
                print(resp)
            except Exception:
                print("用法: search 用户名")

        elif cmd.startswith("history"):
            # 查历史: history 用户名
            try:
                _, friend_id = cmd.split()
                resp = client.get_history(friend_id)
                print(resp)
            except Exception:
                print("用法: history 用户名")

        elif cmd == "contacts":
            # 查通讯录
            resp = client.get_contacts()
            print(resp)

        elif cmd.startswith("send"):
            # 发消息: send 用户名 消息内容
            try:
                _, friend_id, *content = cmd.split()
                content = ' '.join(content)
                resp = client.send_message(friend_id, content)
                print(resp)
            except Exception:
                print("用法: send 用户名 消息内容")
                
        elif cmd == "quit":
            client.stop()
            break
        else:
            print("未知命令。支持: register, login, add, del, search, history, contacts, send, quit")