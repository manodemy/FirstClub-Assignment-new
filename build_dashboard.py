import csv
import json
import os

def compile_dashboard():
    csv_file = "raw_transaction_data.csv"
    template_file = "index_template.html"
    output_file = "index.html"
    
    demo_records = []
    
    # Read the first 500 rows or filter a clean subset of the CSV
    # Let's take about 600 rows to ensure we have a realistic and rich demo dataset,
    # covering multiple brands, categories, and dates.
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Select a representative sample of rows (first 24 unique FSNs)
            selected_fsns = [f"FSN{i:06d}" for i in range(1, 25)]
            
            for r in rows:
                if r["FSN"] in selected_fsns:
                    demo_records.append({
                        "Date": r["Date"],
                        "FSN": r["FSN"],
                        "Product_Name": r["Product_Name"],
                        "Brand": r["Brand"],
                        "Category": r["Category"],
                        "Subcategory": r["Subcategory"],
                        "Units_Sold": int(r["Units_Sold"]),
                        "Revenue": float(r["Revenue"]),
                        "Sell_Price": float(r["Sell_Price"]),
                        "Comp_Price": float(r["Comp_Price"]),
                        "Instock_Pct": float(r["Instock_Pct"]),
                        "Demand_Score": float(r["Demand_Score"]),
                        "Search_Rank": int(r["Search_Rank"]),
                        "Conversion_Rate": float(r["Conversion_Rate"]),
                        "Repeat_Orders": int(r["Repeat_Orders"])
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}. Using a synthetic small list.")
        demo_records = []

    # If csv loading failed or was empty, provide a minimal fallback list
    if not demo_records:
        demo_records = [
            {
                "Date": "2026-05-20", "FSN": "FSN000001", "Product_Name": "boAt Airdopes 141 TWS",
                "Brand": "boAt", "Category": "Audio", "Subcategory": "TWS",
                "Units_Sold": 25, "Revenue": 37500.0, "Sell_Price": 1500.0, "Comp_Price": 1600.0,
                "Instock_Pct": 92.5, "Demand_Score": 78.4, "Search_Rank": 12, "Conversion_Rate": 8.5,
                "Repeat_Orders": 4
            }
        ]

    demo_data_json = json.dumps(demo_records, indent=2)

    # Compile index_template.html -> index.html
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            template = f.read()
        output_content = template.replace("/* DEMO_DATA_PLACEHOLDER */", demo_data_json)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_content)
        print("Dashboard application index.html created successfully with embedded high-quality data slice!")
    except Exception as e:
        print(f"Error compiling index.html: {e}")

    # Compile anomaly_report_template.html -> anomaly_report.html
    try:
        anomaly_template_file = "anomaly_report_template.html"
        anomaly_output_file = "anomaly_report.html"
        if os.path.exists(anomaly_template_file):
            with open(anomaly_template_file, "r", encoding="utf-8") as f:
                anomaly_template = f.read()
            anomaly_output = anomaly_template.replace("/* DEMO_DATA_PLACEHOLDER */", demo_data_json)
            with open(anomaly_output_file, "w", encoding="utf-8") as f:
                f.write(anomaly_output)
            print("Anomaly report anomaly_report.html compiled successfully with embedded high-quality data slice!")
        else:
            print("Warning: anomaly_report_template.html not found.")
    except Exception as e:
        print(f"Error compiling anomaly_report.html: {e}")

if __name__ == "__main__":
    compile_dashboard()
