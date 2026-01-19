import os
import numpy as np
import matplotlib.pyplot as plt
import dpdata
from dscribe.descriptors import SOAP
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

class SOAPSpaceAnalyzer:
    def __init__(self, data_path, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        print(f"[Analyzer] 正在加载数据: {data_path}")
        # 直接读取 DeepMD npy 格式
        self.system = dpdata.LabeledSystem(data_path, fmt='deepmd/npy')
        print(f"   -> 成功加载 {len(self.system)} 帧。")

    def compute_and_plot(self, soap_config, species_map):
        if len(self.system) == 0:
            print("❌ 数据集为空，跳过分析。")
            return

        print("[Analyzer] 1. 计算全局 SOAP...")
        ase_frames = self.system.to_ase_structure()
        species_labels = [v['label'] for k, v in species_map.items()]

        # --- 修正点：适配 dscribe 新版参数名 (r_cut, n_max, l_max) ---
        soap = SOAP(
            species=species_labels,
            periodic=True,
            r_cut=soap_config.get("soap_rcut", 6.0),  # rcut -> r_cut
            n_max=soap_config.get("soap_nmax", 8),    # nmax -> n_max
            l_max=soap_config.get("soap_lmax", 6),    # lmax -> l_max
            sigma=soap_config.get("soap_sigma", 0.5),
            average="inner", # 全局平均
            sparse=False
        )

        # n_jobs=-1 使用所有 CPU 核心并行计算
        descriptors = soap.create(ase_frames, n_jobs=-1)
        print(f"   -> 特征矩阵维度: {descriptors.shape}")

        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(descriptors)

        print("[Analyzer] 2. PCA 降维...")
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        evr = pca.explained_variance_ratio_

        print("[Analyzer] 3. 绘图...")
        energies = self.system['energies']
        natoms = self.system.get_natoms()
        # 计算相对能量 (shifted to 0)
        e_relative = (energies / natoms) - np.min(energies / natoms)

        plt.figure(figsize=(10, 8))
        sc = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=e_relative, 
                         cmap='plasma', s=20, alpha=0.8, edgecolor='none')
        cbar = plt.colorbar(sc)
        cbar.set_label('Relative Energy (eV/atom)')
        
        plt.xlabel(f"PC1 ({evr[0]:.2%})")
        plt.ylabel(f"PC2 ({evr[1]:.2%})")
        plt.title("SOAP Descriptor Space (Energy Map)")
        
        save_path = os.path.join(self.output_dir, "soap_pca.png")
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"✅ 图表已保存: {save_path}")