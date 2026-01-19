import dpdata
import os
import numpy as np
from modules.validator import StructureValidator  # 导入新模块

class StructureSampler:
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"[Error] 找不到文件: {file_path}")
        # 强制指定 fmt='vasp/poscar'
        self.base_system = dpdata.System(file_path, fmt='vasp/poscar')

    def generate_perturbations(self, num_perturbed=5, pert_config=None):
        """
        生成微扰结构 (带物理预筛选)
        """
        if pert_config is None:
            pert_config = {"cell_pert_fraction": 0.03, "atom_pert_distance": 0.1, "atom_pert_style": "normal"}
        
        print(f"[Sampler] 目标: 生成 {num_perturbed} 个合格的微扰结构...")
        
        valid_systems = []
        # 始终把原始结构作为第一个 (如果需要的话)
        # valid_systems.append(self.base_system) 
        
        attempts = 0
        max_attempts = num_perturbed * 10  # 防止死循环
        
        while len(valid_systems) < num_perturbed and attempts < max_attempts:
            attempts += 1
            
            # 生成 1 个微扰结构 (tmp_sys 此时只包含这 1 帧)
            tmp_sys = self.base_system.perturb(pert_num=1, **pert_config)
            
            # --- 修改点 1: 索引从 [1] 改为 [0] ---
            # 因为 tmp_sys 只有一帧，就是刚才生成的那个微扰结构
            ase_atoms = tmp_sys.to_ase_structure()[0] 
            
            # 调用验证器
            is_valid, msg = StructureValidator.check_overlap(ase_atoms, threshold_factor=0.5)
            
            if is_valid:
                # --- 修改点 2: 直接添加 tmp_sys 或取 [0] ---
                # 既然 tmp_sys 就是我们要的那一帧，直接 append 即可
                valid_systems.append(tmp_sys)
                
                # 或者如果你想保持严谨的切片写法，也可以写:
                # valid_systems.append(tmp_sys.sub_system([0]))
            else:
                # print(f"  [Reject] Attempt {attempts}: {msg}")
                pass
                
        if len(valid_systems) < num_perturbed:
            print(f"⚠️ 警告: 尝试了 {max_attempts} 次，只生成了 {len(valid_systems)} 个合格结构。可能微扰幅度太大。")
            
        print(f"[Sampler] 成功生成 {len(valid_systems)} 个结构 (尝试次数: {attempts})")
        
        # 将列表合并为一个 dpdata.System 返回
        final_system = valid_systems[0]
        for s in valid_systems[1:]:
            final_system.append(s)
            
        return final_system