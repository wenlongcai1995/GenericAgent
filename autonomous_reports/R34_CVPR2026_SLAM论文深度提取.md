# R34 CVPR/ICRA 2026 SLAM论文深度提取
**时间**: 2026-04-30
**类型**: 实时知识提取
**对应**: TODO2
**源**: arXiv/silent_fetch/GitHub README

---

## 全景总览

| 排名 | 方向 | 论文 | 团队 | 会议 | 创新点 | 代码状态 |
|------|------|------|------|------|--------|----------|
| 🥇 | 动态场景鲁棒SLAM | **DROID-SLAM in the Wild** (arXiv 2603.19076) | Li Moyang, Zihan Zhu, Marc Pollefeys, Daniel Barath (ETH Zurich) | CVPR 2026 | 不确定性感知BA + 可微深度渲染滤波动态物体 | 未开源 |
| 🥇 | 动态场景鲁棒SLAM | **π³-mos-SLAM** (arXiv 2512.06868) | Xingguang Zhong, Liren Jin, Marija Popović, Jens Behley, Cyrill Stachniss (Bonn) | CVPR 2026 | 泛化3D先验 + 几何patch BA + 前馈重建滤波动态区域 | ✅ [开源](https://github.com/PRBonn/Pi3MOS-SLAM) |
| 🥈 | 3DGS SLAM | **VarSplat** (arXiv 2603.09673) | — | CVPR 2026 | 不确定性感知3DGS-SLAM: 逐splat外观方差 + 总方差律α合成 | 未开源 |
| 🥈 | 3DGS SLAM | **AERGS-SLAM** (Poster #38205) | — | CVPR 2026 | 3DGS SLAM方法, Poster展示 | 待确认 |
| 🥉 | Event相机SLAM | **Edged USLAM** | — | ICRA 2026 | 事件相机SLAM, 边缘特征提取 | 待确认 |

---

## 深度分析

### 🥇 热点1: 动态场景鲁棒SLAM

#### 1.1 DROID-SLAM in the Wild
- **核心问题**: 传统SLAM假设静态场景，动态物体导致跟踪失败
- **方法关键**:
  1. 基于可微深度渲染的**动态区域滤波**——利用渲染深度与观测深度的差异检测动态区域
  2. **不确定性感知Bundle Adjustment**——对动态区域的特征点赋予低权重，减少对位姿估计的影响
  3. 实时RGB SLAM系统（非RGB-D，强调纯RGB输入）
- **贡献**: 在动态/杂乱场景中鲁棒跟踪，无需预定义动态先验
- **验证基准**: TUM RGB-D动态序列、ScanNet（真实世界）

#### 1.2 π³-mos-SLAM
- **核心问题**: 单目SLAM在动态自然环境中精度恶化
- **方法关键**:
  1. **泛化前馈重建模型**（feed-forward reconstruction model）精确定位动态区域
  2. **几何patch BA**（patch-based bundle adjustment）保持几何一致性
  3. 深度预测与BA patch对齐，处理**尺度歧义**
  4. 纯单目（monocular），无需深度传感器
- **贡献**: 结合前馈模型与几何BA的互补优势
- **验证基准**: 动态自然环境数据集
- **开源**: ✅ 完整代码 + 补充材料

---

### 🥈 热点2: 3DGS SLAM

#### 2.1 VarSplat
- **核心问题**: 现有3DGS-SLAM隐式处理测量可靠性，在低纹理/透明/反射表面产生漂移
- **方法关键**:
  1. **不确定性感知3DGS**：显式学习每个splat的外观方差
  2. **总方差律+α合成**：计算渲染颜色的总不确定性，指导BA优化和新增splat采样
  3. 实现更鲁棒的高斯地图构建
- **贡献**: 首个显式不确定性建模的3DGS-SLAM
- **验证基准**: Replica (合成)、TUM-RGBD、ScanNet、ScanNet++ (真实世界)
- **效果**: 跟踪/建图/新视图合成均优于现有RGB-D SLAM

#### 2.2 AERGS-SLAM
- **信息有限**: CVPR 2026 Poster #38205，具体方法待论文公开

---

### 🥉 热点3: Event相机SLAM

#### 3.1 Edged USLAM
- **方向**: Event-based SLAM，利用事件相机高动态范围/低延迟特性
- **方法**: 边缘特征提取 + USLAM框架
- **会议**: ICRA 2026
- **信息有限**: 处于探索期，论文待深入阅读

---

## 🔬 可验证趋势

### 趋势1: 不确定性建模成为SLAM标配
- DROID-SLAM in the Wild: 不确定性感知BA（特征级不确定性）
- VarSplat: 不确定性感知3DGS（splat级外观方差）
- **→ 信号**: 显式不确定性估计正在替代隐式鲁棒性机制

### 趋势2: 前馈/泛化模型辅助SLAM
- π³-mos-SLAM使用**前馈重建模型**过滤动态区域
- 与传统几何方法互补，而非完全替代
- **→ 信号**: 2D/3D基础模型正在作为SLAM模块组件集成

### 趋势3: 3DGS SLAM走出实验室
- VarSplat + AERGS-SLAM 表明3DGS-SLAM已从概念验证进入方法改进阶段
- 不确定性建模+3DGS是核心改进方向

---

## 📎 引用来源

| 论文 | URL | 提取长度 |
|------|-----|----------|
| DROID-SLAM in the Wild | https://arxiv.org/abs/2603.19076 | 3380 char (arXiv) |
| VarSplat | https://arxiv.org/abs/2603.09673 | 3916 char (arXiv) |
| π³-mos-SLAM | https://arxiv.org/abs/2512.06868 | 6797 char (GitHub README) |
| Pi3MOS-SLAM GitHub | https://github.com/PRBonn/Pi3MOS-SLAM | 标题+描述+作者列表 |
| AERGS-SLAM | CVPR 2026 Poster #38205 | R33热探测 |
| Edged USLAM | ICRA 2026 | R33热探测 |