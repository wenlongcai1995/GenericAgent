# macOS LaunchAgents/LaunchDaemons 进程审计报告
**日期**: 2026-04-25

## 1. 用户级 LaunchAgents (~/Library/LaunchAgents) - 9项

| 服务 | 用途 | 来源 |
|:--|:--|:--|
| Adobe CCXProcess | Adobe Creative Cloud 后台 | Adobe |
| EaseUS NTFS | NTFS磁盘格式支持 | EaseUS |
| Google Keystone ×2 | Google软件自动更新 | Google |
| Google Updater Wake | Google更新唤醒 | Google |
| ShadowsocksX-NG ×3 | 代理/VPN客户端 | Shadowsocks |
| Steam Clean | Steam游戏平台 | Valve |

## 2. 系统级 LaunchAgents (/Library/LaunchAgents) - 11项

| 服务 | 用途 | 来源 |
|:--|:--|:--|
| Citrix ×3 | 远程桌面/虚拟化 | Citrix |
| Microsoft Update | Office更新 | Microsoft |
| Paragon NTFS Notification | NTFS支持通知 | Paragon |
| Sangfor ECAgentProxy | VPN/安全接入 | Sangfor(深信服) |
| Sogou ×2 | 输入法/任务管理 | Sogou(搜狗) |
| TeamViewer ×2 | 远程协助 | TeamViewer |

## 3. 系统级 LaunchDaemons (/Library/LaunchDaemons) - 20项

| 服务 | 用途 | 备注 |
|:--|:--|:--|
| AdGuard ×2 | 广告过滤(PAC/TUN) | 网络层 |
| Adobe ×2 | Flash/ACC安装 | |
| Citrix ×2 | 虚拟化USB/更新 | |
| Docker ×2 | 容器引擎socket/vmnet | ❌ 未运行 |
| EaseUS NTFS Daemon | NTFS支持 | |
| LeiGod Helper | 游戏加速器 | 雷神加速器 |
| Microsoft ×2 | Office许可/更新 | |
| MySQL (Oracle) | 数据库服务 | Oracle MySQL |
| Omi NTFS | NTFS工具 | |
| Paragon NTFS ×3 | NTFS驱动/加载 | |
| Sangfor EasyMonitor | VPN监控 | |
| TeamViewer Helper/Svc | 远程协助服务 | |
| ClashX ProxyConfig | 代理配置 | ClashX |

## 关键发现
- **网络/代理相关**: ShadowsocksX-NG, ClashX, Sangfor, AdGuard - 多代理栈
- **NTFS工具**: EaseUS, Paragon, Omi - 3种NTFS方案共存，可能冲突
- **数据库**: MySQL已安装(LaunchDaemon)但未确认运行
- **远程协助**: TeamViewer + Citrix
