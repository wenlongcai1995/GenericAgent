# R33 CVPR/ICRA 2026 SLAM方向热点探测

**时间**: 2026-04-30 00:22
**类型**: 实时知识探测
**对应**: TODO-B
**源**: arXiv/Paper Digest/GitHub (silent_search + silent_fetch 组合流)

---

## 🏆 热点1: 动态场景鲁棒SLAM — 不确定性感知BA

### DROID-SLAM in the Wild
- **团队**: Li Moyang, Zihan Zhu, Marc Pollefeys, Daniel Barath (ETH Zurich?)
- **发布时间**: 2026.03.19 (arXiv 2603.19076)
- **核心创新**: 可微分不确定性感知束调整(Uncertainty-aware Bundle Adjustment)
- **亮点**: 
  - 逐像素不确定性估计，通过多视角视觉特征不一致性推断
  - 动态场景SOTA相机位姿和场景几何
  - **实时** (~10FPS)
  - 无需预定义动态先验
- **代码**: github.com/MoyangLi00/DROID-W.git
- **原文**: "Our method estimates per-pixel uncertainty by exploiting multi-view visual feature inconsistency, enabling robust tracking and reconstruction even in real-world environments."

### Pi³MOS-SLAM — CVPR 2026
- **团队**: Xingguang Zhong, Liren Jin, Marija Popović, Jens Behley, Cyrill Stachniss (Univ. Bonn)
- **核心**: Dynamic Visual SLAM using a General 3D Prior
- **亮点**: CVPR 2026已接收，代码已开源 (PRBonn/Pi3MOS-SLAM)
- **方法**: 基于DPVO网络，融合通用3D先验处理动态场景

### 🔍 趋势判断
> 动态场景SLAM正在从"检测已知动态物体"进化到"逐像素不确定性估计"，不再需要预定义动态类别。DROID-W和Pi³MOS代表两条路线：端到端可微分BA vs 3D先验引导。

---

## 🏆 热点2: 3D Gaussian Splatting (3DGS) + SLAM 大爆发

### VarSplat — Uncertainty-aware 3DGS SLAM
- **团队**: Anh Thuan Tran, Jana Kosecka (George Mason University)
- **发布时间**: 2026.03.10 (arXiv 2603.09673)
- **核心创新**: 显式学习每个高斯点的外观方差(appearance variance)，通过alpha compositing渲染可微逐像素不确定性图
- **亮点**:
  - 处理低纹理区域、透明表面、复杂反射表面
  - 不确定性引导跟踪/子图配准/闭环检测
  - 在Replica/TUM-RGBD/ScanNet/ScanNet++上SOTA或相当
- **原文**: "We introduce VarSplat, an uncertainty-aware 3DGS-SLAM system that explicitly learns per-splat appearance variance... This map guides tracking, submap registration, and loop detection toward focusing on reliable regions"

### AERGS-SLAM — CVPR 2026 Poster
- **标题**: Auto-Exposure-Robust Stereo 3D Gaussian Splatting for SLAM
- **角度**: 曝光鲁棒的双目3DGS-SLAM

### 🔍 趋势判断
> 3DGS SLAM在2026年进入成熟期，方向从"验证可行性"转向"解决实际问题"(低纹理/透明/复杂反射)。不确定性感知成为3DGS-SLAM的核心能力。

---

## 🏆 热点3: Event-based SLAM 和神经形态视觉

### Edged USLAM — ICRA 2026
- Edge-Aware Event-Based SLAM with Learned Depth
- 事件相机SLAM从"实验室环境"走向"野外场景"

### 🔍 趋势判断
> 事件相机SLAM是ICRA 2026重点方向(有Neurormorphic Field Robotics Workshop)，但总体活跃度低于3DGS SLAM。

---

## 📊 汇总: 三大热点排名

| 排名 | 方向 | 代表工作 | 热度 | 成熟度 |
|:---:|:-----|:---------|:----:|:-----:|
| 🥇 | Dynamic SLAM (不确定性BA) | DROID-W, Pi³MOS | 🔥🔥🔥🔥 | 高(代码已开源) |
| 🥈 | 3DGS SLAM | VarSplat, AERGS-SLAM | 🔥🔥🔥🔥🔥 | 高(多论文+CVPR) |
| 🥉 | Event-based SLAM | Edged USLAM | 🔥🔥🔥 | 中(探索期) |

## 📎 原文引用来源
1. arXiv 2603.19076 - DROID-SLAM in the Wild
2. arXiv 2603.09673 - VarSplat
3. PRBonn/Pi3MOS-SLAM (GitHub) - CVPR 2026
4. CVPR 2026 Poster #38205 - AERGS-SLAM
5. Paper Digest: CVPR 2026 (>4,000 accepted papers, Denver)
