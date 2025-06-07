import os
import subprocess

spectrum_list = ['spectrum100_Copper0.1mm']
thickness_list = range(50, 401, 50)
repeat_count = 1
histories_per_run = 1e10
base_seed = 2342
file_remarks = 'Ba_607_e'
vox_remarks_list= ['Ba_606_2']
m_file_list = ['Ba']

# 模板文件读取
template_path = '/mnt/no2/huzhen/MC-GPU_v1.5_lite_template.in'
print("\n-------------------  data:2025-5-21  -------------------\n")
# 读取模板文件内容
with open(template_path, 'r') as file:
    template_content = file.read()

for spectrum in spectrum_list:
    print(f"\n开始处理能谱：{spectrum}--\n")
    for thickness in thickness_list:
        for vox_remarks in vox_remarks_list:
            for m_file in m_file_list:
                for run in range(1, repeat_count + 1):
                    seed = base_seed + run
        
                    print(f"开始处理厚度：{thickness} mm | 第 {run} 次")
        
                    # 替换模板中的占位符
                    config_content = template_content.format(
                        spectrum=spectrum,
                        thickness=thickness,
                        seed=seed,
                        run=run,
                        histories=histories_per_run*(thickness/200),
                        fileRemarks=file_remarks,
                        vox=vox_remarks,
                        mfile = m_file 
                    )
        
                    # 生成 .in 文件
                    in_filename = f'config_{spectrum}_{thickness}mm_{vox_remarks}_run{run}.in'
                    with open(in_filename, 'w') as file:
                        file.write(config_content)
        
                    # 运行 MCGPU 单GPU
                    command = f'MCGPULite1.5 {in_filename}'
                    print(f'\n正在执行：{command}\n')
                    try:
                        subprocess.run(command, shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f" 模拟失败：{e}")
