import pandas as pd
import numpy as np
from datetime import datetime

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
print("深度补充分析 - 第二份报告")
print("=" * 80)

# ===================== 维度 1: Top 游戏时间序列 =====================
print("\n" + "=" * 80)
print("维度 1: Top 游戏的逐日趋势（持续性 vs 偶然性）")
print("=" * 80)

top_games = ['仙侠世界 2', '热血传说', '狂暴战神', '封神榜传奇', '王者传说 2']
game_trend_data = df[df['target_name'].isin(top_games)].copy()

for game in top_games:
    if len(game_trend_data[game_trend_data['target_name'] == game]) > 0:
        game_data = game_trend_data[game_trend_data['target_name'] == game]
        daily_game = game_data.groupby('date').agg({
            'impression_total': 'sum',
            'click_total': 'sum'
        }).reset_index()
        daily_game['ctr'] = daily_game['click_total'] / daily_game['impression_total']
        
        print(f"\n[{game}] 逐日表现")
        print("-" * 60)
        print(f"{'日期':<10} {'曝光':>12} {'点击':>12} {'CTR':>10}")
        for _, row in daily_game.iterrows():
            print(f"{row['date'].strftime('%m-%d'):<10} {row['impression_total']:>12,} {row['click_total']:>12,} {row['ctr']*100:>9.2f}%")
        
        total_imp = daily_game['impression_total'].sum()
        total_click = daily_game['click_total'].sum()
        overall_ctr = total_click / total_imp if total_imp > 0 else 0
        print(f"\n总计：曝光{total_imp:,}, 点击{total_click:,}, CTR={overall_ctr*100:.2f}%")

# ===================== 维度 2: 模块 x 游戏交叉矩阵 =====================
print("\n" + "=" * 80)
print("维度 2: 模块 x 游戏交叉矩阵（哪个模块捧红了哪些游戏）")
print("=" * 80)

module_game_matrix = df[df['target_name'].notna()].groupby(['position', 'target_name']).agg({
    'impression_total': 'sum',
    'click_total': 'sum'
}).reset_index()
module_game_matrix['ctr'] = module_game_matrix['click_total'] / module_game_matrix['impression_total']

print("\n各模块中 Top 游戏分布 (CTR>3% 且曝光>5000)")
print("-" * 100)

for pos in module_game_matrix['position'].unique():
    pos_games = module_game_matrix[module_game_matrix['position'] == pos]
    strong_games = pos_games[(pos_games['ctr'] > 0.03) & (pos_games['impression_total'] > 5000)]
    
    print(f"\n【{pos}】强势游戏:")
    print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
    for _, row in strong_games.sort_values('ctr', ascending=False).iterrows():
        print(f"{row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['ctr']*100:>9.2f}%")
    if len(strong_games) == 0:
        print("   （无符合条件的游戏）")

# ===================== 维度 3: CTR 突变日归因 =====================
print("\n" + "=" * 80)
print("维度 3: CTR 突变日归因（08-06 vs 08-11 对比基准日 08-04）")
print("=" * 80)

anomaly_dates = [pd.Timestamp('2026-08-06'), pd.Timestamp('2026-08-11')]
normal_date = pd.Timestamp('2026-08-04')

for anomaly_day in anomaly_dates:
    day_data = df[df['date'] == anomaly_day]
    normal_data = df[df['date'] == normal_date]
    
    print(f"\n>>> [{anomaly_day.strftime('%Y-%m-%d')}] vs [{normal_date.strftime('%Y-%m-%d')}]")
    print("-" * 100)
    
    day_module = day_data.groupby('position').agg({'impression_total': 'sum'}).reset_index()
    norm_module = normal_data.groupby('position').agg({'impression_total': 'sum'}).reset_index()
    
    print("各模块曝光量变化：")
    for _, row in day_module.iterrows():
        norm_imp = norm_module[norm_module['position'] == row['position']]['impression_total'].values
        if len(norm_imp) > 0:
            norm_val = norm_imp[0]
            curr_val = row['impression_total']
            change_pct = ((curr_val/norm_val) - 1)*100 if norm_val > 0 else 0
            arrow = "+" if change_pct > 0 else ""
            sign = "UP" if abs(change_pct) > 5 else "->"
            print(f"  {row['position']:<25} {curr_val:>10,} -> {norm_val:>10,} ({arrow}{change_pct:+7.1f}%){sign}")

# ===================== 维度 4: UV 效率分析 =====================
print("\n" + "=" * 80)
print("维度 4: UV 转化效率分析（人均曝光/点击价值）")
print("=" * 80)

uv_analysis = df.groupby('position').agg({
    'impression_total': 'sum',
    'impression_uv': 'sum',
    'click_total': 'sum',
    'click_uv': 'sum'
}).reset_index()

uv_analysis['avg_imp_per_user'] = uv_analysis['impression_total'] / uv_analysis['impression_uv']
uv_analysis['avg_click_per_user'] = uv_analysis['click_total'] / uv_analysis['click_uv']
uv_analysis['ctr'] = uv_analysis['click_total'] / uv_analysis['impression_total']

print("\n各模块的用户活跃与转化效率")
print("-" * 100)
print(f"{'模块':<25} {'UV 数':>10} {'人均曝光':>10} {'人均点击':>10} {'CTR':>10}")
print("-" * 100)
for _, row in uv_analysis.iterrows():
    print(f"{row['position']:<25} {row['impression_uv']:>10,} {row['avg_imp_per_user']:>10.1f}次/人 {row['avg_click_per_user']:>10.2f}次/人 {row['ctr']*100:>9.2f}%")

# ===================== 维度 5: 长尾游戏分层 =====================
print("\n" + "=" * 80)
print("维度 5: 长尾游戏效能矩阵（曝光量级 x CTR 水平）")
print("=" * 80)

game_summary = df[df['target_name'].notna()].groupby('target_name').agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
game_summary['ctr'] = game_summary['click_total'] / game_summary['impression_total']

# 创建层级标签
def get_level(imp):
    if imp < 10000:
        return '低曝光 (<1w)'
    elif imp < 50000:
        return '中曝光 (1w-5w)'
    else:
        return '高曝光 (>5w)'

def get_quality(ctr):
    if ctr < 0.02:
        return '差 (CTR<2%)'
    elif ctr < 0.05:
        return '中等 (2%-5%)'
    else:
        return '优秀 (CTR>5%)'

game_summary['level'] = game_summary['impression_total'].apply(get_level)
game_summary['quality'] = game_summary['ctr'].apply(get_quality)

# 关键象限
quadrants = [
    ("【待优化 - 高曝光低效】", game_summary[(game_summary['level'] == '高曝光 (>5w)') & (game_summary['quality'] == '差 (CTR<2%)')].sort_values('impression_total', ascending=False).head(5)),
    ("【明星产品】", game_summary[(game_summary['level'] == '高曝光 (>5w)') & (game_summary['quality'] == '优秀 (CTR>5%)')].sort_values('click_total', ascending=False).head(5)),
    ("【潜力种子】", game_summary[(game_summary['level'] == '低曝光 (<1w)') & (game_summary['quality'] == '优秀 (CTR>5%)')].sort_values('ctr', ascending=False).head(5)),
]

for label, qdf in quadrants:
    print(f"\n{label}:")
    print(f"{'游戏名称':<30} {'曝光':>10} {'点击':>10} {'CTR':>10}")
    if len(qdf) > 0:
        for _, row in qdf.iterrows():
            print(f"{row['target_name']:<30} {row['impression_total']:>10,} {row['click_total']:>10,} {row['ctr']*100:>9.2f}%")
    else:
        print("   （空）")

# ===================== 行动建议汇总 =====================
print("\n" + "=" * 80)
print("综合行动建议")
print("=" * 80)

print("""
[P1 立即执行]
- 下架 CTR=0% 的 10+ 游戏 (剑指沙场、魔神降临等)
- 排查曝光>5w 但 CTR<2% 的游戏资源占用
- 加大仙侠世界 2(CTR=15.38%)、热血传说 (CTR=7.42%) 倾斜
- 排查版本资料全览模块 CTR 下滑 19.2% 原因
- 调研 08-06 单日 CTR 暴跌 16.8% 根因

[P2 一周内完成]
- 建立 Top 游戏素材库 (标题模板、封面风格提炼)
- 对 CTR>5% 但曝光<1w 的潜力种子进行小流量测试
- 复制资讯聚合页成功经验 (曝光+12.7%, CTR+19.5%)
- 构建监控看板 (CTR 波动±5% 告警)

[P3 长期机制]
- 建立内容生命周期管理策略
- A/B 测试常态化 (同一游戏多素材组合)
- 跨模块协同 (Top 游戏集中曝光)
- 以 CTR 为核心的游戏分级与流量分配规则
""")

print("\n分析完毕")
print("=" * 80)
