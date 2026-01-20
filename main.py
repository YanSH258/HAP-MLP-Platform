import argparse
# 注意这里导入的是 run_stage_xxx
from modules.workflows import run_stage_1_generate, run_stage_2_collect, run_stage_3_analysis, run_stage_4_merge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HONPAS-MLP Automation Platform ")

    parser.add_argument("--mode", type=str, default="scf", 
                        choices=["scf", "relax", "aimd"], 
                        help="计算模式 (scf/relax/aimd)")
    
    parser.add_argument("--stage", type=int, default=1, 
                        choices=[1, 2, 3, 4], 
                        help="阶段: 1=生成提交, 2=收集清洗, 3=分析绘图, 4=合并数据")
    
    parser.add_argument("--submit", action="store_true", 
                        help="[仅Stage 1] 是否真实提交作业")
    
    parser.add_argument("--path", type=str, default=None, 
                        help="传入待分析数据 (Stage 3)")

    args = parser.parse_args()

    # 逻辑调度
    if args.stage == 1:
        # dry_run=True 如果没加 --submit
        run_stage_1_generate(mode=args.mode, dry_run=not args.submit)
        
    elif args.stage == 2:
        run_stage_2_collect(mode=args.mode)
        
    elif args.stage == 3:
        run_stage_3_analysis(mode=args.mode, custom_path=args.path)

    elif args.stage == 4:
        run_stage_4_merge()