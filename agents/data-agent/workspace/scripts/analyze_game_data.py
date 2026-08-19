import pandas as pd
import numpy as np
from datetime import datetime

# 读取 Excel 文件
file_path = r"D:\Users\Downloads\qst_首页分日分模块分内容曝光点击统计_2026-08-14T09_55_55.202723848+08_00.xlsx"
df = pd.read_excel(file_path)

# 列名映射（解决中文编码问题）
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

# 转换日期列
df['date'] = pd.to_datetime(df['date'])

print("=" * 80)
print("QST 首页数据分析师 - 深度数据分析报告")
print("=" * 80)
print(f"数据范围：{df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
print(f"总行数：{len(df)}")
print()

# ===================== 1. 基础对比（8.3-8.6 vs 8.10-8.13）=====================
print("=" * 80)
print("1. 基础对比：两个 4 天区间总量环比")
print("=" * 80)

period1_start = pd.Timestamp('2026-08-03')
period1_end = pd.Timestamp('2026-08-06')
period2_start = pd.Timestamp('2026-08-10')
period2_end = pd.Timestamp('2026-08-13')

p1_data = df[(df['date'] >= period1_start) & (df['date'] <= period1_end)]
p2_data = df[(df['date'] >= period2_start) & (df['date'] <= period2_end)]

def calc_period_stats(data):
    return {
        'days': len(data['date'].unique()),
        'impression_total': data['impression_total'].sum(),
        'impression_uv': data['impression_uv'].sum(),
        'click_total': data['click_total'].sum(),
        'click_uv': data['click_uv'].sum(),
        'ctr': (data['click_total'].sum() / data['impression_total'].sum()) if data['impression_total'].sum() > 0 else 0
    }

stats1 = calc_period_stats(p1_data)
stats2 = calc_period_stats(p2_data)

print(f"\n【8.3-8.6 (4 天)】vs【8.10-8.13 (4 天)】")
print("-" * 80)
print(f"{'指标':<20} {'8.3-8.6':<15} {'8.10-8.13':<15} {'环比变化':<20}")
print("-" * 80)
print(f"{'曝光总量':<20} {stats1['impression_total']:>15,} {stats2['impression_total']:>15,} {((stats2['impression_total']/stats1['impression_total']-1)*100):>+8.1f}%")
print(f"{'点击总量':<20} {stats1['click_total']:>15,} {stats2['click_total']:>15,} {((stats2['click_total']/stats1['click_total']-1)*100):>+8.1f}%")
print(f"{'CTR(点击率)':<20} {stats1['ctr']*100:>14.2f}% {stats2['ctr']*100:>14.2f}% {((stats2['ctr']/stats1['ctr']-1)*100):>+8.1f}%")
print("-" * 80)
print(f"日均曝光：{stats1['impression_total']/stats1['days']:>12,} → {stats2['impression_total']/stats2['days']:>12,} ({((stats2['impression_total']/stats2['days'])/(stats1['impression_total']/stats1['days'])-1)*100:+.1f}%)")
print(f"日均点击：{stats1['click_total']/stats1['days']:>12,} → {stats2['click_total']/stats2['days']:>12,} ({((stats2['click_total']/stats2['days'])/(stats1['click_total']/stats1['days'])-1)*100:+.1f}%)")
print()

# ===================== 2. 分模块拆解 =====================
print("=" * 80)
print("2. 分模块拆解：曝光/点击/CTR 排名")
print("=" * 80)

# 聚合所有模块的总量
module_stats = df.groupby('position').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
    'ctr': 'mean'
}).reset_index()

module_stats['ctr_weighted'] = module_stats['click_total'] / module_stats['impression_total']
module_stats = module_stats.sort_values('impression_total', ascending=False)

print("\n【按曝光量排序 - 全时段】")
print("-" * 100)
print(f"{'模块':<25} {'曝光总量':>12} {'占比':>8} {'点击总量':>12} {'CTR':>10}")
print("-" * 100)
total_imp = module_stats['impression_total'].sum()
for _, row in module_stats.iterrows():
    print(f"{row['position']:<25} {row['impression_total']:>12,} {row['impression_total']/total_imp*100:>7.1f}% {row['click_total']:>12,} {row['ctr_weighted']*100:>9.2f}%")
print("-" * 100)
print()

# 分时间段对比模块表现
print("\n【模块间对比：8.3-8.6 vs 8.10-8.13】")
print("-" * 100)
print(f"{'模块':<25} {'P1 曝光':>12} {'P2 曝光':>12} {'环比':>10} {'P1 CTR':>10} {'P2 CTR':>10} {'CTR 变化':>10}")
print("-" * 100)

for pos in module_stats['position']:
    p1_mod = p1_data[p1_data['position'] == pos]
    p2_mod = p2_data[p2_data['position'] == pos]
    
    imp1 = p1_mod['impression_total'].sum() if len(p1_mod) > 0 else 0
    imp2 = p2_mod['impression_total'].sum() if len(p2_mod) > 0 else 0
    
    # CTR 直接计算 (点击 / 曝光)
    ctr1 = (p1_mod['click_total'].sum() / imp1) if imp1 > 0 else 0
    ctr2 = (p2_mod['click_total'].sum() / imp2) if imp2 > 0 else 0
    
    imp_change = ((imp2/imp1 - 1)*100) if imp1 > 0 else 0
    
    print(f"{pos:<25} {imp1:>12,} {imp2:>12,} {imp_change:>9.1f}% {ctr1*100:>9.2f}% {ctr2*100:>9.2f}% {((ctr2/ctr1 - 1)*100 if ctr1 > 0 else 0):>9.1f}%")
print("-" * 100)
print()

# ===================== 3. 分游戏表拆解 =====================
print("=" * 80)
print("3. 分内容/游戏表拆解：Top 与 Bottom 分析")
print("=" * 80)

# 筛选出有 target_name 的记录（有效游戏内容）
game_data = df[df['target_name'].notna()].copy()

print("\n【按 CTR 排序 - Top 10 & Bottom 10】(全时段)")
print("-" * 100)
game_ctr = game_data.groupby('target_name').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
game_ctr['ctr'] = game_ctr['click_total'] / game_ctr['impression_total']
game_ctr = game_ctr.sort_values('ctr', ascending=False)

print("\nTop 10 CTR:")
print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
for i, (_, row) in enumerate(game_ctr.head(10).iterrows()):
    marker = "*" if i < 3 else ""
    print(f"{marker} {row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['ctr']*100:>9.2f}%")

print("\nBottom 10 CTR:")
print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
for i, (_, row) in enumerate(game_ctr.tail(10).iloc[::-1].iterrows()):
    marker = "!" if i < 3 else ""
    print(f"{marker} {row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['ctr']*100:>9.2f}%")
print()

print("\n【按点击绝对量排序 - Top 10 & Bottom 10】(全时段)")
print("-" * 100)
game_click = game_data.groupby('target_name').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
game_click = game_click.sort_values('click_total', ascending=False)

print("\nTop 10 点击量:")
print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
for i, (_, row) in enumerate(game_click.head(10).iterrows()):
    marker = "*" if i < 3 else ""
    print(f"{marker} {row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['click_total']/row['impression_total']*100:>9.2f}%")

print("\nBottom 10 点击量:")
print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
for i, (_, row) in enumerate(game_click.tail(10).iloc[::-1].iterrows()):
    marker = "!" if i < 3 else ""
    print(f"{marker} {row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['click_total']/row['impression_total']*100:>9.2f}%")
print()

# ===================== 4. 趋势 vs 断点分析 =====================
print("=" * 80)
print("4. 趋势 vs 断点：逐日变化分析")
print("=" * 80)

# 按日期聚合
daily_stats = df.groupby('date').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
daily_stats['ctr'] = daily_stats['click_total'] / daily_stats['impression_total']

print("\n【逐日趋势图】")
print(f"{'日期':<12} {'曝光':>12} {'点击':>12} {'CTR':>10} {'环比 CTR'}")
print("-" * 60)

prev_ctr = None
for _, row in daily_stats.iterrows():
    ctr_change = f"{((row['ctr']/prev_ctr - 1)*100 if prev_ctr else 0):>+7.1f}%" if prev_ctr else "---"
    print(f"{row['date'].strftime('%m-%d'):<12} {row['impression_total']:>12,} {row['click_total']:>12,} {row['ctr']*100:>9.2f}% {ctr_change:>10}")
    prev_ctr = row['ctr']
print()

# 检测突变点
print("\n【突变点检测】(单日 CTR 变化>5% 视为突变)")
print("-" * 60)
for i in range(1, len(daily_stats)):
    prev_row = daily_stats.iloc[i-1]
    curr_row = daily_stats.iloc[i]
    change = (curr_row['ctr'] / prev_row['ctr'] - 1) * 100
    
    if abs(change) > 5:
        direction = "+" if change > 0 else "-"
        print(f"!!! {curr_row['date'].strftime('%m-%d')}: CTR {curr_row['ctr']*100:.2f}% ({direction}{change:.1f}%)")
print()

# ===================== 5. 结构性问题诊断 =====================
print("=" * 80)
print("5. 结构性问题分析")
print("=" * 80)

print("\n【场景诊断矩阵】")
print("-" * 80)

# 计算各模块在两个时期的变化
structural_issues = []
for pos in module_stats['position']:
    p1_mod = p1_data[p1_data['position'] == pos]
    p2_mod = p2_data[p2_data['position'] == pos]
    
    imp1 = p1_mod['impression_total'].sum() if len(p1_mod) > 0 else 0
    imp2 = p2_mod['impression_total'].sum() if len(p2_mod) > 0 else 0
    
    # CTR 直接计算
    ctr1 = (p1_mod['click_total'].sum() / imp1) if imp1 > 0 else 0
    ctr2 = (p2_mod['click_total'].sum() / imp2) if imp2 > 0 else 0
    
    imp_change_pct = ((imp2/imp1 - 1)*100) if imp1 > 0 else 0
    ctr_change_pct = ((ctr2/ctr1 - 1)*100) if ctr1 > 0 else 0
    
    # 诊断类型
    if abs(imp_change_pct) < 10 and abs(ctr_change_pct) < 5:
        diagnosis = "[稳] 稳定型"
    elif imp_change_pct < -10 and ctr_change_pct > 5:
        diagnosis = "[精] 精准度提升但流量萎缩"
    elif imp_change_pct > 10 and ctr_change_pct < -5:
        diagnosis = "[量] 堆量导致吸引力下降"
    elif imp_change_pct < -20 and ctr_change_pct < -10:
        diagnosis = "[警] 双降预警"
    elif imp_change_pct > 20 and ctr_change_pct > 10:
        diagnosis = "[增] 双重增长"
    else:
        diagnosis = "[观] 需关注"
    
    structural_issues.append({
        '模块': pos,
        '曝光变化': imp_change_pct,
        'CTR 变化': ctr_change_pct,
        '诊断': diagnosis
    })

struct_df = pd.DataFrame(structural_issues)
print(struct_df.to_string(index=False))
print()

# ===================== 6. 关键发现总结 =====================
print("=" * 80)
print("关键发现与建议")
print("=" * 80)

# 计算整体趋势
overall_imp_change = (stats2['impression_total'] - stats1['impression_total']) / stats1['impression_total'] * 100
overall_ctr_change = (stats2['ctr'] - stats1['ctr']) / stats1['ctr'] * 100

print(f"\n1. 【整体态势】")
print(f"   - 曝光总量环比变化：{overall_imp_change:+.1f}% ({'增长' if overall_imp_change > 0 else '下滑'})")
print(f"   - CTR 环比变化：{overall_ctr_change:+.1f}% ({'提升' if overall_ctr_change > 0 else '下降'})")

print(f"\n2. 【最佳表现模块】(按曝光占比 + CTR 综合)")
top_module = module_stats.loc[module_stats['ctr_weighted'].idxmax()]
print(f"   - {top_module['position']}: CTR {top_module['ctr_weighted']*100:.2f}%, 曝光占比{top_module['impression_total']/total_imp*100:.1f}%")

print(f"\n3. 【最优质效游戏】(高 CTR 且有一定曝光)")
high_perf_games = game_ctr[(game_ctr['impression_total'] > 10000) & (game_ctr['ctr'] > 0.08)].sort_values('ctr', ascending=False)
if len(high_perf_games) > 0:
    for _, row in high_perf_games.head(5).iterrows():
        print(f"   - {row['target_name']}: CTR {row['ctr']*100:.2f}%, 曝光{row['impression_total']:,}, 点击{row['click_total']:,}")
else:
    print("   - 无明显高质效游戏（建议检查样本量或内容质量）")

print(f"\n4. 【待优化游戏】(低 CTR + 低曝光 或 低 CTR + 高曝光)")
low_perf_games = game_ctr[(game_ctr['ctr'] < 0.05)].sort_values('ctr')
if len(low_perf_games) > 0:
    for _, row in low_perf_games.head(3).iterrows():
        status = "低曝光需谨慎推广" if row['impression_total'] < 5000 else "高曝光需立即优化"
        print(f"   - {row['target_name']}: CTR {row['ctr']*100:.2f}%, {status}")

print(f"\n5. 【建议下一步动作】")
print(f"   - 深入分析 Top 游戏的内容特征，建立可复制的成功模式")
print(f"   - 排查 Bottom 游戏的下架/优化必要性（CTR<5% 且持续低迷者）")
print(f"   - 检查是否有版本更新、活动上线等外部因素影响（8.7-8.9 期间）")
print(f"   - 建立分模块监控看板，持续追踪结构性变化")

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
