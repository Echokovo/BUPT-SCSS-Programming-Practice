# Server

## 运行

### 配置



### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行项目

```bash
python app.py
```

## 项目结构

```
.
├── app.py                      # 应用入口文件
├── config.py                   # 配置文件（开发、测试、生产环境配置）
├── README.md                   # 项目说明文档
├─ models/                      # 数据模型层
│    ├── contacts.py            # 联系人数据模型
│    ├── database.py            # 数据库初始化与连接配置
│    ├── online.py              # 在线状态相关模型
│    ├── users.py               # 用户模型
│    └── __init__.py            # 初始化
│
├─ routes/                      # 路由层（API 接口定义）
│    ├── auth.py                # 认证相关路由
│    ├── contacts.py            # 联系人相关路由
│    ├── utils.py               # 工具类路由
│    └── __init__.py            # 初始化
│
├─ schemas/                     # 数据序列化/验证模型（如使用 Marshmallow 或 Pydantic）
│    ├── auth.py                # 认证相关 Schema
│    ├── contacts.py            # 联系人相关 Schema
│    ├── utils.py               # 工具类 Schema
│    └── __init__.py            # 初始化
│
└─ services/                    # 业务逻辑层
     ├── auth.py                # 认证相关的服务逻辑
     ├── contacts.py            # 联系人管理服务逻辑
     ├── utils.py               # 公共工具函数或服务
     └── __init__.py            # 初始化
```

