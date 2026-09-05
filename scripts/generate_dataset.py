import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_retail_data():
    os.makedirs("data", exist_ok=True)
    random.seed(42)  # For deterministic reproducibility

    # 1. STORES
    stores_data = [
        {"store_id": "S101", "store_name": "Downtown Flagship", "location": "Downtown Core", "manager_name": "Alice Smith"},
        {"store_id": "S102", "store_name": "Suburban Mall", "location": "Northside Mall", "manager_name": "Bob Johnson"},
        {"store_id": "S103", "store_name": "Metro Express", "location": "Financial District", "manager_name": "Carol Williams"},
        {"store_id": "S104", "store_name": "Westside Center", "location": "Westside Hub", "manager_name": "David Brown"},
    ]
    df_stores = pd.DataFrame(stores_data)
    df_stores.to_csv("data/stores.csv", index=False)
    print(f"Generated {len(df_stores)} stores.")

    # 2. PRODUCTS
    categories = {
        "Electronics": [
            ("Wireless Mouse", 29.99, 14.00, "Supplier TechA", 3),
            ("Bluetooth Headphones", 89.99, 45.00, "Supplier TechA", 5),
            ("Mechanical Keyboard", 119.99, 65.00, "Supplier TechB", 4),
            ("USB-C Hub", 34.99, 15.00, "Supplier TechB", 3),
            ("Smart Watch", 199.99, 110.00, "Supplier TechA", 7),
            ("Portable Charger", 24.99, 10.00, "Supplier TechC", 4),
            ("Noise Canceling Earbuds", 149.99, 75.00, "Supplier TechA", 5),
            ("HD Webcam", 59.99, 28.00, "Supplier TechB", 3),
            ("Ergonomic Mousepad", 14.99, 4.50, "Supplier TechC", 2),
            ("Dual Monitor Stand", 49.99, 22.00, "Supplier TechC", 6),
            ("4K Monitor", 299.99, 180.00, "Supplier TechA", 7),
            ("LED Desk Lamp", 39.99, 18.00, "Supplier TechC", 4),
        ],
        "Apparel": [
            ("Cotton T-Shirt", 19.99, 7.00, "Supplier ClothsX", 4),
            ("Denim Jeans", 49.99, 20.00, "Supplier ClothsX", 5),
            ("Running Shoes", 79.99, 35.00, "Supplier Sportify", 6),
            ("Wool Hoodie", 59.99, 25.00, "Supplier ClothsX", 5),
            ("Leather Belt", 29.99, 10.00, "Supplier ClothsY", 3),
            ("Athletic Shorts", 24.99, 9.00, "Supplier Sportify", 4),
            ("Formal Shirt", 39.99, 16.00, "Supplier ClothsY", 5),
            ("Winter Coat", 129.99, 55.00, "Supplier ClothsX", 8),
            ("Canvas Sneakers", 44.99, 18.00, "Supplier Sportify", 5),
            ("Casual Socks 3-Pack", 12.99, 4.00, "Supplier ClothsY", 2),
            ("Summer Dress", 49.99, 21.00, "Supplier ClothsX", 4),
            ("Silk Scarf", 24.99, 8.00, "Supplier ClothsY", 3),
        ],
        "Grocery": [
            ("Organic Coffee Beans", 14.99, 6.50, "Supplier FreshG", 2),
            ("Green Tea Pack", 8.99, 3.50, "Supplier FreshG", 2),
            ("Protein Bars 6-Pack", 11.99, 5.00, "Supplier NutriFit", 3),
            ("Almond Milk 1L", 4.49, 1.80, "Supplier FreshG", 2),
            ("Dark Chocolate 85%", 3.99, 1.50, "Supplier SweetCo", 2),
            ("Dried Fruit Mix", 6.99, 2.80, "Supplier FreshG", 3),
            ("Energy Drink 4-Pack", 9.99, 4.20, "Supplier NutriFit", 2),
            ("Sparkling Water 12-Pack", 7.99, 3.00, "Supplier FreshG", 3),
            ("Oatmeal Oats 1kg", 5.49, 2.10, "Supplier FreshG", 2),
            ("Extra Virgin Olive Oil", 12.99, 6.00, "Supplier FreshG", 4),
            ("Whole Grain Bread", 3.99, 1.20, "Supplier BakeryX", 1),
            ("Organic Honey Jar", 9.49, 4.00, "Supplier FreshG", 3),
        ],
        "Home Goods": [
            ("Stainless Travel Mug", 22.99, 9.00, "Supplier HomePlus", 4),
            ("Ceramic Plate Set", 39.99, 16.00, "Supplier HomePlus", 5),
            ("Non-Stick Frying Pan", 34.99, 14.00, "Supplier ChefGear", 4),
            ("Scented Candle", 16.99, 6.00, "Supplier HomePlus", 3),
            ("Microfiber Towel 4-Pack", 18.99, 7.00, "Supplier HomePlus", 3),
            ("Smart Wi-Fi Plug", 15.99, 6.00, "Supplier TechB", 3),
            ("Water Filter Pitcher", 27.99, 11.00, "Supplier HomePlus", 4),
            ("Air Purifier Filter", 29.99, 12.00, "Supplier HomePlus", 5),
            ("Throw Pillow", 19.99, 7.50, "Supplier HomePlus", 3),
            ("Wall Clock", 24.99, 9.50, "Supplier HomePlus", 4),
            ("Storage Bins 3-Pack", 29.99, 12.00, "Supplier HomePlus", 4),
            ("Table Runner", 14.99, 5.00, "Supplier HomePlus", 3),
        ],
        "Beauty & Health": [
            ("Facial Cleanser", 18.99, 7.50, "Supplier BeautyGlow", 3),
            ("Moisturizing Cream", 24.99, 10.00, "Supplier BeautyGlow", 3),
            ("Sunscreen SPF 50", 15.99, 6.00, "Supplier BeautyGlow", 3),
            ("Shampoo & Conditioner", 16.99, 6.50, "Supplier BeautyGlow", 4),
            ("Hand Sanitizer 5-Pack", 9.99, 3.50, "Supplier PharmaCare", 2),
            ("Vitamin C Serum", 29.99, 11.00, "Supplier BeautyGlow", 4),
            ("Electric Toothbrush", 49.99, 21.00, "Supplier PharmaCare", 5),
            ("Lip Balm Set", 8.99, 3.00, "Supplier BeautyGlow", 2),
            ("Herbal Body Soap", 5.99, 2.00, "Supplier BeautyGlow", 2),
            ("Body Lotion 500ml", 14.99, 5.50, "Supplier BeautyGlow", 3),
            ("Ionic Hair Dryer", 59.99, 26.00, "Supplier TechB", 5),
            ("Foot Relief Cream", 11.99, 4.50, "Supplier PharmaCare", 3),
        ]
    }

    products_data = []
    pid_counter = 101
    for cat, item_list in categories.items():
        for name, price, cost, supplier, lead_time in item_list:
            pid = f"P{pid_counter}"
            products_data.append({
                "product_id": pid,
                "product_name": name,
                "category": cat,
                "price": price,
                "cost": cost,
                "supplier": supplier,
                "lead_time_days": lead_time
            })
            pid_counter += 1

    df_products = pd.DataFrame(products_data)
    df_products.to_csv("data/products.csv", index=False)
    print(f"Generated {len(df_products)} products.")

    # 3. SALES & INVENTORY (90 days)
    end_date = datetime(2026, 9, 5)
    start_date = end_date - timedelta(days=89)  # 90 total days
    dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(90)]

    sales_records = []
    inventory_records = []

    # Map of special profiles for deterministic verification
    # (store_id, product_id) -> profile type
    for store in stores_data:
        sid = store["store_id"]
        for prod in products_data:
            pid = prod["product_id"]

            profile = "normal"
            if pid == "P101" and sid == "S101":
                profile = "stockout_risk"  # Wireless Mouse at Downtown Flagship
            elif pid == "P115" and sid == "S102":
                profile = "overstocked"    # Winter Coat at Suburban Mall
            elif pid == "P103" and sid == "S101":
                profile = "spike"          # Mechanical Keyboard at Downtown Flagship
            elif pid == "P125" and sid == "S103":
                profile = "drop"           # Organic Coffee Beans at Metro Express
            elif pid == "P145" and sid == "S104":
                profile = "non_moving"     # Herbal Soap at Westside Center
            elif pid == "P108":
                if sid == "S101":
                    profile = "stockout_risk" # HD Webcam selling fast in S101
                elif sid == "S104":
                    profile = "overstocked"    # HD Webcam sitting in S104

            base_sales = random.randint(2, 6)
            current_stock = random.randint(40, 120)

            for d_idx, d_str in enumerate(dates):
                is_recent_7 = (d_idx >= 83)

                if profile == "stockout_risk":
                    units_sold = random.randint(5, 8)
                    if d_idx >= 85:
                        current_stock = max(12 - (d_idx - 85) * 4, 3)
                    else:
                        current_stock = max(200 - d_idx * 2, 20)

                elif profile == "overstocked":
                    units_sold = random.choice([0, 1]) if d_idx % 2 == 0 else 0
                    current_stock = 350 - (d_idx // 5)

                elif profile == "spike":
                    if is_recent_7:
                        units_sold = random.randint(12, 16)
                    else:
                        units_sold = random.randint(1, 2)
                    current_stock = max(150 - d_idx, 40)

                elif profile == "drop":
                    if is_recent_7:
                        units_sold = random.choice([0, 1])
                    else:
                        units_sold = random.randint(8, 12)
                    current_stock = max(300 - d_idx * 3, 50)

                elif profile == "non_moving":
                    if d_idx >= 50:
                        units_sold = 0
                    else:
                        units_sold = random.randint(0, 1)
                    current_stock = 180

                else:
                    units_sold = random.randint(max(0, base_sales - 2), base_sales + 2)
                    if (d_idx % 14 == 0) and (current_stock < 30):
                        current_stock += 50
                    current_stock = max(current_stock - units_sold, 5)

                revenue = round(units_sold * float(prod["price"]), 2)

                sales_records.append({
                    "date": d_str,
                    "store_id": sid,
                    "product_id": pid,
                    "units_sold": units_sold,
                    "revenue": revenue
                })

                inventory_records.append({
                    "date": d_str,
                    "store_id": sid,
                    "product_id": pid,
                    "stock_quantity": current_stock
                })

    df_sales = pd.DataFrame(sales_records)
    df_sales.to_csv("data/sales.csv", index=False)
    print(f"Generated {len(df_sales)} daily sales records.")

    df_inventory = pd.DataFrame(inventory_records)
    df_inventory.to_csv("data/inventory.csv", index=False)
    print(f"Generated {len(df_inventory)} daily inventory records.")

if __name__ == "__main__":
    generate_retail_data()
