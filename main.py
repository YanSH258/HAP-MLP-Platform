import argparse

from modules.workflows import run_stage_1_generate, run_stage_2_collect, run_stage_3_analysis, run_stage_4_merge, run_stage_5_train

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HONPAS-MLP Automation Platform ")

    parser.add_argument("--mode", type=str, default="scf", 
                        choices=["scf", "relax", "aimd"], 
                        help="计算模式 (scf/relax/aimd)")
    
    parser.add_argument("--stage", type=int, default=1, 
                        choices=[1, 2, 3, 4, 5], 
                        help="阶段: 1=生成提交, 2=收集清洗, 3=分析绘图, 4=合并数据, 5=训练准备")
    
    parser.add_argument("--submit", action="store_true", 
                        help="[仅Stage 1] 是否真实提交作业")
    
    parser.add_argument("--path", type=str, default=None, 
                        help="传入待分析数据 (Stage 3)")
    
    parser.add_argument("--model_type", type=str, default="deepmd",
                        choices=["deepmd", "gpumd"],
                        help="[Stage 5] 训练模型类型")
    
    parser.add_argument("--data_path", type=str, default=None,
                        help="[Stage 3/5] 指定特定数据集路径 (默认自动搜索)")

    parser.add_argument("--val_ratio", type=float, default=0.2,
                        help="[Stage 5] 验证集划分比例 (默认 0.2 即 4:1)")

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
        
    elif args.stage == 5:
        from modules.workflows import run_stage_5_train
        run_stage_5_train(
            model_type=args.model_type, 
            data_path=args.data_path,
            val_ratio=args.val_ratio
        )