import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 读取 Excel 文件
file_path = r"D:\Users\Downloads\qst_首页分日分模块分内容曝光点击统计_2026-08-14T09_55_55.202723848+08_00.xlsx"
df = pd.read_excel(file_path)

# 列名映射
col_mapping = {
    df.columns[0]: 'date',
    df.columns[1]: 'position',
    df.columns[2]: 'target_type',
    df.columns[3]: 'target_name',
    df.columns[4]: 'content_id',
    df.columns[5]: 'impression_total',
    df.columns[6]: 'impression_uv',
    df.columns[7]: 'click_total',
    df.columns[8]: 'click_uv',
    df.columns[9]: 'ctr'
}
df.rename(columns=col_mapping, inplace=True)
df['date'] = pd.to_datetime(df['date'])

print("=" * 80)
print("QST 首页数据 - 可视化分析报表")
print("=" * 80)

# ========================================================
# 图表 1: 模块对比 (P1 vs P2)
# ========================================================
period1_start = pd.Timestamp('2026-08-03')
period1_end = pd.Timestamp('2026-08-06')
period2_start = pd.Timestamp('2026-08-10')
period2_end = pd.Timestamp('2026-08-13')

p1_data = df[(df['date'] >= period1_start) & (df['date'] <= period1_end)]
p2_data = df[(df['date'] >= period2_start) & (df['date'] <= period2_end)]

print("\n【图表 1】模块间对比：8.3-8.6 vs 8.10-8.13")
print("-" * 100)

module_comparison = {}
for pos in p1_data['position'].unique():
    p1_mod = p1_data[p1_data['position'] == pos]
    p2_mod = p2_data[p2_data['position'] == pos]
    
    imp1 = p1_mod['impression_total'].sum()
    imp2 = p2_mod['impression_total'].sum()
    click1 = p1_mod['click_total'].sum()
    click2 = p2_mod['click_total'].sum()
    ctr1 = click1 / imp1 if imp1 > 0 else 0
    ctr2 = click2 / imp2 if imp2 > 0 else 0
    
    imp_change = ((imp2/imp1 - 1)*100) if imp1 > 0 else 0
    click_change = ((click2/click1 - 1)*100) if click1 > 0 else 0
    ctr_change = ((ctr2/ctr1 - 1)*100) if ctr1 > 0 else 0
    
    module_comparison[pos] = {
        '曝光_P1': imp1,
        '曝光_P2': imp2,
        '曝光变化%': imp_change,
        '点击_P1': click1,
        '点击_P2': click2,
        '点击变化%': click_change,
        'CTR_P1': round(ctr1*100, 2),
        'CTR_P2': round(ctr2*100, 2),
        'CTR 变化%': round(ctr_change, 1)
    }

module_df = pd.DataFrame(module_comparison).T
print(module_df.to_string())

# ========================================================
# 图表 2: Top 游戏表现排名（全时段）
# ========================================================
game_data = df[df['target_name'].notna()].copy()
game_summary = game_data.groupby('target_name').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
game_summary['ctr'] = game_summary['click_total'] / game_summary['impression_total']

# 过滤有效数据（曝光>=1000，点击>=5）
valid_games = game_summary[(game_summary['impression_total'] >= 1000) & (game_summary['click_total'] >= 5)].copy()

print("\n【图表 2】Top 游戏表现排名（按 CTR 排序）")
print("-" * 100)
top_ctr = valid_games.sort_values('ctr', ascending=False).head(15)[['target_name', 'impression_total', 'click_total', 'ctr']]
top_ctr.columns = ['游戏名称', '曝光总量', '点击总量', 'CTR(%)']
print(top_ctr.to_string(index=False))

print("\n【图表 3】Top 游戏表现排名（按点击量排序）")
print("-" * 100)
top_click = valid_games.sort_values('click_total', ascending=False).head(15)[['target_name', 'impression_total', 'click_total', 'ctr']]
top_click.columns = ['游戏名称', '曝光总量', '点击总量', 'CTR(%)']
print(top_click.to_string(index=False))

# ========================================================
# 图表 4: 低效游戏识别（曝光>5000 且 CTR<2%）
# ========================================================
low_efficiency = valid_games[
    (valid_games['impression_total'] > 5000) & 
    (valid_games['ctr'] < 0.02)
].sort_values('impression_total', ascending=False).head(15)

print("\n【图表 4】低效游戏识别（需优化下架）")
print("-" * 100)
if len(low_efficiency) > 0:
    print(f"{'游戏名称':<30} {'曝光':>12} {'点击':>10} {'CTR(%)':>10}")
    for _, row in low_efficiency.iterrows():
        print(f"{row['target_name']:<30} {row['impression_total']:>12,} {row['click_total']:>10,} {row['ctr']*100:>9.2f}%")
else:
    print("无符合筛选条件的低效游戏")

# ========================================================
# 生成 Excel 可视化数据表
# ========================================================
output_file = r"D:\Users\Administrator\qst_analysis_visualization.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Sheet 1: 模块对比
    module_df.to_excel(writer, sheet_name='01_模块对比', index=True)
    
    # Sheet 2: Top 游戏 CTR
    top_ctr_sorted = valid_games.sort_values('ctr', ascending=False).head(20).copy()
    top_ctr_sorted.columns = ['target_name', 'impression_total', 'click_total', 'ctr']
    top_ctr_sorted.index.name = 'Rank'
    top_ctr_sorted.to_excel(writer, sheet_name='02_Top_游戏_CTR', index=True)
    
    # Sheet 3: Top 游戏 点击量
    top_click_sorted = valid_games.sort_values('click_total', ascending=False).head(20).copy()
    top_click_sorted.columns = ['target_name', 'impression_total', 'click_total', 'ctr']
    top_click_sorted.index.name = 'Rank'
    top_click_sorted.to_excel(writer, sheet_name='03_Top_游戏_点击量', index=True)
    
    # Sheet 4: 低效游戏
    low_efficiency.to_excel(writer, sheet_name='04_低效游戏_待优化', index=True)
    
    # Sheet 5: 概览摘要
    summary_df = pd.DataFrame([{
        '指标': '总曝光量 (P1)', '值': int(p1_data['impression_total'].sum()),
        '指标': '总曝光量 (P2)', '值': int(p2_data['impression_total'].sum()),
        '指标': '曝光环比变化 (%)', '值': f"{((p2_data['impression_total'].sum()/p1_data['impression_total'].sum()-1)*100):+.1f}%",
        '指标': '总点击量 (P1)', '值': int(p1_data['click_total'].sum()),
        '指标': '总点击量 (P2)', '值': int(p2_data['click_total'].sum()),
        '指标': '点击环比变化 (%)', '值': f"{((p2_data['click_total'].sum()/p1_data['click_total'].sum()-1)*100):+.1f}%",
        '指标': '整体 CTR (P1)', '值': f"{(p1_data['click_total'].sum()/p1_data['impression_total'].sum()*100):.2f}%",
        '指标': '整体 CTR (P2)', '值': f"{(p2_data['click_total'].sum()/p2_data['impression_total'].sum()*100):.2f}%",
        '指标': 'CTR 环比变化 (%)', '值': f"{(((p2_data['click_total'].sum()/p2_data['impression_total'].sum())/(p1_data['click_total'].sum()/p1_data['impression_total'].sum())-1)*100):+.1f}%"
    }])
    summary_df.to_excel(writer, sheet_name='05_概览摘要', index=False)

print("\nDATA TABLE SAVED AT:")
print(f"   D:\\Users\\Administrator\\qst_analysis_visualization.xlsx")

# ========================================================
# ASCII 柱状图
# ========================================================
print("\n\nVISUALIZATION CHART 1: Module Exposure Comparison (P1 vs P2)")
print("=" * 80)

max_imp = module_df[['曝光_P1', '曝光_P2']].max().max()

for i, (pos, row) in enumerate(module_df.items()):
    bar1_width = int(row['曝光_P1'] / max_imp * 50)
    bar2_width = int(row['曝光_P2'] / max_imp * 50)
    
    bar1 = "#" * bar1_width
    bar2 = "*" * bar2_width
    imp_change = row['曝光变化%']
    sign = "+" if imp_change > 0 else ""
    
    print(f"{pos[:15]:<15} |{bar1}| {int(row['曝光_P1']):>10,} |{bar2}| {int(row['曝光_P2']):>10,} ({sign}{imp_change:+6.1f}%)")

print("\nVISUALIZATION CHART 2: Module CTR Change Comparison")
print("=" * 80)
for pos, row in module_df.items():
    change = row['CTR 变化%']
    arrow = "UP" if change > 0 else ("DOWN" if change < 0 else "STABLE")
    status = "[IMPROVED]" if change > 5 else ("[DECLINED]" if change < -5 else "[STABLE]")
    
    print(f"{pos[:15]:<15} CTR: {row['CTR_P1']:.2f}% -> {row['CTR_P2']:.2f}% ({arrow} {change:+7.1f}%) [{status}]")

print("\nFINAL CONCLUSIONS")
print("=" * 80)
best_module = module_df.sort_values('CTR_P2', ascending=False).index[0]
worst_module = module_df.sort_values('CTR_P2', ascending=False).index[-1]
best_game = valid_games.loc[valid_games['ctr'].idxmax(), 'target_name']
best_game_ctr = valid_games.loc[valid_games['ctr'].idxmax(), 'ctr']*100

print(f"""
BEST PERFORMING MODULE: {best_module} (CTR={module_df.loc[best_module, 'CTR_P2']:.2f}%)
WORST PERFORMING MODULE: {worst_module} (CTR={module_df.loc[worst_module, 'CTR_P2']:.2f}%)
BEST GAME: {best_game} (CTR={best_game_ctr:.2f}%)
""")

print("\nVISUAL DATA TABLE GENERATED WITH:")
print("  SHEET 1: Module_Comparison - Exposure/CPC/CTR detailed comparison")
print("  SHEET 2: Top_Games_CTR - Game ranking by CTR")
print("  SHEET 3: Top_Games_Clicks - Game ranking by click volume")
print("  SHEET 4: Low_Efficiency_Games - High exposure low CTR games to optimize")
print("  SHEET 5: Summary_Sheet - Core metrics overview")
print("\nPlease check the file!")
