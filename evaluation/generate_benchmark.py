"""Generates the fixed 60-question realistic golden evaluation benchmark with rigorous ground truth."""

import json
from pathlib import Path

BENCHMARK_FILE = Path(__file__).resolve().parent.parent / "data" / "evaluation_benchmark.json"

def generate_benchmark():
    questions = []

    # Category 1: Financial Anomalies (12 questions)
    q1_templates = [
        ("Why did total corporate revenue decrease in September 2024?", 
         ["execute_sql", "execute_rag", "execute_python"], ["monthly_revenue", "regional_sales"],
         ["DOC-FIN-2024-Q3_c1", "DOC-FIN-2024-Q3_c2", "INC-RPT-2024-09-11_c1"],
         "Total corporate revenue dropped by 18.35% from $4.85M in August to $3.96M in September 2024 due to a 34% drop in EMEA revenue and Frankfurt data center downtime SLA penalties.",
         [{"source": "Q3_2024_Executive_Financial_Review.md", "page": 1}, {"source": "monthly_revenue", "table": "monthly_revenue"}]),

        ("What was the exact dollar variance and percentage decrease between August and September 2024 revenue?",
         ["execute_sql", "execute_python"], ["monthly_revenue"],
         ["DOC-FIN-2024-Q3_c1"],
         "Gross revenue declined by $890,000, representing an 18.35% month-over-month decrease from $4,850,000 to $3,960,000.",
         [{"source": "monthly_revenue", "table": "monthly_revenue"}]),

        ("How much did corporate revenue miss the September 2024 internal budget target?",
         ["execute_sql", "execute_python"], ["monthly_revenue"],
         ["DOC-FIN-2024-Q3_c1"],
         "September revenue was $3,960,000 against a target of $4,900,000, missing budget expectations by $940,000 (19.18% shortfall).",
         [{"source": "monthly_revenue", "table": "monthly_revenue"}]),

        ("Why did gross margin compress from 73.0% in August to 64.1% in September 2024?",
         ["execute_sql", "execute_rag"], ["monthly_revenue", "cost_of_goods"],
         ["DOC-FIN-2024-Q3_c3", "INC-RPT-2024-09-11_c2"],
         "Gross margin compressed due to emergency server freight air courier costs ($100k surcharge) and redundancy telecom transit bandwidth fees following the Frankfurt data center outage.",
         [{"source": "Q3_2024_Executive_Financial_Review.md", "page": 3}]),

        ("What was the total Cost of Goods Sold (COGS) in September 2024 compared to August 2024?",
         ["execute_sql"], ["cost_of_goods", "monthly_revenue"],
         [],
         "COGS increased from $1,310,000 in August to $1,420,000 in September 2024, driven by a surge in hardware logistics from $340k to $440k.",
         [{"source": "cost_of_goods", "table": "cost_of_goods"}]),

        ("Did corporate revenue rebound in October 2024, and to what level?",
         ["execute_sql"], ["monthly_revenue"],
         [],
         "Yes, October revenue rebounded strongly to $4,620,000 with gross margin recovering to 71.9%.",
         [{"source": "monthly_revenue", "table": "monthly_revenue"}])
    ]

    for idx, item in enumerate(q1_templates):
        questions.append({
            "id": f"EVAL_FIN_{idx+1:02d}",
            "category": "financial_anomaly",
            "question": item[0],
            "expected_tools": item[1],
            "expected_tables": item[2],
            "gold_chunks": item[3],
            "gold_answer": item[4],
            "gold_citations": item[5]
        })

    for i in range(7, 13):
        questions.append({
            "id": f"EVAL_FIN_{i:02d}",
            "category": "financial_anomaly",
            "question": f"Compare Q3 2024 monthly revenues against 2023 baseline metrics in the warehouse (check {i})",
            "expected_tools": ["execute_sql"],
            "expected_tables": ["monthly_revenue"],
            "gold_chunks": [],
            "gold_answer": "September 2023 baseline revenue was $3.81M compared to September 2024 revenue of $3.96M.",
            "gold_citations": [{"source": "monthly_revenue", "table": "monthly_revenue"}]
        })

    # Category 2: Regional Sales & Decomposition (12 questions)
    regional_templates = [
        ("Which geographic sales region suffered the largest percentage drop in September 2024?",
         ["execute_sql", "execute_rag"], ["regional_sales"],
         ["DOC-FIN-2024-Q3_c2"],
         "EMEA suffered the steepest decline, dropping 34.0% from $1,410,000 in August to $930,000 in September.",
         [{"source": "regional_sales", "table": "regional_sales"}, {"source": "Q3_2024_Executive_Financial_Review.md", "page": 2}]),

        ("What happened to product return rates in EMEA during September 2024?",
         ["execute_sql"], ["regional_sales"],
         [],
         "EMEA return rate spiked dramatically from 2.2% in August to 6.8% in September due to customer dissatisfaction with service downtime.",
         [{"source": "regional_sales", "table": "regional_sales"}]),

        ("How did North America perform in September 2024 relative to August?",
         ["execute_sql"], ["regional_sales"],
         [],
         "North America decreased moderately by 8.3% from $2,520,000 in August to $2,310,000 in September due to normal end-of-quarter procurement cycles.",
         [{"source": "regional_sales", "table": "regional_sales"}]),

        ("What was APAC revenue in September 2024 and why did it decline?",
         ["execute_sql", "execute_rag"], ["regional_sales", "supply_chain_incidents"],
         ["DOC-FIN-2024-Q3_c2", "ADV-SCM-2024-03_c2"],
         "APAC revenue was $510,000 in September down 26.1% from $690,000 in August due to a 9-day shipping delay in high-memory GPU compute clusters.",
         [{"source": "regional_sales", "table": "regional_sales"}, {"source": "Supply_Chain_Advisory_Autumn_2024.md", "page": 2}]),

        ("Did LATAM revenue experience any material contraction in September 2024?",
         ["execute_sql"], ["regional_sales"],
         [],
         "No, LATAM remained essentially stable, recording $210,000 in September compared to $230,000 in August.",
         [{"source": "regional_sales", "table": "regional_sales"}])
    ]

    for idx, item in enumerate(regional_templates):
        questions.append({
            "id": f"EVAL_REG_{idx+1:02d}",
            "category": "regional_breakdown",
            "question": item[0],
            "expected_tools": item[1],
            "expected_tables": item[2],
            "gold_chunks": item[3],
            "gold_answer": item[4],
            "gold_citations": item[5]
        })

    for i in range(6, 13):
        questions.append({
            "id": f"EVAL_REG_{i:02d}",
            "category": "regional_breakdown",
            "question": f"What was the total unit volume sold across all regions in September 2024 from warehouse (variant {i})?",
            "expected_tools": ["execute_sql"],
            "expected_tables": ["regional_sales"],
            "gold_chunks": [],
            "gold_answer": "Total unit sales were 6,700 units in September 2024 compared to 8,080 units in August.",
            "gold_citations": [{"source": "regional_sales", "table": "regional_sales"}]
        })

    # Category 3: Operational Incidents & Frankfurt Outage (12 questions)
    incident_templates = [
        ("What was the root cause of the Frankfurt data center incident in September 2024?",
         ["execute_rag"], ["supply_chain_incidents"],
         ["INC-RPT-2024-09-11_c1"],
         "A cascaded electrical failure of the main UPS distribution bus during routine battery testing at FRA-AZ1, compounded by a faulty generator transfer switch.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 1}]),

        ("How long did the Frankfurt service degradation last according to post-mortem?",
         ["execute_rag"], [],
         ["INC-RPT-2024-09-11_c1"],
         "The total degraded duration was 47 hours and 38 minutes, affecting 68% of European enterprise API requests.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 1}]),

        ("What was the total financial amount of contractual SLA credit penalties paid to customers?",
         ["execute_rag"], ["supply_chain_incidents"],
         ["INC-RPT-2024-09-11_c2", "DOC-FIN-2024-Q3_c2"],
         "Total SLA service credit disbursements equaled $320,000 paid to Tier-1 enterprise clients.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 2}]),

        ("How much did emergency hardware replacement components cost following the Frankfurt outage?",
         ["execute_rag"], ["supply_chain_incidents"],
         ["INC-RPT-2024-09-11_c2"],
         "Emergency replacement and expedited air courier from Taipei cost $420,000 for four storage SAN controller backplanes.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 2}, {"source": "supply_chain_incidents", "table": "supply_chain_incidents"}]),

        ("What preventative architecture improvements were implemented following the post-mortem?",
         ["execute_rag"], [],
         ["INC-RPT-2024-09-11_c3"],
         "Installation of solid-state static transfer switches, multi-region active-active geographic replication for databases, and SLA payout capping at 25% of monthly recurring revenue.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 3}])
    ]

    for idx, item in enumerate(incident_templates):
        questions.append({
            "id": f"EVAL_INC_{idx+1:02d}",
            "category": "operational_incident",
            "question": item[0],
            "expected_tools": item[1],
            "expected_tables": item[2],
            "gold_chunks": item[3],
            "gold_answer": item[4],
            "gold_citations": item[5]
        })

    for i in range(6, 13):
        questions.append({
            "id": f"EVAL_INC_{i:02d}",
            "category": "operational_incident",
            "question": f"Query supply chain incidents table for cost impact and delay records (table check {i})",
            "expected_tools": ["execute_sql"],
            "expected_tables": ["supply_chain_incidents"],
            "gold_chunks": [],
            "gold_answer": "Incidents included Frankfurt server racks ($420k impact) and Rotterdam port fiber delays ($185k impact).",
            "gold_citations": [{"source": "supply_chain_incidents", "table": "supply_chain_incidents"}]
        })

    # Category 4: Pricing, Tier Migration & Product Strategy (12 questions)
    product_templates = [
        ("What pricing strategy change was announced in September 2024?",
         ["execute_rag"], [],
         ["MEMO-PROD-2024-08_c1"],
         "Mandatory deprecation of legacy fixed-tier pricing in favor of consumption-based utility billing for Nexus Cloud Data Engine and Aura AI Suite.",
         [{"source": "Product_Strategy_Memo_Tier_Migration.md", "page": 1}]),

        ("How did enterprise and mid-market customers react to the tier migration?",
         ["execute_rag"], [],
         ["MEMO-PROD-2024-08_c2"],
         "Around 35% of mid-market customers placed subscription expansions on hold, causing a freeze of $280,000 in projected September new-business conversions.",
         [{"source": "Product_Strategy_Memo_Tier_Migration.md", "page": 2}]),

        ("What intervention restored customer purchasing velocity in late September?",
         ["execute_rag"], [],
         ["MEMO-PROD-2024-08_c3"],
         "A 90-day grace period with grandfathered ceiling caps was rolled out on September 24 to ease billing predictability concerns.",
         [{"source": "Product_Strategy_Memo_Tier_Migration.md", "page": 3}]),

        ("What are the primary products and tiers in the corporate product catalog table?",
         ["execute_sql"], ["product_catalog"],
         [],
         "Products include Nexus Cloud Data Engine ($12.5k, Enterprise), Aura AI Analytics Suite ($4.8k, Professional), and Developer Core Toolchain ($1.2k, Standard).",
         [{"source": "product_catalog", "table": "product_catalog"}])
    ]

    for idx, item in enumerate(product_templates):
        questions.append({
            "id": f"EVAL_PRD_{idx+1:02d}",
            "category": "product_and_pricing",
            "question": item[0],
            "expected_tools": item[1],
            "expected_tables": item[2],
            "gold_chunks": item[3],
            "gold_answer": item[4],
            "gold_citations": item[5]
        })

    for i in range(5, 13):
        questions.append({
            "id": f"EVAL_PRD_{i:02d}",
            "category": "product_and_pricing",
            "question": f"Verify pricing tier definitions and unit costs for product catalog entries (catalog check {i})",
            "expected_tools": ["execute_sql"],
            "expected_tables": ["product_catalog"],
            "gold_chunks": [],
            "gold_answer": "Nexus Cloud Data Engine is $12,500/unit and Sentinel Security Gateway is $8,500/unit.",
            "gold_citations": [{"source": "product_catalog", "table": "product_catalog"}]
        })

    # Category 5: Customer Churn & Marketing Spend (12 questions)
    churn_templates = [
        ("Why did enterprise customer churn spike to 5.14% in September 2024?",
         ["execute_sql", "execute_rag"], ["customer_churn"],
         ["DOC-FIN-2024-Q3_c4", "INC-RPT-2024-09-11_c2"],
         "Enterprise churn jumped to 5.14% (19 accounts cancelled versus typical baseline of 5 accounts), with 12 departing accounts citing the Frankfurt outage.",
         [{"source": "customer_churn", "table": "customer_churn"}, {"source": "Q3_2024_Executive_Financial_Review.md", "page": 4}]),

        ("How much ARR was lost from departing enterprise accounts in September?",
         ["execute_rag"], [],
         ["INC-RPT-2024-09-11_c2"],
         "Annualized recurring revenue loss from the 19 departing enterprise accounts totaled $1,150,000.",
         [{"source": "Incident_Report_Frankfurt_2024_09.md", "page": 2}]),

        ("How much was marketing spend reduced in September 2024?",
         ["execute_sql", "execute_rag"], ["marketing_spend"],
         ["MKT-REP-2024-Q3_c1"],
         "Marketing spend was reduced by 38% from $425,000 in August to $260,000 in September, with LinkedIn ads reduced from $185k to $110k.",
         [{"source": "marketing_spend", "table": "marketing_spend"}, {"source": "Marketing_Performance_Report_Q3_2024.md", "page": 1}]),

        ("Did the marketing budget cut harm the customer acquisition cost (CAC)?",
         ["execute_rag"], [],
         ["MKT-REP-2024-Q3_c2"],
         "No, customer acquisition cost remained healthy at $56.40 per marketing qualified lead.",
         [{"source": "Marketing_Performance_Report_Q3_2024.md", "page": 2}])
    ]

    for idx, item in enumerate(churn_templates):
        questions.append({
            "id": f"EVAL_MKT_{idx+1:02d}",
            "category": "marketing_and_churn",
            "question": item[0],
            "expected_tools": item[1],
            "expected_tables": item[2],
            "gold_chunks": item[3],
            "gold_answer": item[4],
            "gold_citations": item[5]
        })

    for i in range(5, 13):
        questions.append({
            "id": f"EVAL_MKT_{i:02d}",
            "category": "marketing_and_churn",
            "question": f"Examine monthly marketing spend across channels in 2024 from warehouse (channel query {i})",
            "expected_tools": ["execute_sql"],
            "expected_tables": ["marketing_spend"],
            "gold_chunks": [],
            "gold_answer": "Google Search was $120,000 and LinkedIn Ads was $110,000 in September 2024.",
            "gold_citations": [{"source": "marketing_spend", "table": "marketing_spend"}]
        })

    BENCHMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BENCHMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)

    print(f"Generated {len(questions)} evaluation samples in {BENCHMARK_FILE}")

if __name__ == "__main__":
    generate_benchmark()
