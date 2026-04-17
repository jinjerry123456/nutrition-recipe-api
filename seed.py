# seed.py
import pandas as pd
from app.database import engine, SessionLocal, Base
from app.models import Category, MenuItem
import math

# 1. 在数据库中创建所有的表
print("正在创建数据库表...")
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 2. 使用你提供的真实数据集路径
    csv_file_path = "dataset/India_Menu.csv" 
    print(f"正在读取数据集: {csv_file_path}")
    
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"❌ 找不到文件！请确认 {csv_file_path} 这个文件真的存在。")
        return

    # 清理数据：把所有的 NaN (空值) 和非数字替换为 0
    df = df.fillna(0)

    # 3. 提取所有的分类并存入 Category 表
    categories = df['Menu Category'].unique()
    category_map = {} 
    
    for cat_name in categories:
        cat = db.query(Category).filter(Category.name == cat_name).first()
        if not cat:
            cat = Category(name=cat_name)
            db.add(cat)
            db.commit()
            db.refresh(cat)
        category_map[cat_name] = cat.id
    
    print(f"✅ 成功导入 {len(category_map)} 个分类！")

    # 4. 遍历每一行数据，存入 MenuItem 表
    print("正在导入菜品数据，请稍候...")
    items_added = 0
    
    for index, row in df.iterrows():
        cat_id = category_map[row['Menu Category']]
        
        existing_item = db.query(MenuItem).filter(MenuItem.name == row['Menu Items']).first()
        if not existing_item:
            new_item = MenuItem(
                category_id=cat_id,
                name=row['Menu Items'],
                serve_size=str(row['Per Serve Size']),
                energy_kcal=float(row['Energy (kCal)']),
                protein_g=float(row['Protein (g)']),
                total_fat_g=float(row['Total fat (g)']),
                sat_fat_g=float(row['Sat Fat (g)']),
                trans_fat_g=float(row['Trans fat (g)']),
                cholesterol_mg=float(row['Cholesterols (mg)']), 
                total_carbs_g=float(row['Total carbohydrate (g)']), 
                total_sugars_g=float(row['Total Sugars (g)']),
                added_sugars_g=float(row['Added Sugars (g)']),
                sodium_mg=float(row['Sodium (mg)'])
            )
            db.add(new_item)
            items_added += 1

    db.commit()
    db.close()
    print(f"🎉 数据导入完成！成功添加了 {items_added} 个菜品进入数据库。")

if __name__ == "__main__":
    seed_data()