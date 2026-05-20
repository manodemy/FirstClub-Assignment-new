import csv
import json
import os
from datetime import datetime, timedelta

def compile_html():
    csv_file = "raw_transaction_data.csv"
    template_file = "index_template.html"
    output_file = "index.html"
    
    demo_records = []
    data_meta = {}
    
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # --- Data Sanity & Quality Checks ---
        total_rows = len(rows)
        all_dates = sorted(set(r["Date"] for r in rows))
        all_fsns  = sorted(set(r["FSN"]  for r in rows))
        
        # Validate Revenue ~ Units_Sold * Sell_Price (allow 1 rupee rounding)
        bad_revenue = 0
        zero_stock_with_sales = 0
        for r in rows:
            expected_rev = round(int(r["Units_Sold"]) * float(r["Sell_Price"]), 0)
            actual_rev   = float(r["Revenue"])
            if abs(expected_rev - actual_rev) > 1.0 and int(r["Units_Sold"]) > 0:
                bad_revenue += 1
            if float(r["Instock_Pct"]) < 5.0 and int(r["Units_Sold"]) > 0:
                zero_stock_with_sales += 1
        
        data_meta = {
            "total_rows":         total_rows,
            "total_fsns":         len(all_fsns),
            "date_range_start":   all_dates[0]  if all_dates else "N/A",
            "date_range_end":     all_dates[-1] if all_dates else "N/A",
            "total_dates":        len(all_dates),
            "revenue_mismatches": bad_revenue,
            "low_stock_but_sold": zero_stock_with_sales,
            "data_quality_pct":   round(100 * (1 - bad_revenue / max(total_rows, 1)), 2),
        }
        
        print(f"[Sanity] Rows: {total_rows:,} | FSNs: {len(all_fsns)} | Dates: {len(all_dates)} "
              f"| Date range: {all_dates[0]} -> {all_dates[-1]}")
        print(f"[Sanity] Revenue mismatches: {bad_revenue} | Low-stock-with-sales: {zero_stock_with_sales} "
              f"| Data quality: {data_meta['data_quality_pct']}%")
        
        # Embed: ALL FSNs for last 30 days (rich fallback for GitHub Pages / offline use)
        # This gives 200 FSNs × 30 days = up to 6,000 rows — plenty for all KPI and anomaly work
        if len(all_dates) >= 30:
            cutoff_date = all_dates[-30]   # 30th-to-last date
        else:
            cutoff_date = all_dates[0]
        
        for r in rows:
            if r["Date"] >= cutoff_date:
                demo_records.append({
                    "Date":            r["Date"],
                    "FSN":             r["FSN"],
                    "Product_Name":    r["Product_Name"],
                    "Brand":           r["Brand"],
                    "Category":        r["Category"],
                    "Subcategory":     r["Subcategory"],
                    "Units_Sold":      int(r["Units_Sold"]),
                    "Revenue":         float(r["Revenue"]),
                    "Sell_Price":      float(r["Sell_Price"]),
                    "Comp_Price":      float(r["Comp_Price"]),
                    "Instock_Pct":     float(r["Instock_Pct"]),
                    "Demand_Score":    float(r["Demand_Score"]),
                    "Search_Rank":     int(r["Search_Rank"]),
                    "Conversion_Rate": float(r["Conversion_Rate"]),
                    "Repeat_Orders":   int(r["Repeat_Orders"])
                })
        
        print(f"[Compile] Embedded {len(demo_records):,} rows (all FSNs, last 30 days of {cutoff_date} -> {all_dates[-1]}) as fallback data.")
    
    except Exception as e:
        print(f"Error reading CSV: {e}. Generating minimum fallback.")
        demo_records = [
            {
                "Date": "2026-05-20", "FSN": "FSN000001", "Product_Name": "boAt Airdopes 141 TWS",
                "Brand": "boAt", "Category": "Audio", "Subcategory": "TWS",
                "Units_Sold": 25, "Revenue": 37500.0, "Sell_Price": 1500.0, "Comp_Price": 1600.0,
                "Instock_Pct": 92.5, "Demand_Score": 78.4, "Search_Rank": 12, "Conversion_Rate": 8.5,
                "Repeat_Orders": 4
            }
        ]
        data_meta = {"total_rows": 1, "total_fsns": 1, "date_range_start": "N/A",
                     "date_range_end": "N/A", "total_dates": 1, "revenue_mismatches": 0,
                     "low_stock_but_sold": 0, "data_quality_pct": 100.0}

    # Convert to json string
    demo_json = json.dumps(demo_records, indent=2)
    meta_json = json.dumps(data_meta)
    
    # Compile index_template.html -> index.html
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            template = f.read()
        output_content = template.replace("/* DEMO_DATA_PLACEHOLDER */", demo_json)
        output_content = output_content.replace("/* DATA_META_PLACEHOLDER */", meta_json)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"Compiled successfully! Output dashboard written to {output_file}.")
    except Exception as e:
        print(f"Error compiling index.html: {e}")

    # Compile anomaly_report_template.html -> anomaly_report.html
    try:
        anomaly_template_file = "anomaly_report_template.html"
        anomaly_output_file   = "anomaly_report.html"
        if os.path.exists(anomaly_template_file):
            with open(anomaly_template_file, "r", encoding="utf-8") as f:
                anomaly_template = f.read()
            anomaly_output = anomaly_template.replace("/* DEMO_DATA_PLACEHOLDER */", demo_json)
            anomaly_output = anomaly_output.replace("/* DATA_META_PLACEHOLDER */", meta_json)
            with open(anomaly_output_file, "w", encoding="utf-8") as f:
                f.write(anomaly_output)
            print(f"Compiled successfully! Output anomaly report written to {anomaly_output_file}.")
        else:
            print("Warning: anomaly_report_template.html not found.")
    except Exception as e:
        print(f"Error compiling anomaly_report.html: {e}")

if __name__ == "__main__":
    compile_html()
