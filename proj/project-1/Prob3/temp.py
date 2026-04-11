import pandas as pd
import re

def parse_benchmark_to_typst(file_path):
    data = []
    
    # 1. 读取并解析文本日志
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split('=== 同类型地图多次随机采样平均表现 ===')[1:]
    
    for block in blocks:
        header_match = re.search(r'地图:\s*(\S+)\s*\|\s*尺寸:\s*(\d+x\d+)', block)
        if not header_match:
            continue
        
        # 格式化名称，例如处理 <lambda> 和下划线
        map_type = header_match.group(1).replace('<lambda>', 'Random').replace('_', ' ')
        map_size = header_match.group(2).replace('x', ' × ')
        
        lines = block.strip().split('\n')
        data_lines = [line for line in lines if '|' in line and 'Algorithm' not in line and '---' not in line]
        
        for line in data_lines:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                data.append({
                    'Size': map_size,
                    'Map Type': map_type.title(), # 首字母大写
                    'Algorithm': parts[0].replace('*', '\\*'), # 转义 Typst 中的星号
                    'Path Len': parts[1],
                    'Explored': parts[2],
                    'Time (ms)': parts[3]
                })

    df = pd.DataFrame(data)
    
    # 2. 生成 Typst 代码
    typst_str = ""
    
    for i, (size, size_group) in enumerate(df.groupby('Size', sort=False)):
        if i > 0:
            typst_str += "    table.hline(stroke: 0.5pt),\n"
            
        total_rows = len(size_group)
        typst_str += f"    table.cell(rowspan: {total_rows})[*{size}*],\n"
        
        for map_type, map_group in size_group.groupby('Map Type', sort=False):
            map_rows = len(map_group)
            typst_str += f"      table.cell(rowspan: {map_rows})[{map_type}],\n"
            
            for _, row in map_group.iterrows():
                # 加粗 JPS 以作凸显，你可以根据需要调整
                if "JPS" in row['Algorithm']:
                    typst_str += f"        [*{row['Algorithm']}*], [*{row['Path Len']}*], [*{row['Explored']}*], [*{row['Time (ms)']}*],\n"
                else:
                    typst_str += f"        [{row['Algorithm']}], [{row['Path Len']}], [{row['Explored']}], [{row['Time (ms)']}],\n"

    # 3. 保存文件
    with open('typst_table_body.txt', 'w', encoding='utf-8') as f:
        f.write(typst_str)
    print("Typst 数据块已成功导出至 typst_table_body.txt")

# 运行脚本
parse_benchmark_to_typst('log.txt')