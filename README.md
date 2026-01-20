
# HAP-MLP-Platform

**HAP-MLP-Platform** 是一个集成化的机器学习势函数（MLP）训练数据生产与管理平台。它基于 `dpdata` 和 `ASE`，支持从结构采样、输入生成、任务提交、结果清洗到特征分析的全流程自动化。

## 核心特性

*   **智能采样**：支持扩胞（Supercell）与微扰（Perturbation），内置基于原子共价半径的碰撞检测。
*   **多模式支持**：支持单点能（SCF）批量采样与动力学（AIMD）轨迹提取。
*   **高性能清洗**：自动剔除原子重叠、能量离群值及受力异常帧。
*   **高维分析**：集成 SOAP 描述符与 UMAP/t-SNE 算法，可视化训练集的构型空间覆盖率。
*   **数据集管理**：支持多源数据集（SCF + AIMD）的一键合并。

---

## 运行环境

建议使用 `conda` 创建环境：

```bash
conda create -n hap_mlp python=3.9
conda activate hap_mlp
pip install dpdata ase dscribe scikit-learn umap-learn matplotlib
```

---

## 快速上手

项目通过 `main.py` 进行阶段化管理，主要分为四个阶段（Stage）。

### 0. 配置参数
在运行前，修改项目根目录下的 `config.py`：
*   `INPUT_PATH`: 初始结构文件（如 POSCAR）。
*   `SUPERCELL_SIZE`: 扩胞尺寸，如 `[2, 2, 2]`。
*   `NUM_TASKS`: 扰动生成的任务数量。
*   `QC_OVERLAP_THRESHOLD`: 原子重叠阈值（共价半径之和的倍数，建议 0.5）。

### Stage 1: 任务生成与提交
生成微扰结构并提交至超算集群（支持 Slurm）。

```bash
# 生成 SCF 采样任务 (默认 DryRun，仅生成文件不提交)
python main.py --stage 1 --mode scf

# 生成任务并直接提交到 Slurm 队列
python main.py --stage 1 --mode scf --submit

# 同样支持 aimd 模式的初始结构准备
python main.py --stage 1 --mode aimd --submit
```

### Stage 2: 数据收集与清洗
计算完成后，提取 `output.log` 等结果，进行质量控制并转换为 DeepMD 格式。

```bash
# 收集 SCF 单点能数据 (提取每一文件夹的最后一帧)
python main.py --stage 2 --mode scf

# 收集 AIMD 轨迹数据 (从 .ANI/.FA 文件提取完整轨迹)
python main.py --stage 2 --mode aimd
```
清洗后的数据将存放在 `data/training/set_{mode}_{timestamp}`。

### Stage 3: 构型空间可视化分析
利用 SOAP 描述符和 UMAP 算法分析数据集的构型覆盖范围。

```bash
# 分析最新的 SCF 数据集
python main.py --stage 3 --mode scf

# 分析指定的任意数据集路径
python main.py --stage 3 --path data/training/merged_master_20260120
```
图表保存于 `data/analysis/` 目录下。

### Stage 4: 数据集大合并
将多个 batch 的数据（如不同温度的 AIMD 和不同幅度的 SCF）合并为一个最终训练集。

```bash
# 自动搜索 data/training/ 下所有 set_* 文件夹并合并
python main.py --stage 4
```

---

## 目录结构说明

```text
├── config.py                # 核心配置文件
├── main.py                  # 工作流入口
├── data/
│   ├── raw/                 # 原始结构输入
│   ├── training/            # 清洗后的 DeepMD 训练集
│   └── analysis/            # UMAP/PCA 分析报告
├── templates/               # 计算软件输入模板 (HONPAS/SIESTA等)
└── modules/                 # 核心功能模块
```
平台的核心逻辑分布在 modules/ 文件夹中，各模块职责如下：
模块名称	核心职责
sampler.py	结构处理中心：负责扩胞 (Supercell) 和几何微扰 (Perturbation)。
validator.py	预筛选闸门：在提交计算前，拦截原子重叠等不合理的物理构型。
wrapper.py	模板引擎：将结构数据填入计算软件（如 HONPAS）的输入模板中。
scheduler.py	任务管家：管理 Slurm 任务生成、sbatch 提交及作业状态监控。
extractor.py	数据采集：支持 SCF 与 AIMD 模式，自动解析 output 与轨迹文件。
cleaner.py	质量控制 (QC)：基于共价半径检查碰撞，剔除能量与力的离群帧。
analyzer.py	特征提取：计算 SOAP 描述符，并进行 PCA 或非线性降维。
merger.py	数据聚合：无损合并不同 batch 或不同模式（SCF/AIMD）的数据集。
visualizer.py	绘图工具：提供能量/力分布直方图及构型空间散点图。
workflows.py	工作流编排：将上述模块串联成 Stage 1~4 的标准操作流程。
---

## 注意事项

1.  **扩胞逻辑**：在 Stage 1 执行时，程序会检查 `SUPERCELL_SIZE`。若任意维度 > 1，则会自动执行扩胞后再进行扰动。
2.  **AIMD 提取**：使用 `--mode aimd` 时，请确保任务目录下存在轨迹文件（如 `.ANI` 或 `.FA`），否则将无法提取受力信息。
3.  **原子类型顺序**：合并数据集时，`dpdata` 会严格检查原子种类顺序。请确保所有 batch 使用相同的 `SPECIES_MAP` 配置。

---
