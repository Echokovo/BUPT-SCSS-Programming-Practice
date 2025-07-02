import jwt
import time
from datetime import datetime, timedelta

class TokenUtils:
    """
    JWT Token工具类，用于生成和验证token
    """
    
    def __init__(self, secret_key="your-secret-key-here"):
        self.secret_key = secret_key
    
    def generate_token(self, user_id, expires_in=3600):
        """
        生成JWT token
        :param user_id: 用户ID
        :param expires_in: 过期时间（秒），默认1小时
        :return: JWT token字符串
        """
        payload = {
            'user_id': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """
        验证JWT token
        :param token: JWT token字符串
        :return: (is_valid, user_id) 元组
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            return True, user_id
        except jwt.ExpiredSignatureError:
            return False, "Token已过期"
        except jwt.InvalidTokenError:
            return False, "Token无效"
    
    def decode_token(self, token):
        """
        解码JWT token（不验证签名，仅用于调试）
        :param token: JWT token字符串
        :return: payload字典
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.InvalidTokenError as e:
            return {"error": str(e)}
    
    def get_token_info(self, token):
        """
        获取token信息（用于调试）
        :param token: JWT token字符串
        :return: token信息字典
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {
                "user_id": payload.get('user_id'),
                "issued_at": datetime.fromtimestamp(payload.get('iat', 0)),
                "expires_at": datetime.fromtimestamp(payload.get('exp', 0)),
                "is_expired": payload.get('exp', 0) < time.time()
            }
        except jwt.InvalidTokenError as e:
            return {"error": str(e)}

# 全局实例
token_utils = TokenUtils()

def generate_test_token(user_id="test_user"):
    """
    生成测试用的token
    :param user_id: 用户ID
    :return: token字符串
    """
    return token_utils.generate_token(user_id, expires_in=3600)

if __name__ == "__main__":
    # 测试token生成和验证
    user_id = "alice"
    token = generate_test_token(user_id)
    print(f"生成的token: {token}")
    
    is_valid, result = token_utils.verify_token(token)
    print(f"验证结果: {is_valid}, 用户ID: {result}")
    
    info = token_utils.get_token_info(token)
    print(f"Token信息: {info}") 