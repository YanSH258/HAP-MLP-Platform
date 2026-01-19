# HAP_MLP_Project/modules/extractor.py
import os
import glob
import dpdata

class ResultExtractor:
    def __init__(self, workspace_root):
        """
        :param workspace_root: 包含 task_xxxx 文件夹的根目录
        """
        self.workspace_root = workspace_root

    def collect_data(self):
        """
        遍历目录，读取 output.log，合并为一个 LabeledSystem
        """
        # 1. 找到所有 output.log
        search_pattern = os.path.join(self.workspace_root, "task_*", "output.log")
        # 按 task 编号排序，保证数据顺序整齐
        files = sorted(glob.glob(search_pattern))
        
        print(f"[Extractor] 在 {self.workspace_root} 中找到 {len(files)} 个输出文件。")
        
        valid_systems = []
        
        # 2. 逐个读取
        for f in files:
            try:
                # 尝试用 siesta/output 格式读取 (兼容 HONPAS)
                ls = dpdata.LabeledSystem(f, fmt='siesta/output')
                
                # 检查是否包含数据 (防止空文件或计算失败的文件)
                if len(ls) > 0:
                    valid_systems.append(ls)
                    # print(f"  [OK] 解析成功: {f}") # 太多可以注释掉
                else:
                    print(f"  [Warn] 文件为空或无帧数据: {f}")
                    
            except Exception as e:
                # 如果某个任务算挂了，不要中断程序，打印错误并跳过
                print(f"  [Error] 解析失败 {f}: {e}")

        if not valid_systems:
            print("[Extractor] 没有收集到任何有效数据！")
            return None

        # 3. 合并数据
        print(f"[Extractor] 正在合并 {len(valid_systems)} 个系统的结果...")
        
        # 以第一个系统为基础
        merged_system = valid_systems[0]
        
        # 把剩下的追加进去
        for s in valid_systems[1:]:
            try:
                merged_system.append(s)
            except Exception as e:
                print(f"  [Error] 合并时出错 (可能是原子数量/类型不一致): {e}")

        print(f"[Extractor] 合并完成！总帧数: {len(merged_system)}")
        return merged_system