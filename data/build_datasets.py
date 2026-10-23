"""Generates realistic corporate datasets and document intelligence files."""

import sqlite3
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
DOCS_DIR = DATA_DIR / "documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "sample_database.sqlite"

def create_sample_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables if any
    cursor.executescript("""
    DROP TABLE IF EXISTS monthly_revenue;
    DROP TABLE IF EXISTS regional_sales;
    DROP TABLE IF EXISTS product_catalog;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customer_churn;
    DROP TABLE IF EXISTS marketing_spend;
    DROP TABLE IF EXISTS supply_chain_incidents;
    DROP TABLE IF EXISTS cost_of_goods;
    """)
    
    # 1. monthly_revenue
    cursor.execute("""
    CREATE TABLE monthly_revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        year INT NOT NULL,
        revenue REAL NOT NULL,
        target REAL NOT NULL,
        cogs REAL NOT NULL,
        gross_margin REAL NOT NULL
    );
    """)
    
    # Populate monthly revenue for 2023 & 2024
    revenue_data = [
        ("January", 2024, 4120000.0, 4000000.0, 1150000.0, 0.721),
        ("February", 2024, 4280000.0, 4150000.0, 1180000.0, 0.724),
        ("March", 2024, 4510000.0, 4300000.0, 1220000.0, 0.729),
        ("April", 2024, 4420000.0, 4400000.0, 1210000.0, 0.726),
        ("May", 2024, 4650000.0, 4500000.0, 1260000.0, 0.729),
        ("June", 2024, 4790000.0, 4650000.0, 1290000.0, 0.731),
        ("July", 2024, 4720000.0, 4700000.0, 1280000.0, 0.729),
        ("August", 2024, 4850000.0, 4800000.0, 1310000.0, 0.730),
        ("September", 2024, 3960000.0, 4900000.0, 1420000.0, 0.641),  # The key anomaly! (-18.35% MoM, $890k drop)
        ("October", 2024, 4620000.0, 4950000.0, 1300000.0, 0.719),
        ("November", 2024, 4890000.0, 5050000.0, 1340000.0, 0.726),
        ("December", 2024, 5210000.0, 5200000.0, 1390000.0, 0.733),
        # 2023 baseline
        ("September", 2023, 3810000.0, 3750000.0, 1080000.0, 0.717),
        ("August", 2023, 3740000.0, 3700000.0, 1060000.0, 0.717)
    ]
    cursor.executemany("""
    INSERT INTO monthly_revenue (month, year, revenue, target, cogs, gross_margin)
    VALUES (?, ?, ?, ?, ?, ?);
    """, revenue_data)
    
    # 2. regional_sales
    cursor.execute("""
    CREATE TABLE regional_sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        month TEXT NOT NULL,
        year INT NOT NULL,
        revenue REAL NOT NULL,
        units_sold INT NOT NULL,
        return_rate REAL NOT NULL
    );
    """)
    regional_data = [
        # August 2024
        ("North America", "August", 2024, 2520000.0, 4200, 0.018),
        ("EMEA", "August", 2024, 1410000.0, 2350, 0.022),
        ("APAC", "August", 2024, 690000.0, 1150, 0.015),
        ("LATAM", "August", 2024, 230000.0, 380, 0.025),
        # September 2024 - EMEA plummeted from $1.41M to $930K (-34.0%)
        ("North America", "September", 2024, 2310000.0, 3950, 0.021),
        ("EMEA", "September", 2024, 930000.0, 1510, 0.068),  # Huge return spike + outage
        ("APAC", "September", 2024, 510000.0, 890, 0.019),
        ("LATAM", "September", 2024, 210000.0, 350, 0.024),
        # October 2024 - Recovery
        ("North America", "October", 2024, 2480000.0, 4180, 0.019),
        ("EMEA", "October", 2024, 1310000.0, 2210, 0.024),
        ("APAC", "October", 2024, 610000.0, 1020, 0.017),
        ("LATAM", "October", 2024, 220000.0, 370, 0.023)
    ]
    cursor.executemany("""
    INSERT INTO regional_sales (region, month, year, revenue, units_sold, return_rate)
    VALUES (?, ?, ?, ?, ?, ?);
    """, regional_data)
    
    # 3. product_catalog
    cursor.execute("""
    CREATE TABLE product_catalog (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL,
        tier TEXT NOT NULL
    );
    """)
    products = [
        ("PRD-001", "Nexus Cloud Data Engine", "Infrastructure", 12500.0, "Enterprise"),
        ("PRD-002", "Aura AI Analytics Suite", "Software", 4800.0, "Professional"),
        ("PRD-003", "Developer Core Toolchain", "Developer Tools", 1200.0, "Standard"),
        ("PRD-004", "Sentinel Security Gateway", "Security", 8500.0, "Enterprise"),
        ("PRD-005", "StreamLine Integration Bus", "Middleware", 3200.0, "Professional")
    ]
    cursor.executemany("""
    INSERT INTO product_catalog (product_id, product_name, category, unit_price, tier)
    VALUES (?, ?, ?, ?, ?);
    """, products)
    
    # 4. orders
    cursor.execute("""
    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        order_date TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        region TEXT NOT NULL
    );
    """)
    orders_sample = [
        ("ORD-20240901-01", "CUST-1001", "PRD-001", "2024-09-02", 25000.0, "Completed", "North America"),
        ("ORD-20240905-02", "CUST-1044", "PRD-002", "2024-09-05", 9600.0, "Completed", "EMEA"),
        ("ORD-20240912-03", "CUST-1088", "PRD-004", "2024-09-12", 17000.0, "Cancelled", "EMEA"),
        ("ORD-20240914-04", "CUST-1092", "PRD-001", "2024-09-14", 50000.0, "Refunded", "EMEA"),
        ("ORD-20240918-05", "CUST-1105", "PRD-002", "2024-09-18", 14400.0, "Delayed", "APAC"),
        ("ORD-20240922-06", "CUST-1120", "PRD-005", "2024-09-22", 6400.0, "Completed", "North America"),
        ("ORD-20240928-07", "CUST-1150", "PRD-001", "2024-09-28", 25000.0, "Completed", "North America"),
        ("ORD-20240810-01", "CUST-1001", "PRD-001", "2024-08-10", 50000.0, "Completed", "North America"),
        ("ORD-20240815-02", "CUST-1033", "PRD-004", "2024-08-15", 34000.0, "Completed", "EMEA"),
        ("ORD-20240822-03", "CUST-1065", "PRD-001", "2024-08-22", 37500.0, "Completed", "EMEA")
    ]
    cursor.executemany("""
    INSERT INTO orders (order_id, customer_id, product_id, order_date, amount, status, region)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, orders_sample)
    
    # 5. customer_churn
    cursor.execute("""
    CREATE TABLE customer_churn (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        year INT NOT NULL,
        tier TEXT NOT NULL,
        churned_count INT NOT NULL,
        active_users INT NOT NULL,
        churn_rate REAL NOT NULL
    );
    """)
    churn_data = [
        ("July", 2024, "Enterprise", 4, 380, 0.0105),
        ("August", 2024, "Enterprise", 5, 385, 0.0129),
        ("September", 2024, "Enterprise", 19, 369, 0.0514),  # Spike due to outage & SLA breaches
        ("October", 2024, "Enterprise", 6, 372, 0.0161),
        ("September", 2024, "Professional", 42, 1250, 0.0336),
        ("August", 2024, "Professional", 24, 1260, 0.0190)
    ]
    cursor.executemany("""
    INSERT INTO customer_churn (month, year, tier, churned_count, active_users, churn_rate)
    VALUES (?, ?, ?, ?, ?, ?);
    """, churn_data)
    
    # 6. marketing_spend
    cursor.execute("""
    CREATE TABLE marketing_spend (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        year INT NOT NULL,
        channel TEXT NOT NULL,
        spend REAL NOT NULL,
        acquired_leads INT NOT NULL
    );
    """)
    mkt_data = [
        ("August", 2024, "Google Search", 145000.0, 3200),
        ("August", 2024, "LinkedIn Ads", 185000.0, 2400),
        ("August", 2024, "Tech Conferences", 95000.0, 850),
        ("September", 2024, "Google Search", 120000.0, 2800),
        ("September", 2024, "LinkedIn Ads", 110000.0, 1600), # Budget curtailed by 40%
        ("September", 2024, "Tech Conferences", 30000.0, 210)
    ]
    cursor.executemany("""
    INSERT INTO marketing_spend (month, year, channel, spend, acquired_leads)
    VALUES (?, ?, ?, ?, ?);
    """, mkt_data)
    
    # 7. supply_chain_incidents
    cursor.execute("""
    CREATE TABLE supply_chain_incidents (
        incident_id TEXT PRIMARY KEY,
        date TEXT NOT NULL,
        component TEXT NOT NULL,
        affected_region TEXT NOT NULL,
        delay_days INT NOT NULL,
        severity TEXT NOT NULL,
        cost_impact REAL NOT NULL
    );
    """)
    incidents = [
        ("INC-2024-09-01", "2024-09-11", "Frankfurt Tier-3 Cloud Server Racks", "EMEA", 18, "Critical", 420000.0),
        ("INC-2024-09-02", "2024-09-15", "Rotterdam Port Fiber Hardware", "EMEA", 12, "High", 185000.0),
        ("INC-2024-09-03", "2024-09-19", "APAC High-Memory GPU Clusters", "APAC", 9, "Medium", 95000.0),
        ("INC-2024-08-01", "2024-08-14", "Austin Power Conditioning Unit", "North America", 3, "Low", 25000.0)
    ]
    cursor.executemany("""
    INSERT INTO supply_chain_incidents (incident_id, date, component, affected_region, delay_days, severity, cost_impact)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, incidents)
    
    # 8. cost_of_goods
    cursor.execute("""
    CREATE TABLE cost_of_goods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        year INT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL
    );
    """)
    cogs_data = [
        ("August", 2024, "Cloud Hosting & Datacenters", 680000.0),
        ("August", 2024, "Third-Party APIs & Software", 290000.0),
        ("August", 2024, "Hardware Replacement & Logistics", 340000.0),
        ("September", 2024, "Cloud Hosting & Datacenters", 695000.0),
        ("September", 2024, "Third-Party APIs & Software", 285000.0),
        ("September", 2024, "Hardware Replacement & Logistics", 440000.0) # $100k surge from emergency rerouting
    ]
    cursor.executemany("""
    INSERT INTO cost_of_goods (month, year, category, amount)
    VALUES (?, ?, ?, ?);
    """, cogs_data)
    
    conn.commit()
    conn.close()
    print("Sample SQLite database created successfully at:", DB_PATH)

def create_sample_documents():
    # 1. Q3 2024 Executive Financial Review
    doc1 = """# Q3 2024 Executive Financial Review & Earnings Commentary
**Document ID:** DOC-FIN-2024-Q3
**Date Published:** October 15, 2024
**Authors:** Chief Financial Officer (Elena Rostova), VP of Financial Planning & Analysis (Marcus Vance)
**Audience:** Board of Directors & Senior Leadership

## Section 1: Executive Summary & Performance Highlights (Page 1)
During the third quarter of 2024, total corporate gross revenue achieved $13.53M, representing a slight 1.2% contraction relative to the initial internal target of $14.40M. While July ($4.72M) and August ($4.85M) registered steady performance in line with our growth trajectory, September experienced an acute top-line deceleration, dropping to $3.96M—an 18.35% month-over-month decrease ($890,000 variance against August).

## Section 2: Regional Performance & September Anomaly Breakdown (Page 2)
The revenue shortfall was overwhelmingly localized to the EMEA operating theater:
- North America revenue declined mildly by 8.3% ($2.52M in August to $2.31M in September), attributable to normal procurement end-of-quarter cyclicity.
- EMEA revenue collapsed by 34.0%, plummeting from $1.41M in August to $930,000 in September.
- APAC registered $510,000 against $690,000 in August (-26.1%).
- LATAM held essentially flat at $210,000.

The primary catalyst for the EMEA contraction was an unforeseen 48-hour service degradation across our Frankfurt primary data center node beginning September 11, which triggered contractual SLA credit penalties totaling $320,000 and the postponement of three enterprise contract renewals valued at $410,000 into Q4.

## Section 3: Cost of Goods & Margin Compression (Page 3)
Cost of goods sold (COGS) reached $1.42M in September compared to $1.31M in August. Gross margin compressed from 73.0% in August to 64.1% in September. The key drivers were emergency server freight costs ($100,000 surcharge for expedited air courier from Taiwan) and emergency redundancy bandwidth fees billed by our European telecom transit providers.

## Section 4: Churn Impact & Enterprise Retention (Page 4)
Enterprise churn rose to 5.14% in September (19 account cancellations versus our baseline expectation of 5 accounts). Post-churn exit interviews revealed that 12 of the 19 departing accounts cited operational risk concerns tied to the Frankfurt downtime. The executive team instituted an immediate Customer Assurance Credit program and dedicated technical account managers to stabilize the affected customer tier.
"""
    (DOCS_DIR / "Q3_2024_Executive_Financial_Review.md").write_text(doc1, encoding="utf-8")

    # 2. Frankfurt Incident Report
    doc2 = """# Major Incident Post-Mortem: Frankfurt Data Center Degradation
**Document ID:** INC-RPT-2024-09-11
**Incident Reference:** INC-2024-09-01
**Date of Incident:** September 11-13, 2024
**Author:** Director of Site Reliability Engineering (Dr. Henrik Lindqvist)
**Severity:** P0 - Critical Outage

## Section 1: Incident Description & Timeline (Page 1)
At 08:14 UTC on September 11, 2024, our primary Frankfurt availability zone (FRA-AZ1) experienced a cascaded failure of its main uninterruptible power supply (UPS) distribution bus during routine battery load testing. Redundant failover to generator banks was interrupted due to a faulty transfer relay switch.

Total degraded duration: 47 hours and 38 minutes.
Service impact: 68% of European enterprise API requests experienced latency spikes exceeding 3,500ms or returned HTTP 504 Gateway Timeouts.

## Section 2: Direct Financial & Operational Consequences (Page 2)
1. **Contractual SLA Penalties:** Total service credit disbursements issued to Tier-1 enterprise clients equaled $320,000.
2. **Hardware Damage & Emergency Sourcing:** Four primary storage SAN controller backplanes were shorted during the voltage spike. Replacement components had to be sourced via chartered cargo from Taipei, racking up $420,000 in direct emergency replacement and freight fees.
3. **Customer Churn:** 19 enterprise accounts terminated their contracts within 14 days of the incident, resulting in an annualized recurring revenue (ARR) loss of $1,150,000.

## Section 3: Remediation & Preventative Roadmap (Page 3)
- Replaced all electromechanical transfer switches with solid-state static transfer systems across all European data centers.
- Implemented multi-region active-active geographic replication for all enterprise database instances to eliminate single-datacenter failure modes.
- Revised SLA terms to cap single-month credit payouts to 25% of monthly recurring revenue.
"""
    (DOCS_DIR / "Incident_Report_Frankfurt_2024_09.md").write_text(doc2, encoding="utf-8")

    # 3. Product Pricing Tier Migration Memo
    doc3 = """# Product Strategy Memo: 2024 Tier Migration & Legacy Sunset
**Document ID:** MEMO-PROD-2024-08
**Date:** August 20, 2024
**Author:** Chief Product Officer (Sophia Chen)
**Topic:** Transition from Legacy Standard to Consumption-Based Pricing

## Section 1: Background & Objectives (Page 1)
On September 1, 2024, the product management organization initiated the mandatory deprecation of our legacy fixed-tier pricing model for 'Nexus Cloud Data Engine' and 'Aura AI Analytics Suite', migrating all existing customer contracts to consumption-based utility billing.

## Section 2: Market Friction & Customer Pushback (Page 2)
The timing of the migration coincided with the Frankfurt infrastructure disruption in mid-September. Customers already anxious about reliability reacted with heightened resistance to usage billing. Approximately 35% of mid-market customers placed their subscription expansion orders on hold pending price predictability assurances. This caused a temporary freeze of $280,000 in projected September new-business pipeline conversions.

## Section 3: Mitigation Plan (Page 3)
A 90-day grace period with grandfathered ceiling caps was rolled out on September 24 to appease accounts with erratic billing forecasts. This intervention restored pipeline velocity in October.
"""
    (DOCS_DIR / "Product_Strategy_Memo_Tier_Migration.md").write_text(doc3, encoding="utf-8")

    # 4. Supply Chain Logistics Advisory
    doc4 = """# Global Logistics & Hardware Supply Chain Advisory: Autumn 2024
**Document ID:** ADV-SCM-2024-03
**Date:** September 18, 2024
**Author:** VP of Global Procurement (David O'Connor)

## Section 1: Semiconductor & Fiber Switch Bottlenecks (Page 1)
During late August through September 2024, global shipping congestions centered around the Port of Rotterdam caused transit delays of 12 to 18 days for critical networking modules and high-bandwidth fiber optic transceivers. 

## Section 2: Financial Impact on Delivery Timelines (Page 2)
The average cost impact logged under supply chain incidents reached $420,000 for the Frankfurt server restoration, plus $185,000 for Rotterdam port rerouting. High-memory GPU cluster deliveries for APAC customers were delayed by 9 business days, moving approximately $180,000 of delivery milestone billing from September into the October accounting cycle.
"""
    (DOCS_DIR / "Supply_Chain_Advisory_Autumn_2024.md").write_text(doc4, encoding="utf-8")

    # 5. Marketing Spend & Demand Generation Report
    doc5 = """# Demand Generation & Marketing Performance Report: Q3 2024
**Document ID:** MKT-REP-2024-Q3
**Date:** October 5, 2024
**Author:** Chief Marketing Officer (Rachel Zane)

## Section 1: Channel Expenditure Optimization (Page 1)
In response to mid-quarter budget realignment mandates from the CFO, marketing spend was curtailed by 38% in September, dropping from $425,000 in August to $260,000 in September. LinkedIn sponsored ad campaigns were cut from $185,000 to $110,000, and paid search was reduced from $145,000 to $120,000.

## Section 2: Lead Velocity & Pipeline Attribution (Page 2)
Acquired inbound marketing qualified leads (MQLs) declined from 6,450 in August to 4,610 in September. However, customer acquisition cost (CAC) remained healthy at $56.40 per lead. The reduction in top-of-funnel lead velocity primarily impacts Q4 deal closures rather than immediate September bookings.
"""
    (DOCS_DIR / "Marketing_Performance_Report_Q3_2024.md").write_text(doc5, encoding="utf-8")

    print("Sample business intelligence documents created successfully in:", DOCS_DIR)

if __name__ == "__main__":
    create_sample_database()
    create_sample_documents()
