import pandas as pd

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

# 筛选 P2 数据 (8.10-8.13)
p2_data = df[(df['date'] >= pd.Timestamp('2026-08-10')) & (df['date'] <= pd.Timestamp('2026-08-13'))].copy()

print("=" * 100)
print("P2 期 (8.10-8.13) 各模块表现 Top 5 游戏排行榜")
print("=" * 100)

# 过滤有效数据（曝光>=100）
valid_p2 = p2_data[p2_data['impression_total'] >= 100][['position', 'target_name', 'impression_total', 'click_total', 'ctr']].copy()

# 汇总每个游戏的总量
game_summary = valid_p2.groupby(['position', 'target_name']).agg({
    'impression_total': 'sum',
    'click_total': 'sum',
}).reset_index()
game_summary['ctr'] = game_summary['click_total'] / game_summary['impression_total']

# 为每个模块排序并取 Top 5
top5_list = []

for pos in game_summary['position'].unique():
    pos_games = game_summary[game_summary['position'] == pos]
    
    # 按 CTR 排序，取前 5 名
    top5 = pos_games.sort_values('ctr', ascending=False).head(5)[['target_name', 'impression_total', 'click_total', 'ctr']]
    
    top5_list.append({
        'module': pos,
        'data': top5
    })

# 打印结果
for item in top5_list:
    print("\n" + "=" * 100)
    print(f"MODULE: {item['module']}")
    print("=" * 100)
    print(f"{'Rank':>4} | {'Game Name':<25} | {'Impression':>12} | {'Clicks':>10} | {'CTR(%)':>10}")
    print("-" * 100)
    
    for idx, row in item['data'].iterrows():
        rank_num = list(item['data'].sort_values('ctr', ascending=False).index).index(idx) + 1
        print(f"{rank_num:>4} | {row['target_name']:<25} | {row['impression_total']:>12,} | {row['click_total']:>10,} | {row['ctr']*100:>9.2f}%")

# 生成导出文件
output_file = r"D:\Users\Administrator\p2_top5_games.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    sheet_num = 1
    for item in top5_list:
        pos_games = game_summary[game_summary['position'] == item['module']]
        top5 = pos_games.sort_values('ctr', ascending=False).head(5).copy()
        top5.columns = ['Game_Name', 'Total_Impression', 'Total_Clicks', 'CTR']
        top5.index = range(1, len(top5)+1)
        top5.to_excel(writer, sheet_name=f'Sheet{sheet_num}_{item["module"][:8]}', index=True)
        sheet_num += 1

print(f"\n\nExcel DATA TABLE SAVED AT:")
print(f"   D:\\Users\\Administrator\\p2_top5_games.xlsx")
print(f"\nTotal {len(top5_list)} MODULES with TOP 5 GAMES each!")
