from sqlalchemy import create_engine, text

def drop_tables():
    engine = create_engine('sqlite:///database/restaurant.db')
    with engine.begin() as conn:
        conn.execute(text('DROP TABLE IF EXISTS menu_items'))
        conn.execute(text('DROP TABLE IF EXISTS categories'))
        conn.execute(text('DROP TABLE IF EXISTS allergens'))
        conn.execute(text('DROP TABLE IF EXISTS menu_item_allergens'))
        conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        print("Tables dropped successfully")

if __name__ == '__main__':
    drop_tables() 