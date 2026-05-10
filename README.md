# 未成年人电脑使用监控系统

手机远程控制电脑关机时间，用于防沉迷管理。

## 功能特性

- 远程设置电脑关机时间（定时关机）
- 实时查看电脑在线状态
- 立即关机控制
- 密码认证保护
- 开机自动启动（客户端）
- 隐蔽运行（客户端无窗口）

## 项目结构

```
pc-manager/
├── client/              # PC客户端 (Python)
│   ├── main.py          # 主程序
│   ├── requirements.txt # Python依赖
│   ├── build.bat        # 构建脚本
│   ├── install.bat      # 安装脚本
│   └── uninstall.bat    # 卸载脚本
├── server/              # 服务器端 (Node.js)
│   ├── index.js         # 服务主程序
│   └── package.json     # Node.js依赖
├── web/                 # 手机Web控制页面
│   └── index.html
└── .env.example         # 环境变量示例
```

## 部署步骤

### 1. 服务端部署（阿里云ECS）

```bash
# 克隆仓库
git clone https://github.com/ShyNo11/pc-manager.git
cd pc-manager/server

# 安装依赖
npm install

# 创建环境变量文件
cp ../.env.example .env
nano .env  # 编辑密码配置

# 启动服务（开发模式）
npm start

# 或使用 pm2 守护进程（推荐）
npm install -g pm2
pm2 start index.js --name pc-manager
pm2 save
pm2 startup
```

创建 `.env` 文件，设置密码：
```
PASSWORD=你的密码
```

**开放端口：**

在阿里云控制台 -> ECS实例 -> 安全组 -> 配置规则，添加入方向规则：
- 端口：3000
- 协议：TCP
- 授权对象：0.0.0.0/0

如果服务器开启了防火墙：
```bash
firewall-cmd --zone=public --add-port=3000/tcp --permanent
firewall-cmd --reload
```

### 2. PC客户端安装

在被监控的电脑上操作：

**方式一：直接运行Python脚本（开发测试）**

```bash
cd client
pip install -r requirements.txt
python main.py
```

**方式二：打包成EXE安装（推荐）**

```bash
cd client

# 安装依赖
pip install -r requirements.txt

# 构建EXE
build.bat
# 或手动执行：pyinstaller --onefile --noconsole --name "WindowsUpdateService" main.py

# 安装（以管理员身份运行）
install.bat
```

安装后客户端会：
- 自动复制到 `%APPDATA%\Microsoft\Windows\WindowsUpdateService\`
- 添加开机自启动
- 隐藏窗口运行

**卸载客户端：**

```bash
uninstall.bat
```

### 3. 修改客户端服务器地址

编辑 `client/main.py` 第13行，修改服务器地址：

```python
SERVER_URL = "ws://你的服务器IP:3000"
```

然后重新构建安装。

## 使用说明

### 手机控制

1. 手机浏览器访问 `http://服务器IP:3000`
2. 输入密码登录
3. 查看在线设备列表
4. 选择操作：
   - **立即关机**：电脑立即关闭
   - **定时关机**：设置分钟/秒数后自动关机

### 功能说明

| 功能 | 说明 |
|------|------|
| 设备列表 | 显示所有在线的被监控电脑 |
| 立即关机 | 电脑立即执行关机命令 |
| 定时关机 | 倒计时结束后自动关机 |
| 退出登录 | 清除登录状态 |

## 注意事项

1. **安全建议**
   - 设置强密码保护控制面板
   - 定期更换密码
   - 建议使用HTTPS（需配置SSL证书）

2. **客户端隐蔽性**
   - 客户端伪装成"WindowsUpdateService"系统服务
   - 运行时无窗口显示
   - 开机自动启动

3. **网络要求**
   - 服务端需要公网IP
   - 客户端需要能访问服务器
   - 服务器端口3000需要开放

4. **兼容性**
   - 服务端：Linux/Windows
   - 客户端：仅支持Windows

## 故障排查

**客户端无法连接服务器：**
- 检查服务器是否启动
- 检查防火墙端口是否开放
- 确认客户端SERVER_URL配置正确

**手机无法访问控制页面：**
- 检查服务器是否运行
- 确认阿里云安全组已开放端口
- 检查服务器防火墙设置

**登录失败：**
- 确认服务器端 `.env` 文件已创建并设置密码
- 重启服务器使配置生效