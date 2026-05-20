import csv
import random
from datetime import datetime, timedelta

def generate_firstclub_dataset():
    # 1. Master Catalog Definition
    brands = [
        "Samsung", "boAt", "Noise", "Philips", "Sony", 
        "JBL", "OnePlus", "Realme", "Xiaomi", "Titan",
        "Prestige", "Bajaj", "Havells", "Crompton", "Orient", 
        "Pigeon", "Butterfly", "Amazfit", "Fire-Boltt", "Zebronics"
    ]

    # Category -> Subcategory mapping
    catalog_structure = {
        "Electronics": ["Headphones", "Speakers", "Chargers", "Cables"],
        "Audio": ["TWS", "Neckband", "Soundbar"],
        "Wearables": ["Smartwatch", "Fitness Band"],
        "Kitchen": ["Mixer Grinder", "Induction Cooktop"],
        "Home Appliances": ["Fans"]
    }
    
    # Map subcategories back to categories
    subcat_to_cat = {}
    for cat, subcats in catalog_structure.items():
        for subcat in subcats:
            subcat_to_cat[subcat] = cat

    # Assign brands to categories/subcategories realistically
    brand_specialties = {
        "Samsung": ["TWS", "Smartwatch", "Chargers"],
        "boAt": ["TWS", "Neckband", "Speakers", "Headphones", "Cables"],
        "Noise": ["Smartwatch", "Fitness Band", "TWS"],
        "Philips": ["Mixer Grinder", "Speakers", "Headphones"],
        "Sony": ["Headphones", "Speakers", "Soundbar"],
        "JBL": ["Speakers", "Headphones", "Soundbar", "TWS"],
        "OnePlus": ["TWS", "Neckband", "Smartwatch", "Chargers"],
        "Realme": ["TWS", "Neckband", "Smartwatch", "Chargers"],
        "Xiaomi": ["Smartwatch", "Fitness Band", "Chargers", "Speakers"],
        "Titan": ["Smartwatch"],
        "Prestige": ["Mixer Grinder", "Induction Cooktop"],
        "Bajaj": ["Mixer Grinder", "Fans"],
        "Havells": ["Fans", "Induction Cooktop"],
        "Crompton": ["Fans"],
        "Orient": ["Fans"],
        "Pigeon": ["Mixer Grinder", "Induction Cooktop"],
        "Butterfly": ["Mixer Grinder", "Induction Cooktop"],
        "Amazfit": ["Smartwatch", "Fitness Band"],
        "Fire-Boltt": ["Smartwatch"],
        "Zebronics": ["Speakers", "Soundbar", "Cables", "Headphones"]
    }

    # Price ranges for subcategories in INR
    price_ranges = {
        "Headphones": (1000, 8000),
        "Speakers": (1500, 15000),
        "Chargers": (500, 2500),
        "Cables": (200, 1000),
        "TWS": (800, 6000),
        "Neckband": (600, 3000),
        "Soundbar": (3000, 25000),
        "Smartwatch": (2000, 25000),
        "Fitness Band": (1000, 5000),
        "Mixer Grinder": (1500, 8000),
        "Induction Cooktop": (1800, 6000),
        "Fans": (1500, 9000)
    }

    # Generate 200 unique products (FSNs)
    products = []
    subcategories = list(subcat_to_cat.keys())
    
    random.seed(42)  # For deterministic generation
    
    for i in range(1, 201):
        fsn = f"FSN{i:06d}"
        
        # Pick a subcategory and category
        subcat = random.choice(subcategories)
        cat = subcat_to_cat[subcat]
        
        # Pick a brand that is specialized or any random brand if none
        matching_brands = [b for b, specialties in brand_specialties.items() if subcat in specialties]
        if not matching_brands:
            matching_brands = brands
        brand = random.choice(matching_brands)
        
        # Base Price
        p_min, p_max = price_ranges[subcat]
        base_price = round(random.uniform(p_min, p_max), -1)  # Round to nearest 10
        if base_price == 0:
            base_price = p_min
            
        product_name = f"{brand} {subcat[:-1] if subcat.endswith('s') else subcat} Model {random.randint(100, 999)}"
        
        products.append({
            "FSN": fsn,
            "Product_Name": product_name,
            "Brand": brand,
            "Category": cat,
            "Subcategory": subcat,
            "Base_Price": base_price,
            "Base_Search_Rank": random.randint(1, 200),
            "Base_Conv_Rate": random.uniform(1.5, 8.0)
        })

    # 2. Date Setup
    end_date = datetime(2026, 5, 20)
    start_date = end_date - timedelta(days=179)  # 180 days total
    dates = [start_date + timedelta(days=d) for d in range(180)]

    # 3. Dynamic Factors per Product (e.g. price change schedule, stock status schedule)
    # We will generate a list of days where prices change for each product
    product_schedules = {}
    for p in products:
        # 8-12 price changes
        num_changes = random.randint(8, 12)
        change_days = sorted(random.sample(range(180), num_changes))
        
        # Price multipliers at each change
        price_multipliers = [1.0]
        curr_mult = 1.0
        for _ in range(num_changes):
            # Price hike or cut (-15% to +10%)
            change = random.uniform(-0.15, 0.10)
            curr_mult = max(0.5, min(2.0, curr_mult * (1 + change)))
            price_multipliers.append(curr_mult)
            
        # Out-of-stock periods: 1-3 episodes per product, lasting 3-10 days
        oos_days = set()
        if random.random() < 0.6:  # 60% of products get OOS episodes
            num_episodes = random.randint(1, 3)
            for _ in range(num_episodes):
                ep_start = random.randint(0, 170)
                ep_dur = random.randint(3, 10)
                for d in range(ep_start, min(180, ep_start + ep_dur)):
                    oos_days.add(d)

        product_schedules[p["FSN"]] = {
            "change_days": change_days,
            "price_multipliers": price_multipliers,
            "oos_days": oos_days
        }

    # Global events
    # 5-10 sales SPIKES (sudden +150% to +250% jumps) on random days
    spike_days = random.sample(range(180), random.randint(6, 10))
    # 5-10 sales DROPS (sudden -40% to -70% falls)
    drop_days = random.sample([d for d in range(180) if d not in spike_days], random.randint(6, 10))
    
    # Big Billion Days: 3-day promotional spike around the middle (days 88, 89, 90)
    bbd_days = [88, 89, 90]

    # Let's create the records
    records = []
    
    for day_idx, dt in enumerate(dates):
        is_weekend = dt.weekday() in [5, 6]  # Saturday, Sunday
        is_bbd = day_idx in bbd_days
        is_spike = day_idx in spike_days
        is_drop = day_idx in drop_days
        
        date_str = dt.strftime("%Y-%m-%d")
        
        # Every day, we sample a subset of active products so we don't have too large a dataset,
        # but we need to meet the 2,000 rows minimum.
        # Let's make it so all 200 products are active, giving 200 * 180 = 36,000 rows.
        # This is high quality and lets us test all FSNs perfectly. Let's do that!
        for p in products:
            fsn = p["FSN"]
            sched = product_schedules[fsn]
            
            # Determine current price multiplier
            mult_idx = 0
            for idx, c_day in enumerate(sched["change_days"]):
                if day_idx >= c_day:
                    mult_idx = idx + 1
                else:
                    break
            curr_mult = sched["price_multipliers"][mult_idx]
            sell_price = round(p["Base_Price"] * curr_mult, -1)
            
            # Competitor Price (Comp_Price)
            # Competitor pricing reacts to ours with some lag and random variance
            comp_ratio = random.uniform(0.85, 1.15)
            comp_price = round(sell_price * comp_ratio, -1)
            
            # Stock availability (Instock_Pct)
            if day_idx in sched["oos_days"]:
                # Severe OOS
                instock_pct = round(random.uniform(0, 35), 1)
            else:
                # Normal stock
                instock_pct = round(random.uniform(75, 100), 1)
                
            # Base daily sales units sold for this product
            base_units = random.randint(2, 20)
            if p["Category"] == "Electronics":
                base_units = random.randint(1, 8)  # Electronics are higher value, lower volume
            elif p["Category"] == "Audio":
                base_units = random.randint(5, 30) # High volume
                
            # Modifiers
            units_mult = 1.0
            
            # 1. Weekly Seasonality (weekend sales 30-60% higher)
            if is_weekend:
                units_mult *= random.uniform(1.30, 1.60)
                
            # 2. Out-of-Stock effect
            if instock_pct < 40:
                # OOS drops units dramatically
                units_mult *= (instock_pct / 100.0) * random.uniform(0.1, 0.4)
                
            # 3. Global spikes & drops
            if is_bbd:
                units_mult *= random.uniform(4.0, 6.0)  # Big Billion Days!
            elif is_spike:
                # Sudden spike (+150% to +250% jump)
                units_mult *= random.uniform(2.5, 3.5)
            elif is_drop:
                # Sudden drop (-40% to -70% fall)
                units_mult *= random.uniform(0.3, 0.6)
                
            # Random daily noise
            units_mult *= random.uniform(0.8, 1.2)
            
            units_sold = int(round(base_units * units_mult))
            if instock_pct == 0:
                units_sold = 0
                
            # Calculate Revenue
            revenue = round(units_sold * sell_price, 2)
            
            # Search Rank (dynamic, improves with sales, slips with OOS)
            rank_shift = int((base_units - units_sold) * 2)
            if instock_pct < 40:
                rank_shift += random.randint(10, 30)
            search_rank = max(1, min(200, p["Base_Search_Rank"] + rank_shift + random.randint(-5, 5)))
            
            # Conversion Rate (dynamic)
            conv_modifier = 1.0
            if instock_pct < 50:
                conv_modifier *= 0.5
            if sell_price < comp_price:
                conv_modifier *= 1.2 # Cheaper than competitor improves conversion
            conversion_rate = round(max(0.5, min(25.0, p["Base_Conv_Rate"] * conv_modifier + random.uniform(-1, 1))), 2)
            
            # Repeat Orders
            repeat_pct = random.uniform(0.05, 0.35)
            repeat_orders = int(round(units_sold * repeat_pct))
            if repeat_orders > units_sold:
                repeat_orders = units_sold
                
            # Demand Score
            # composite: search rank (40%), conversion (30%), repeat orders (30%)
            # Search rank is 1-200. (201 - search_rank) / 200 maps 1->1.0 and 200->0.005
            search_part = 40.0 * (201 - search_rank) / 200.0
            conv_part = 30.0 * (conversion_rate / 25.0)
            repeat_part = 30.0 * (repeat_orders / max(1, units_sold))
            demand_score = round(max(0.0, min(100.0, search_part + conv_part + repeat_part)), 1)
            
            records.append({
                "Date": date_str,
                "FSN": fsn,
                "Product_Name": p["Product_Name"],
                "Brand": p["Brand"],
                "Category": p["Category"],
                "Subcategory": p["Subcategory"],
                "Units_Sold": units_sold,
                "Revenue": revenue,
                "Sell_Price": sell_price,
                "Comp_Price": comp_price,
                "Instock_Pct": instock_pct,
                "Demand_Score": demand_score,
                "Search_Rank": search_rank,
                "Conversion_Rate": conversion_rate,
                "Repeat_Orders": repeat_orders
            })

    # Save to CSV
    output_file = "raw_transaction_data.csv"
    headers = [
        "Date", "FSN", "Product_Name", "Brand", "Category", "Subcategory",
        "Units_Sold", "Revenue", "Sell_Price", "Comp_Price", "Instock_Pct",
        "Demand_Score", "Search_Rank", "Conversion_Rate", "Repeat_Orders"
    ]
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Generated {len(records)} transaction rows successfully into {output_file}!")

if __name__ == "__main__":
    generate_firstclub_dataset()
