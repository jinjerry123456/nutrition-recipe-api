# seed.py
import pandas as pd
from app.database import engine, SessionLocal, Base
from app.models import Category, MenuItem

# Create all tables before importing dataset rows.
print("Creating database tables...")
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()

    # Dataset source can be swapped later if you compare multiple nutrition corpora.
    csv_file_path = "dataset/India_Menu.csv"
    print(f"Reading dataset: {csv_file_path}")
    
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Dataset file not found: {csv_file_path}")
        return

    # Normalize missing values so numeric casting is predictable.
    df = df.fillna(0)

    # Seed categories first to preserve clean foreign-key mapping for menu rows.
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

    print(f"Imported {len(category_map)} categories.")

    # Seed menu items once categories exist, skipping duplicates by item name.
    print("Importing menu items...")
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
    print(f"Seeding complete. Added {items_added} menu items.")

if __name__ == "__main__":
    seed_data()