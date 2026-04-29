# Docker容器审计报告
**日期**: 2026-04-25

## 状态

| 项目 | 状态 |
|:--|:--|
| Docker客户端 | ✅ 已安装 (v28.1.1, desktop-linux context) |
| Docker Desktop | ✅ 已安装 (/Applications/Docker.app) |
| Docker守护进程 | ❌ 未运行 (docker.sock不存在) |
| 运行容器 | 无 |
| 可用镜像 | 无 |
| 自定义网络 | 无 |

## 分析
Docker Desktop已安装但未启动。启动后可立即使用容器能力。
LaunchDaemons中com.docker.socket.plist和com.docker.vmnetd.plist存在，说明曾配置过。
一台macOS设备上无容器在运行，属于clean状态。
