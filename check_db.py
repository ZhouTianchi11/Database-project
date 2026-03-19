import sqlite3
from config import DB_PATH

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查看 orders 表的结构
cursor.execute("PRAGMA table_info(orders)")
columns = cursor.fetchall()

# 打印所有列
print("✅ Orders 表的所有列：")
for col in columns:
    print(f"列名：{col[1]}, 类型：{col[2]}, 是否非空：{col[3]}")
cursor = conn.cursor()
# 检查是否有 user_id 列
has_user_id = any(col[1] == 'user_id' for col in columns)
print(f"\n📌 是否包含 user_id 列：{'✅ 有' if has_user_id else '❌ 没有'}")

cursor.close()
conn.close()