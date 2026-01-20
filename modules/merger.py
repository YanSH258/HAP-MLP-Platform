import os
import glob
import dpdata
import time

class DatasetMerger:
    @staticmethod
    def merge_all(dataset_dirs, output_path):
        """
        dataset_dirs: 一个包含多个数据集路径的列表
        output_path: 合并后的保存路径
        """
        if not dataset_dirs:
            print("❌ 没有提供需要合并的路径。")
            return None

        print(f"[Merger] 准备合并 {len(dataset_dirs)} 个数据集...")
        
        # 1. 加载第一个作为基准
        try:
            # 假设之前保存的都是 deepmd/npy 格式
            final_system = dpdata.LabeledSystem(dataset_dirs[0], fmt='deepmd/npy')
            print(f"   -> [1/{len(dataset_dirs)}] 加载: {dataset_dirs[0]} ({len(final_system)} 帧)")
        except Exception as e:
            print(f"❌ 加载基础数据集失败: {e}")
            return None

        # 2. 循环追加剩下的
        for i, ddir in enumerate(dataset_dirs[1:], 2):
            try:
                next_sys = dpdata.LabeledSystem(ddir, fmt='deepmd/npy')
                final_system.append(next_sys)
                print(f"   -> [{i}/{len(dataset_dirs)}] 合并: {ddir} ({len(next_sys)} 帧)")
            except Exception as e:
                print(f"⚠️ 跳过数据集 {ddir}，原因: {e}")

        # 3. 保存
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        final_system.to('deepmd/npy', output_path)
        final_system.to('deepmd/raw', output_path) # 同时存一份 raw 方便查看
        
        print(f"✅ 合并完成！总帧数: {len(final_system)}")
        print(f"✅ 合并后的数据集已保存至: {output_path}")
        return final_system