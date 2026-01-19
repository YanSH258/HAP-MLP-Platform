
# HAP-MLP Automation Platform (V2)

**HAP-MLP Platform** 是一个基于 Python 构建的自动化工作流系统，旨在连接国产材料模拟软件 **HONPAS** 与机器学习势能训练框架 **DeepMD-kit**。

该平台实现了从**初始结构微扰采样**、**高通量 DFT 任务调度**、**数据清洗**到**相空间可视化分析**的全流程自动化，极大地简化了机器学习势能（MLP）数据集的构建过程。

## ✨ 核心功能

- **自动化采样 (Sampler)**: 基于 `dpdata` 对基态结构进行超胞扩充、随机微扰 (Rattle) 和晶胞形变 (Strain)。
- **物理预筛选 (Validator)**: 在提交计算前自动剔除原子重叠等非物理结构，节省算力。
- **任务调度 (Scheduler)**: 自动生成任务目录、分发赝势文件，并对接 Slurm 集群进行批量作业提交。
- **数据清洗 (Cleaner)**: 基于几何准则和统计学方法 (Z-score)，自动剔除 DFT 计算发散或能量异常的脏数据。
- **可视化分析 (Analyzer)**: 计算 SOAP 描述符并进行 PCA 降维，可视化数据集的相空间覆盖情况。

## 📂 目录结构

```text
HAP_project_v2/
├── config.py              # 全局配置文件（路径、计算参数、阈值设置）
├── main.py                # 程序主入口 (CLI)
├── modules/               # 核心功能模块
│   ├── sampler.py         # 结构微扰与生成
│   ├── validator.py       # 几何合理性校验
│   ├── wrapper.py         # 输入文件生成
│   ├── scheduler.py       # 任务与作业管理
│   ├── extractor.py       # 结果提取与格式转换
│   ├── cleaner.py         # 数据质量控制 (QC)
│   ├── analyzer.py        # SOAP/PCA 可视化分析
│   └── workflows.py       # 阶段流程逻辑封装
├── templates/             # HONPAS 输入模板 (.in) 及赝势库
└── data/                  # 数据存储目录
    ├── raw/               # 原始结构 (POSCAR)
    ├── perturbed/         # 微扰结构备份
    ├── training/          # 清洗后的 DeepMD 训练集
    └── analysis/          # 可视化分析报告
```

## 🛠️ 依赖环境

请确保您的计算环境安装了以下 Python 库：

```bash
pip install dpdata ase numpy matplotlib seaborn dscribe scikit-learn
```

---

## 🚀 快速开始

通过 `main.py` 命令行工具控制工作流。

### 参数说明

- `--mode`: 计算模式
  - `scf`: 单点能计算 (用于打标签)
  - `relax`: 结构优化 (用于预处理或基准)
  - `aimd`: 分子动力学 (用于大规模采样)
- `--stage`: 执行阶段
  - `1`: **生成与提交** (Generate & Submit)
  - `2`: **收集与清洗** (Collect & Clean)
  - `3`: **可视化分析** (Analyze)
  - `4`: **模型训练** (Train)
- `--submit`: (仅 Stage 1) 加上此参数才会真实提交作业，否则仅生成文件 (Dry Run)。

### 工作流示例

#### 1. 生成并提交任务 (Stage 1)
生成 50 个微扰结构并提交结构优化任务：

```bash
# 1. 先进行 Dry Run (只生成文件，检查目录结构)
python main.py --mode relax --stage 1

# 2. 确认无误后，正式提交到 Slurm 集群
python main.py --mode relax --stage 1 --submit
```

#### 2. 收集与清洗数据 (Stage 2)
等待集群任务计算完成后，一键提取并清洗数据：

```bash
python main.py --mode relax --stage 2
```
> 程序会自动剔除原子重叠和能量离群的帧，结果保存至 `data/training/set_relax_时间戳`。

#### 3. 数据集可视化 (Stage 3)
检查数据集是否覆盖了足够的相空间：

```bash
python main.py --mode relax --stage 3
```
> 程序将生成 SOAP-PCA 分布图，保存在 `data/analysis/report_relax/` 下。

---

## ⚙️ 配置说明 (`config.py`)

所有关键参数均可在 `config.py` 中调整，无需修改源码。

| 参数类别 | 变量名 | 说明 |
| :--- | :--- | :--- |
| **微扰设置** | `PERTURB_CONFIG` | 控制晶胞形变比例 (`cell_pert_fraction`) 和原子位移距离 (`atom_pert_distance`) |
| **质量控制** | `QC_SIGMA_E` | 能量离群值阈值 (Z-score)，建议 3.0 ~ 5.0 |
| **质量控制** | `QC_MAX_FORCE` | 最大受力容忍值 (eV/Å)，防止发散数据进入训练集 |
| **可视化** | `VIS_CONFIG` | SOAP 描述符参数 (rcut, nmax, lmax) |
| **任务规模** | `NUM_TASKS` | 每次生成的微扰结构数量 |

---
