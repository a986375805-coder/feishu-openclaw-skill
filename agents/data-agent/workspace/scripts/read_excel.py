import pandas as pd

# 读取 Excel 文件
file_path = r"D:\Users\Downloads\qst_首页分日分模块分内容曝光点击统计_2026-08-14T09_55_55.202723848+08_00.xlsx"
df = pd.read_excel(file_path)

# 打印所有列名
print("=== 完整列名 ===")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n=== 日期分布 ===")
date_col = df.columns[0]
print(f"日期列名：{date_col}")
print(df[date_col].value_counts().sort_index())

print("\n=== 模块分布 ===")
module_col = df.columns[1]
print(df[module_col].value_counts())
