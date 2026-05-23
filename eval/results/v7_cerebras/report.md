# DOCNEST Multi-Format RAG Accuracy Evaluation

**Date:** 2026-05-23  
**Formats tested:** PDF, DOCX, XLSX, HTML, Markdown  
**Judge:** Gemini 2.5 Pro  

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Average accuracy** | **8.6 / 10** |
| **Pass rate (≥ 7/10)** | **93%** |
| Total questions | 88 |
| Documents evaluated | 10 |

### Accuracy by Format

| Format | Avg Score | Pass Rate | Questions |
|--------|-----------|-----------|-----------|
| 📊 XLSX | 8.7/10 | 93% | 15 |
| 📝 DOCX | 7.9/10 | 86% | 14 |
| 🌐 HTML | 8.9/10 | 93% | 14 |
| 📋 MD | 8.7/10 | 100% | 15 |
| 📄 PDF | 8.7/10 | 93% | 30 |

---

## Efficiency Metrics

### Token Consumption (docnest vs Traditional Naive Chunking RAG)

| Document | Format | docnest Tokens | Trad. Tokens | Reduction | Avg docnest ms | Avg Trad ms |
|----------|--------|---------------|--------------|-----------|---------------|-------------|
| Acme Corp Financial Workbook 2024 | 📊 XLSX | 38,991 | 48,840 | **20.2%** | 555 ms | 2 ms |
| TechVision Inc Annual Report 2024 | 📝 DOCX | 11,789 | 35,224 | **66.5%** | 497 ms | 3 ms |
| NexusAPI v3 Developer Reference | 🌐 HTML | 9,631 | 19,418 | **50.4%** | 496 ms | 2 ms |
| CloudMesh Technical Architecture Sp | 📋 MD | 8,650 | 29,835 | **71.0%** | 455 ms | 2 ms |
| IPCC AR6 — Summary for Policymakers | 📄 PDF | 22,946 | 17,280 | **-32.8%** | 1001 ms | 17 ms |
| BIS Annual Economic Report 2024 | 📄 PDF | 18,040 | 17,280 | **-4.4%** | 640 ms | 61 ms |
| GPT-3 Paper — Language Models are F | 📄 PDF | 46,637 | 17,280 | **-169.9%** | 521 ms | 38 ms |
| Attention Is All You Need — Transfo | 📄 PDF | 20,017 | 16,928 | **-18.2%** | 73 ms | 7 ms |
| Llama 2 — Open Foundation and Fine- | 📄 PDF | 46,888 | 17,280 | **-171.3%** | 226 ms | 28 ms |
| Constitutional AI — Harmlessness fr | 📄 PDF | 9,216 | 17,280 | **46.7%** | 297 ms | 17 ms |
| **TOTAL** | — | **232,805** | **236,645** | **1.6%** | — | — |

> docnest used **1.6% fewer tokens** than a traditional naive chunking RAG across all 10 documents and 88 questions.


---

## Results by Document

### 📊 Acme Corp Financial Workbook 2024 (`XLSX`)

| | |
|---|---|
| Sections | 10 |
| Tables extracted | 10 |
| Parse time | 104 ms |
| Avg score | **8.7/10** |
| Pass rate | **93%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What was the total Q1 revenue across all products in US… | ✅ 10/10 | 739 | 2 | 1,929 | 3,256 | The total Q1 revenue across all products is given in the "TOTAL" row under the Q… | The sum of Q1 column: DataSync Pro 4200 + CloudVault 3100 +  |
| 2 | Which product had the highest annual revenue and how mu… | ✅ 7/10 | 553 | 2 | 2,448 | 3,256 | The product with the highest annual revenue was DataSync Pro, and its annual rev… | DataSync Pro: 4200+5100+6300+7800 = 23400 |
| 3 | How many total employees does the Engineering departmen… | ✅ 10/10 | 513 | 2 | 2,192 | 3,256 | The Engineering department has 142 full-time employees and 8 part-time employees… | Engineering: 142 FT + 8 PT = 150 |
| 4 | Which region had the highest year-over-year growth perc… | ⚠️ 5/10 | 528 | 2 | 3,002 | 3,256 | The region with the highest year-over-year growth percentage is Asia Pacific, wi… | Asia Pacific 31.7% is the highest in the Regional Sales shee |
| 5 | What is the NRR% for the Mid-Market customer segment? | ✅ 7/10 | 565 | 2 | 2,697 | 3,256 | The NRR% for the Mid-Market customer segment is 118.… | Customer Segments sheet: Mid-Market (100-999 emp) NRR% = 118 |
| 6 | What was SupportDesk's Q3 revenue and what was its full… | ✅ 7/10 | 521 | 2 | 3,010 | 3,256 | SupportDesk's Q3 revenue was 1100 USD thousands, and its full-year annual total … | SupportDesk row: Q1=950, Q2=1020, Q3=1100, Q4=1250; Annual T |
| 7 | Which month had the highest combined total revenue acro… | ✅ 10/10 | 608 | 2 | 2,685 | 3,256 | The month with the highest combined total revenue across all products in the Mon… | Monthly Trend sheet: Nov had the highest total of 7,052 USD  |
| 8 | What is the total ARR (in USD thousands) from Enterpris… | ✅ 10/10 | 587 | 3 | 2,712 | 3,256 | To calculate the total ARR (in USD thousands) from Enterprise tier customers in … | Top Accounts: sum of ARR for all Enterprise tier rows = 7,60 |
| 9 | How many customer accounts are based in the Asia Pacifi… | ✅ 10/10 | 563 | 2 | 3,007 | 3,256 | To determine the number of customer accounts based in the Asia Pacific region, w… | Top Accounts sheet: 6 accounts have Region = 'Asia Pacific' |
| 10 | Which product had the highest annual gross margin perce… | ✅ 8/10 | 507 | 2 | 2,448 | 3,256 | The product with the highest annual gross margin percentage in the Product Margi… | Product Margin sheet: DataSync Pro annual GM% = 75.4% |
| 11 | What is the Net Revenue Retention (NRR) rate for Enterp… | ✅ 10/10 | 546 | 2 | 2,729 | 3,256 | The Net Revenue Retention (NRR) rate for Enterprise segment customers is 132%.… | Customer Segments sheet: Enterprise NRR = 132% |
| 12 | What was the total annual R&D expense and how does it c… | ✅ 8/10 | 494 | 2 | 2,200 | 3,256 | The total annual R&D expense was 210000.   The total annual Sales & Marketing ex… | Expense Detail sheet: R&D Full Year = 210,000, S&M = 170,000 |
| 13 | What was the total partnership channel revenue in 2024 … | ✅ 10/10 | 563 | 2 | 3,017 | 3,256 | The total partnership channel revenue in 2024 was 38700. The partner type with t… | Partnerships sheet: Total = 38,700, Referral 62.3% YoY growt |
| 14 | How many R&D projects have Priority P0 status and how m… | ✅ 10/10 | 533 | 2 | 3,011 | 3,256 | - R&D projects with Priority P0 status:     1. AI Recommendation Engine     2. Z… | R&D Projects sheet: 3 P0 priority projects, 3 completed |
| 15 | What is the total revenue and YoY growth percentage for… | ✅ 8/10 | 509 | 2 | 1,904 | 3,256 | The total revenue for the System Integrator partner type is 9800, and the YoY gr… | Partnerships sheet: System Integrator — Revenue 9,800, YoY G |

<details><summary>Q1: What was the total Q1 revenue across all products in USD thousands?</summary>

**Retrieved section:** `§1` | **Query latency:** 739 ms

**DOCNEST answer:**
> The total Q1 revenue across all products is given in the "TOTAL" row under the Q1 column in the Revenue table.    From the document:  - Q1 revenue for DataSync Pro: 4200  - Q1 revenue for CloudVault: 3100  - Q1 revenue for SecureID: 1800  - Q1 revenue for AnalyticsEdge: 2500  - Q1 revenue for SupportDesk: 950  - Total Q1 revenue: 12550    Step-by-step sum:  4200 + 3100 = 7300    7300 + 1800 = 9100    9100 + 2500 = 11600    11600 + 950 = 12550      Verified total: 12550    Answer: The total Q1 revenue across all products is 12,550 thousand USD.

**Ground truth:**
> The sum of Q1 column: DataSync Pro 4200 + CloudVault 3100 + SecureID 1800 + AnalyticsEdge 2500 + SupportDesk 950 = 12550

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=1.00

</details>

<details><summary>Q2: Which product had the highest annual revenue and how much was it?</summary>

**Retrieved section:** `§1` | **Query latency:** 553 ms

**DOCNEST answer:**
> The product with the highest annual revenue was DataSync Pro, and its annual revenue was 23400.

**Ground truth:**
> DataSync Pro: 4200+5100+6300+7800 = 23400

**Score:** 7/10 — local-judge: num=0.20 kw=0.43 phrase=0.50

</details>

<details><summary>Q3: How many total employees does the Engineering department have (full-time + part-time)?</summary>

**Retrieved section:** `§2` | **Query latency:** 513 ms

**DOCNEST answer:**
> The Engineering department has 142 full-time employees and 8 part-time employees.    Total employees = 142 + 8 = 150.      Answer: The Engineering department has a total of 150 employees (142 full-time + 8 part-time).

**Ground truth:**
> Engineering: 142 FT + 8 PT = 150

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=1.00

</details>

<details><summary>Q4: Which region had the highest year-over-year growth percentage?</summary>

**Retrieved section:** `§3` | **Query latency:** 528 ms

**DOCNEST answer:**
> The region with the highest year-over-year growth percentage is Asia Pacific, with a YoY Growth % of 31.7.

**Ground truth:**
> Asia Pacific 31.7% is the highest in the Regional Sales sheet

**Score:** 5/10 — local-judge: num=0.00 kw=0.50 phrase=0.00

</details>

<details><summary>Q5: What is the NRR% for the Mid-Market customer segment?</summary>

**Retrieved section:** `§7` | **Query latency:** 565 ms

**DOCNEST answer:**
> The NRR% for the Mid-Market customer segment is 118.

**Ground truth:**
> Customer Segments sheet: Mid-Market (100-999 emp) NRR% = 118

**Score:** 7/10 — local-judge: num=0.33 kw=0.50 phrase=0.00

</details>

<details><summary>Q6: What was SupportDesk's Q3 revenue and what was its full-year annual total in USD thousands?</summary>

**Retrieved section:** `§1` | **Query latency:** 521 ms

**DOCNEST answer:**
> SupportDesk's Q3 revenue was 1100 USD thousands, and its full-year annual total was 4320 USD thousands.

**Ground truth:**
> SupportDesk row: Q1=950, Q2=1020, Q3=1100, Q4=1250; Annual Total = 950+1020+1100+1250 = 4320

**Score:** 7/10 — local-judge: num=0.33 kw=0.50 phrase=0.00

</details>

<details><summary>Q7: Which month had the highest combined total revenue across all products in the Monthly Trend sheet?</summary>

**Retrieved section:** `§4` | **Query latency:** 608 ms

**DOCNEST answer:**
> The month with the highest combined total revenue across all products in the Monthly Trend sheet is December, with a total of 6963.

**Ground truth:**
> Monthly Trend sheet: Nov had the highest total of 7,052 USD thousands

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.56

</details>

<details><summary>Q8: What is the total ARR (in USD thousands) from Enterprise tier customers in the Top Accounts sheet?</summary>

**Retrieved section:** `§5` | **Query latency:** 587 ms

**DOCNEST answer:**
> To calculate the total ARR (in USD thousands) from Enterprise tier customers in the Top Accounts sheet:    Step 1: Identify all Enterprise tier customers and their ARR values from the Top Accounts sheet:  - Apex Industries: 480  - BlueSky Corp: 320  - DataBridge Inc: 560  - FortressAI: 720  - Horizon Tech: 410  - Juno Systems: 290  - Keystone Capital: 380  - Meridian Bank: 850  - NexGen Pharma: 430  - PeakLogix: 510  - Quantum Fintech: 390  - SkyLine Energy: 260  - TechForge: 640  - Unified HealthCo: 470  - WaveCore Systems: 580    Step 2: Add the ARR values step-by-step:  480 + 320 = 800    800 + 560 = 1360    1360 + 720 = 2080    2080 + 410 = 2490    2490 + 290 = 2780    2780 + 380 = 3160    3160 + 850 = 4010    4010 + 430 = 4440    4440 + 510 = 4950    4950 + 390 = 5340    5340 + 260 = 5600    5600 + 640 = 6240    6240 + 470 = 6710    6710 + 580 = 7290    Verified total: 7290    The total ARR (in USD thousands) from Enterprise tier customers in the Top Accounts sheet is 7290.

**Ground truth:**
> Top Accounts: sum of ARR for all Enterprise tier rows = 7,600

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.67

</details>

<details><summary>Q9: How many customer accounts are based in the Asia Pacific region?</summary>

**Retrieved section:** `§5` | **Query latency:** 563 ms

**DOCNEST answer:**
> To determine the number of customer accounts based in the Asia Pacific region, we examine the "Top Accounts" table under the "Region" column and count all entries where the region is "Asia Pacific".    From the table:  - Crestwood Ltd | Pro | Asia Pacific | 120 | CloudVault | Feb 2025  - Horizon Tech | Enterprise | Asia Pacific | 410 | CloudVault, DataSync Pro | Jul 2025  - OmniRetail | Pro | Asia Pacific | 135 | SupportDesk, CloudVault | Apr 2025  - Quantum Fintech | Enterprise | Asia Pacific | 390 | SecureID | Aug 2025  - Vertex Solutions | Pro | Asia Pacific | 115 | CloudVault | Mar 2025  - Yonder Analytics | Enterprise | Asia Pacific | 310 | AnalyticsEdge | Nov 2025    List of accounts in Asia Pacific:  1. Crestwood Ltd  2. Horizon Tech  3. OmniRetail  4. Quantum Fintech  5. Vertex Solutions  6. Yonder Analytics    Count: 6 accounts    Answer: There are 6 customer accounts based in the Asia Pacific region: Crestwood Ltd, Horizon Tech, OmniRetail, Quantum Fintech, Vertex Solutions, and Yonder Analytics.

**Ground truth:**
> Top Accounts sheet: 6 accounts have Region = 'Asia Pacific'

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.83

</details>

<details><summary>Q10: Which product had the highest annual gross margin percentage in the Product Margin sheet?</summary>

**Retrieved section:** `§6` | **Query latency:** 507 ms

**DOCNEST answer:**
> The product with the highest annual gross margin percentage in the Product Margin sheet is DataSync Pro, with an Annual GM% of 75.4.

**Ground truth:**
> Product Margin sheet: DataSync Pro annual GM% = 75.4%

**Score:** 8/10 — local-judge: num=0.00 kw=1.00 phrase=0.50

</details>

<details><summary>Q11: What is the Net Revenue Retention (NRR) rate for Enterprise segment customers?</summary>

**Retrieved section:** `§7` | **Query latency:** 546 ms

**DOCNEST answer:**
> The Net Revenue Retention (NRR) rate for Enterprise segment customers is 132%.

**Ground truth:**
> Customer Segments sheet: Enterprise NRR = 132%

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.50

</details>

<details><summary>Q12: What was the total annual R&D expense and how does it compare to Sales & Marketing spend?</summary>

**Retrieved section:** `§8` | **Query latency:** 494 ms

**DOCNEST answer:**
> The total annual R&D expense was 210000.    The total annual Sales & Marketing expense was 170000.    R&D spend (210000) is higher than Sales & Marketing spend (170000).

**Ground truth:**
> Expense Detail sheet: R&D Full Year = 210,000, S&M = 170,000

**Score:** 8/10 — local-judge: num=1.00 kw=0.14 phrase=0.00

</details>

<details><summary>Q13: What was the total partnership channel revenue in 2024 and which partner type had the highest YoY growth?</summary>

**Retrieved section:** `§9` | **Query latency:** 563 ms

**DOCNEST answer:**
> The total partnership channel revenue in 2024 was 38700. The partner type with the highest YoY growth was Referral, with a YoY growth of 62.3%.

**Ground truth:**
> Partnerships sheet: Total = 38,700, Referral 62.3% YoY growth

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.57

</details>

<details><summary>Q14: How many R&D projects have Priority P0 status and how many have been completed?</summary>

**Retrieved section:** `§10` | **Query latency:** 533 ms

**DOCNEST answer:**
> - R&D projects with Priority P0 status:      1. AI Recommendation Engine      2. Zero-Trust Security Module      3. Data Residency (EU)      Total count: 3    - R&D projects that have been completed:      1. Multi-Region Failover      2. Data Residency (EU)      3. SOC 3 Certification      Total count: 3    Answer: There are 3 R&D projects with Priority P0 status, and 3 R&D projects have been completed.

**Ground truth:**
> R&D Projects sheet: 3 P0 priority projects, 3 completed

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.75

</details>

<details><summary>Q15: What is the total revenue and YoY growth percentage for the System Integrator partner type?</summary>

**Retrieved section:** `§9` | **Query latency:** 509 ms

**DOCNEST answer:**
> The total revenue for the System Integrator partner type is 9800, and the YoY growth percentage is 41.2.

**Ground truth:**
> Partnerships sheet: System Integrator — Revenue 9,800, YoY Growth% 41.2

**Score:** 8/10 — local-judge: num=0.50 kw=0.62 phrase=0.00

</details>

---

### 📝 TechVision Inc Annual Report 2024 (`DOCX`)

| | |
|---|---|
| Sections | 29 |
| Tables extracted | 12 |
| Parse time | 122 ms |
| Avg score | **7.9/10** |
| Pass rate | **86%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What was TechVision's total revenue in FY2024 and the y… | ✅ 9/10 | 528 | 3 | 893 | 2,516 | TechVision's total revenue in FY2024 was $1.24 billion, with a year-over-year gr… | Executive Summary: record revenue of $1.24 billion, 34% YoY  |
| 2 | Which business segment became the largest revenue contr… | ✅ 8/10 | 451 | 3 | 795 | 2,516 | Cloud Services became the largest revenue contributor for the first time, with F… | Section 2.1: Cloud Services $621M became largest for first t |
| 3 | What is the company's net income margin in FY2024? | ✅ 8/10 | 477 | 2 | 923 | 2,516 | The company's net income margin in FY2024 is 15.1%.… | Executive Summary: Net income $187M, 15.1% margin |
| 4 | What is the severity rating of the cybersecurity breach… | ✅ 10/10 | 433 | 2 | 814 | 2,516 | The severity rating of the cybersecurity breach risk is HIGH.… | Risk Assessment Matrix: Cybersecurity breach Severity = HIGH |
| 5 | What is TechVision's FY2025 revenue guidance range? | ⚠️ 6/10 | 572 | 2 | 878 | 2,516 | TechVision's FY2025 revenue guidance range is $1.55–1.62 billion.… | Section 6: guides for $1.55-1.62 billion, +25-31% YoY |
| 6 | What percentage of TechVision's electricity came from r… | ✅ 10/10 | 561 | 3 | 703 | 2,516 | 94% of TechVision's electricity came from renewable sources in 2024.… | ESG section: 94% of global electricity from renewable source |
| 7 | What is the estimated cost of the Zero-Trust Security S… | ✅ 7/10 | 502 | 3 | 818 | 2,516 | The estimated cost of the Zero-Trust Security Suite initiative is $32 million.… | Product Roadmap table: Zero-Trust Security Suite $32M, Q3 20 |
| 8 | What is TechVision's estimated serviceable obtainable m… | ✅ 8/10 | 541 | 3 | 749 | 2,516 | TechVision's estimated serviceable obtainable market size for enterprise cloud p… | Section 7 Market Analysis: serviceable obtainable market est |
| 9 | Which three countries are TechVision's priority interna… | ⚠️ 6/10 | 467 | 3 | 799 | 2,516 | The three priority international expansion targets for TechVision in FY2025 are … | Section 8 International Expansion: priority markets are Germ |
| 10 | What is TechVision's platform uptime and mean time to r… | ✅ 8/10 | 443 | 3 | 1,034 | 2,516 | TechVision's platform uptime in FY2024 is 99.97%, and the mean time to recover i… | Section 11 Infrastructure table: Platform Uptime 99.97%, MTT |
| 11 | What are the names and acquisition prices of the two co… | ✅ 7/10 | 531 | 3 | 803 | 2,516 | The two companies TechVision acquired in FY2024 are:  - **Prism Analytics**, wit… | Section 12 M&A table: Prism Analytics $62M Feb 2024, SecureV |
| 12 | What is TechVision's LTV:CAC ratio and how does it comp… | ✅ 8/10 | 530 | 2 | 927 | 2,516 | TechVision's LTV:CAC ratio is 5.8× in FY2024, which is an increase from 4.2× in … | Section 13 Sales Efficiency table: LTV:CAC Ratio 5.8x FY2024 |
| 13 | What is TechVision's Net Revenue Retention (NRR) rate i… | ✅ 7/10 | 484 | 3 | 1,030 | 2,516 | TechVision's Net Revenue Retention (NRR) rate in FY2024 is 128%.… | Section 14 Customer Success table: NRR 128% in FY2024 |
| 14 | How many active compliance certifications does TechVisi… | ✅ 8/10 | 431 | 3 | 623 | 2,516 | TechVision holds 6 active compliance certifications. The certification that cove… | Section 10 Compliance table: 6 certifications, PCI DSS Level |

<details><summary>Q1: What was TechVision's total revenue in FY2024 and the year-over-year growth rate?</summary>

**Retrieved section:** `§2` | **Query latency:** 528 ms

**DOCNEST answer:**
> TechVision's total revenue in FY2024 was $1.24 billion, with a year-over-year growth rate of 34%.

**Ground truth:**
> Executive Summary: record revenue of $1.24 billion, 34% YoY growth

**Score:** 9/10 — local-judge: num=1.00 kw=0.43 phrase=0.00

</details>

<details><summary>Q2: Which business segment became the largest revenue contributor for the first time?</summary>

**Retrieved section:** `§4.1` | **Query latency:** 451 ms

**DOCNEST answer:**
> Cloud Services became the largest revenue contributor for the first time, with FY2024 revenue of $621 million.

**Ground truth:**
> Section 2.1: Cloud Services $621M became largest for first time

**Score:** 8/10 — local-judge: num=0.50 kw=0.75 phrase=0.00

</details>

<details><summary>Q3: What is the company's net income margin in FY2024?</summary>

**Retrieved section:** `§3` | **Query latency:** 477 ms

**DOCNEST answer:**
> The company's net income margin in FY2024 is 15.1%.

**Ground truth:**
> Executive Summary: Net income $187M, 15.1% margin

**Score:** 8/10 — local-judge: num=0.50 kw=0.50 phrase=0.00

</details>

<details><summary>Q4: What is the severity rating of the cybersecurity breach risk?</summary>

**Retrieved section:** `§6.1` | **Query latency:** 433 ms

**DOCNEST answer:**
> The severity rating of the cybersecurity breach risk is HIGH.

**Ground truth:**
> Risk Assessment Matrix: Cybersecurity breach Severity = HIGH

**Score:** 10/10 — local-judge[text✓]: kw=0.71

</details>

<details><summary>Q5: What is TechVision's FY2025 revenue guidance range?</summary>

**Retrieved section:** `§2` | **Query latency:** 572 ms

**DOCNEST answer:**
> TechVision's FY2025 revenue guidance range is $1.55–1.62 billion.

**Ground truth:**
> Section 6: guides for $1.55-1.62 billion, +25-31% YoY

**Score:** 6/10 — local-judge: num=0.40 kw=0.25 phrase=0.00

</details>

<details><summary>Q6: What percentage of TechVision's electricity came from renewable sources in 2024?</summary>

**Retrieved section:** `§7` | **Query latency:** 561 ms

**DOCNEST answer:**
> 94% of TechVision's electricity came from renewable sources in 2024.

**Ground truth:**
> ESG section: 94% of global electricity from renewable sources

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.60

</details>

<details><summary>Q7: What is the estimated cost of the Zero-Trust Security Suite initiative?</summary>

**Retrieved section:** `§5.1` | **Query latency:** 502 ms

**DOCNEST answer:**
> The estimated cost of the Zero-Trust Security Suite initiative is $32 million.

**Ground truth:**
> Product Roadmap table: Zero-Trust Security Suite $32M, Q3 2025

**Score:** 7/10 — local-judge: num=0.50 kw=0.44 phrase=0.00

</details>

<details><summary>Q8: What is TechVision's estimated serviceable obtainable market size for enterprise cloud platforms?</summary>

**Retrieved section:** `§9` | **Query latency:** 541 ms

**DOCNEST answer:**
> TechVision's estimated serviceable obtainable market size for enterprise cloud platforms is $12 billion.

**Ground truth:**
> Section 7 Market Analysis: serviceable obtainable market estimated at $12 billion

**Score:** 8/10 — local-judge: num=0.50 kw=0.71 phrase=0.00

</details>

<details><summary>Q9: Which three countries are TechVision's priority international expansion targets for FY2025?</summary>

**Retrieved section:** `§10` | **Query latency:** 467 ms

**DOCNEST answer:**
> The three priority international expansion targets for TechVision in FY2025 are Germany, South Korea, and Australia.

**Ground truth:**
> Section 8 International Expansion: priority markets are Germany, South Korea, Australia

**Score:** 6/10 — local-judge: num=0.00 kw=0.78 phrase=0.00

</details>

<details><summary>Q10: What is TechVision's platform uptime and mean time to recover in FY2024?</summary>

**Retrieved section:** `§13.1` | **Query latency:** 443 ms

**DOCNEST answer:**
> TechVision's platform uptime in FY2024 is 99.97%, and the mean time to recover in FY2024 is 4.2 min.

**Ground truth:**
> Section 11 Infrastructure table: Platform Uptime 99.97%, MTTR 4.2 min FY2024

**Score:** 8/10 — local-judge: num=0.67 kw=0.50 phrase=0.00

</details>

<details><summary>Q11: What are the names and acquisition prices of the two companies TechVision acquired in FY2024?</summary>

**Retrieved section:** `§14` | **Query latency:** 531 ms

**DOCNEST answer:**
> The two companies TechVision acquired in FY2024 are:    - **Prism Analytics**, with an acquisition price of **$62M**  - **SecureVault Inc.**, with an acquisition price of **$32M**

**Ground truth:**
> Section 12 M&A table: Prism Analytics $62M Feb 2024, SecureVault Inc. $32M Aug 2024

**Score:** 7/10 — local-judge: num=0.40 kw=0.55 phrase=0.00

</details>

<details><summary>Q12: What is TechVision's LTV:CAC ratio and how does it compare to FY2023?</summary>

**Retrieved section:** `§15` | **Query latency:** 530 ms

**DOCNEST answer:**
> TechVision's LTV:CAC ratio is 5.8× in FY2024, which is an increase from 4.2× in FY2023. This represents a +38.1% year-over-year improvement.

**Ground truth:**
> Section 13 Sales Efficiency table: LTV:CAC Ratio 5.8x FY2024 vs 4.2x FY2023

**Score:** 8/10 — local-judge: num=0.67 kw=0.56 phrase=0.00

</details>

<details><summary>Q13: What is TechVision's Net Revenue Retention (NRR) rate in FY2024?</summary>

**Retrieved section:** `§2` | **Query latency:** 484 ms

**DOCNEST answer:**
> TechVision's Net Revenue Retention (NRR) rate in FY2024 is 128%.

**Ground truth:**
> Section 14 Customer Success table: NRR 128% in FY2024

**Score:** 7/10 — local-judge: num=0.50 kw=0.43 phrase=0.00

</details>

<details><summary>Q14: How many active compliance certifications does TechVision hold and which one covers payment processing?</summary>

**Retrieved section:** `§12` | **Query latency:** 431 ms

**DOCNEST answer:**
> TechVision holds 6 active compliance certifications. The certification that covers payment processing is PCI DSS Level 1.

**Ground truth:**
> Section 10 Compliance table: 6 certifications, PCI DSS Level 1 for Payment Processing, Trustwave

**Score:** 8/10 — local-judge: num=0.67 kw=0.70 phrase=0.00

</details>

---

### 🌐 NexusAPI v3 Developer Reference (`HTML`)

| | |
|---|---|
| Sections | 18 |
| Tables extracted | 12 |
| Parse time | 219 ms |
| Avg score | **8.9/10** |
| Pass rate | **93%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What are the rate limits and price for the Pro plan? | ✅ 10/10 | 355 | 1 | 803 | 1,387 | The Pro plan has the following rate limits and price:  - Requests per minute: 1,… | Rate Limits table: Pro plan — 1000/min, 500k/day, burst 2000 |
| 2 | How long do OAuth tokens last and how long are refresh … | ✅ 10/10 | 366 | 2 | 715 | 1,387 | OAuth tokens last for 3600 seconds (1 hour). Refresh tokens are valid for 30 day… | Authentication section: tokens expire after 3600 seconds, re |
| 3 | What HTTP method and endpoint is used to trigger AI par… | ⚠️ 5/10 | 529 | 2 | 623 | 1,387 | HTTP method: POST   Endpoint: /documents/{id}/parse… | Documents API table: POST /documents/{id}/parse — Trigger AI |
| 4 | What happens if a webhook endpoint does not respond wit… | ✅ 10/10 | 572 | 3 | 522 | 1,387 | If a webhook endpoint does not respond within 10 seconds, the delivery is retrie… | Webhooks section: respond within 10 seconds or retried up to |
| 5 | What is HTTP error code 429 in NexusAPI called, what ca… | ✅ 10/10 | 581 | 3 | 610 | 1,387 | HTTP error code 429 in NexusAPI is called "Too Many Requests". It is caused by e… | Error codes table: 429 Too Many Requests — Rate limit exceed |
| 6 | What are the SDK package names and minimum runtime requ… | ✅ 8/10 | 630 | 2 | 652 | 1,387 | For Python: - SDK package name: nexus-sdk - Minimum runtime requirement: Python … | SDK table: Python nexus-sdk 3.4.1 Python 3.9+; JavaScript @n |
| 7 | What is the base URL for NexusAPI v3 and what version i… | ✅ 7/10 | 570 | 2 | 684 | 1,387 | The base URL for NexusAPI v3 is https://api.nexus.io/v3, and the version documen… | Header: Version 3.4.2, Base URL https://api.nexus.io/v3 |
| 8 | What HTTP method and endpoint retrieves a paginated lis… | ✅ 10/10 | 622 | 2 | 634 | 1,387 | HTTP method: GET   Endpoint: /documents    This endpoint retrieves a paginated l… | Documents API table: GET /documents — List documents (pagina |
| 9 | On which plan are API keys for server-to-server communi… | ✅ 10/10 | 551 | 2 | 753 | 1,387 | API keys for server-to-server communication are available on the Pro plan and ab… | Authentication section: API keys for server-to-server commun |
| 10 | What is the daily request quota, burst limit, and month… | ✅ 7/10 | 576 | 2 | 822 | 1,387 | The daily request quota for the Enterprise plan is Unlimited, the burst limit is… | Rate Limits table: Enterprise — 10,000/min, Unlimited/day, b |
| 11 | How long is raw analytics event data retained for Pro p… | ✅ 7/10 | 588 | 2 | 758 | 1,387 | Raw analytics event data is retained for 90 days for Pro plan customers.… | Analytics section 6.1: raw events retained 90 days on Pro, a |
| 12 | What permission role is required to manage workspace us… | ✅ 10/10 | 317 | 1 | 772 | 1,387 | The permission role required to manage workspace user permissions is Workspace A… | Teams & Permissions section: minimum role to manage permissi |
| 13 | When did the NexusAPI v2 reach end-of-life, and how lon… | ✅ 10/10 | 367 | 1 | 575 | 1,387 | The NexusAPI v2 reached end-of-life on December 31, 2024. Each major version is … | Versioning section: v2 EOL Dec 31 2024; versions supported 2 |
| 14 | What are the available geographic regions for Enterpris… | ✅ 10/10 | 324 | 1 | 708 | 1,387 | Available geographic regions for Enterprise data residency: US-East, EU-West (Fr… | Compliance section: data residency regions are US-East, EU-W |

<details><summary>Q1: What are the rate limits and price for the Pro plan?</summary>

**Retrieved section:** `§1.1.2` | **Query latency:** 355 ms

**DOCNEST answer:**
> The Pro plan has the following rate limits and price:    - Requests per minute: 1,000    - Requests per day: 500,000    - Burst Limit: 2,000    - Price per month: $199

**Ground truth:**
> Rate Limits table: Pro plan — 1000/min, 500k/day, burst 2000, $199/month

**Score:** 10/10 — local-judge[fast✓]: num=0.75 kw=0.62

</details>

<details><summary>Q2: How long do OAuth tokens last and how long are refresh tokens valid?</summary>

**Retrieved section:** `§1.1` | **Query latency:** 366 ms

**DOCNEST answer:**
> OAuth tokens last for 3600 seconds (1 hour). Refresh tokens are valid for 30 days.

**Ground truth:**
> Authentication section: tokens expire after 3600 seconds, refresh valid 30 days

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.60

</details>

<details><summary>Q3: What HTTP method and endpoint is used to trigger AI parsing of a document?</summary>

**Retrieved section:** `§1.2.1` | **Query latency:** 529 ms

**DOCNEST answer:**
> HTTP method: POST    Endpoint: /documents/{id}/parse

**Ground truth:**
> Documents API table: POST /documents/{id}/parse — Trigger AI parsing, 5/min

**Score:** 5/10 — local-judge: num=0.00 kw=0.38 phrase=0.00

</details>

<details><summary>Q4: What happens if a webhook endpoint does not respond within 10 seconds?</summary>

**Retrieved section:** `§1.4` | **Query latency:** 572 ms

**DOCNEST answer:**
> If a webhook endpoint does not respond within 10 seconds, the delivery is retried up to 5 times with exponential backoff starting at 30 seconds.

**Ground truth:**
> Webhooks section: respond within 10 seconds or retried up to 5 times, backoff 30s

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.67

</details>

<details><summary>Q5: What is HTTP error code 429 in NexusAPI called, what causes it, and what is the recommended client handling strategy?</summary>

**Retrieved section:** `§1.3` | **Query latency:** 581 ms

**DOCNEST answer:**
> HTTP error code 429 in NexusAPI is called "Too Many Requests". It is caused by exceeding the rate limit. The recommended client handling strategy is to implement exponential backoff.

**Ground truth:**
> Error codes table: 429 Too Many Requests — Rate limit exceeded — Implement exponential backoff

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.77

</details>

<details><summary>Q6: What are the SDK package names and minimum runtime requirements for Python and JavaScript?</summary>

**Retrieved section:** `§1.5` | **Query latency:** 630 ms

**DOCNEST answer:**
> For Python:  - SDK package name: nexus-sdk  - Minimum runtime requirement: Python 3.9+    For JavaScript:  - SDK package name: @nexus/sdk  - Minimum runtime requirement: Node 18+

**Ground truth:**
> SDK table: Python nexus-sdk 3.4.1 Python 3.9+; JavaScript @nexus/sdk 3.4.2 Node 18+

**Score:** 8/10 — local-judge: num=0.50 kw=0.83 phrase=0.00

</details>

<details><summary>Q7: What is the base URL for NexusAPI v3 and what version is documented?</summary>

**Retrieved section:** `§1` | **Query latency:** 570 ms

**DOCNEST answer:**
> The base URL for NexusAPI v3 is https://api.nexus.io/v3, and the version documented is 3.4.2.

**Ground truth:**
> Header: Version 3.4.2, Base URL https://api.nexus.io/v3

**Score:** 7/10 — local-judge: num=0.00 kw=0.86 phrase=0.33

</details>

<details><summary>Q8: What HTTP method and endpoint retrieves a paginated list of documents?</summary>

**Retrieved section:** `§1.2.1` | **Query latency:** 622 ms

**DOCNEST answer:**
> HTTP method: GET    Endpoint: /documents      This endpoint retrieves a paginated list of documents. The "Max Results" or pagination limit is not specified in the context for this endpoint, so no numerical limit can be provided.

**Ground truth:**
> Documents API table: GET /documents — List documents (paginated)

**Score:** 10/10 — local-judge[text✓]: kw=0.67

</details>

<details><summary>Q9: On which plan are API keys for server-to-server communication available?</summary>

**Retrieved section:** `§1.1` | **Query latency:** 551 ms

**DOCNEST answer:**
> API keys for server-to-server communication are available on the Pro plan and above.

**Ground truth:**
> Authentication section: API keys for server-to-server communication available on Pro plan and above

**Score:** 10/10 — local-judge[text✓]: kw=0.80

</details>

<details><summary>Q10: What is the daily request quota, burst limit, and monthly price for the Enterprise plan?</summary>

**Retrieved section:** `§1.1.2` | **Query latency:** 576 ms

**DOCNEST answer:**
> The daily request quota for the Enterprise plan is Unlimited, the burst limit is 20,000, and the monthly price is Custom.

**Ground truth:**
> Rate Limits table: Enterprise — 10,000/min, Unlimited/day, burst 20,000, Custom pricing

**Score:** 7/10 — local-judge: num=0.50 kw=0.45 phrase=0.00

</details>

<details><summary>Q11: How long is raw analytics event data retained for Pro plan customers?</summary>

**Retrieved section:** `§1.6.1` | **Query latency:** 588 ms

**DOCNEST answer:**
> Raw analytics event data is retained for 90 days for Pro plan customers.

**Ground truth:**
> Analytics section 6.1: raw events retained 90 days on Pro, aggregated summaries 2 years

**Score:** 7/10 — local-judge: num=0.33 kw=0.50 phrase=0.00

</details>

<details><summary>Q12: What permission role is required to manage workspace user permissions?</summary>

**Retrieved section:** `§1.8` | **Query latency:** 317 ms

**DOCNEST answer:**
> The permission role required to manage workspace user permissions is Workspace Admin.

**Ground truth:**
> Teams & Permissions section: minimum role to manage permissions is Workspace Admin

**Score:** 10/10 — local-judge[text✓]: kw=0.62

</details>

<details><summary>Q13: When did the NexusAPI v2 reach end-of-life, and how long is each major version supported?</summary>

**Retrieved section:** `§1.11` | **Query latency:** 367 ms

**DOCNEST answer:**
> The NexusAPI v2 reached end-of-life on December 31, 2024. Each major version is supported for 24 months after the next major version is released.

**Ground truth:**
> Versioning section: v2 EOL Dec 31 2024; versions supported 24 months after next major release

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.50

</details>

<details><summary>Q14: What are the available geographic regions for Enterprise data residency?</summary>

**Retrieved section:** `§1.10` | **Query latency:** 324 ms

**DOCNEST answer:**
> Available geographic regions for Enterprise data residency: US-East, EU-West (Frankfurt), AP-Southeast (Singapore).

**Ground truth:**
> Compliance section: data residency regions are US-East, EU-West Frankfurt, AP-Southeast Singapore

**Score:** 10/10 — local-judge[text✓]: kw=0.80

</details>

---

### 📋 CloudMesh Technical Architecture Spec (`MD`)

| | |
|---|---|
| Sections | 29 |
| Tables extracted | 0 |
| Parse time | 5 ms |
| Avg score | **8.7/10** |
| Pass rate | **100%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What is CloudMesh's monthly data processing volume and … | ✅ 9/10 | 506 | 2 | 557 | 1,989 | CloudMesh's monthly data processing volume is **2.4 petabytes**, and the uptime … | Overview: processes 2.4 petabytes per month, 99.95% uptime S |
| 2 | What encryption standard is used for data at rest and h… | ✅ 7/10 | 363 | 2 | 467 | 1,989 | Data at rest is encrypted using **AES-256-GCM**, and keys are rotated every **90… | Section 3.1: AES-256-GCM at rest, TLS 1.3 in transit, 90-day |
| 3 | What is the RTO and RPO for Tier 1 services and what DR… | ✅ 10/10 | 441 | 2 | 676 | 1,989 | RTO for Tier 1 services is 15 min, RPO is 1 min, and the DR strategy used is Act… | Disaster Recovery table: Tier 1 — RTO 15 min, RPO 1 min, Act |
| 4 | Which compliance certification covers payment flows and… | ✅ 10/10 | 376 | 2 | 405 | 1,989 | The compliance certification that covers payment flows is PCI DSS Level 1, and t… | Compliance table: PCI DSS Level 1 — Payment flows, Coalfire  |
| 5 | What was the total annual infrastructure cost in FY2024… | ✅ 8/10 | 409 | 2 | 446 | 1,989 | The total annual infrastructure cost in FY2024 was $91.2 million. The largest ca… | Cost Structure table: Total $91.2M, Compute $38.4M is larges |
| 6 | What is the throughput and latency of the Stream Ingest… | ✅ 7/10 | 378 | 2 | 687 | 1,989 | The throughput of the Stream Ingestor component is 850 MB/s, and the latency is … | Ingestion Layer table: Stream Ingestor — Apache Kafka 3.6, 8 |
| 7 | How many countries does CloudMesh serve and how many re… | ✅ 8/10 | 385 | 2 | 488 | 1,989 | CloudMesh serves **34 countries** and runs **12 regional clusters**.… | Overview section: serving 850+ enterprise clients across 34  |
| 8 | What is the deployment frequency and mean time to deplo… | ✅ 8/10 | 349 | 2 | 607 | 1,989 | Deployment frequency: **14.3 deployments/week** average in 2024.   Mean time to … | Deployment Pipeline: 14.3 deployments/week, 8 minutes to dep |
| 9 | What is the capacity and replication factor of the Hot … | ✅ 8/10 | 372 | 2 | 658 | 1,989 | The capacity of the Hot Storage layer is 480 TB, and the replication factor is 3… | Storage Layer table: Hot Storage — Cassandra 4.1, 480 TB, 3x |
| 10 | What is the Tier 0 DR strategy and what services does i… | ✅ 8/10 | 393 | 2 | 712 | 1,989 | Tier 0 DR strategy is Active-Active. It covers the services Auth and API Gateway… | Disaster Recovery table: Tier 0 — Auth, API Gateway, RTO 5 m |
| 11 | What is the SEV-1 incident response time and resolution… | ✅ 10/10 | 328 | 2 | 519 | 1,989 | SEV-1 incident response time is 5 min, and resolution target is 30 min.… | Incident Response table: SEV-1 full platform outage — respon |
| 12 | What is the API rate limit and burst limit for the Plat… | ✅ 7/10 | 312 | 2 | 653 | 1,989 | The API rate limit for the Platinum tenant tier is Unlimited, and the burst limi… | Rate Limiting table: Platinum — Unlimited/min, burst 50,000, |
| 13 | How many active Prometheus alert rules does CloudMesh h… | ✅ 10/10 | 698 | 3 | 648 | 1,989 | CloudMesh has 1,842 active Prometheus alert rules. The log retention period in L… | Observability table: Prometheus 1,842 alert rules; Loki log  |
| 14 | What is the data retention period for billing records a… | ✅ 10/10 | 762 | 3 | 594 | 1,989 | The data retention period for billing records is 7 years, and the deletion metho… | Data Retention table: Billing records retained 7 years, Secu |
| 15 | Which NA-East regional cluster has the lowest latency b… | ✅ 10/10 | 751 | 3 | 533 | 1,989 | The NA-East regional cluster has a latency of 4ms between its primary data cente… | Regional Cluster table: NA-East us-east-1/us-east-2 latency  |

<details><summary>Q1: What is CloudMesh's monthly data processing volume and uptime SLA?</summary>

**Retrieved section:** `§1.2` | **Query latency:** 506 ms

**DOCNEST answer:**
> CloudMesh's monthly data processing volume is **2.4 petabytes**, and the uptime SLA is **99.95%**.

**Ground truth:**
> Overview: processes 2.4 petabytes per month, 99.95% uptime SLA

**Score:** 9/10 — local-judge: num=1.00 kw=0.43 phrase=0.00

</details>

<details><summary>Q2: What encryption standard is used for data at rest and how often are keys rotated?</summary>

**Retrieved section:** `§1.4.1` | **Query latency:** 363 ms

**DOCNEST answer:**
> Data at rest is encrypted using **AES-256-GCM**, and keys are rotated every **90 days**.

**Ground truth:**
> Section 3.1: AES-256-GCM at rest, TLS 1.3 in transit, 90-day key rotation

**Score:** 7/10 — local-judge: num=0.50 kw=0.40 phrase=0.00

</details>

<details><summary>Q3: What is the RTO and RPO for Tier 1 services and what DR strategy is used?</summary>

**Retrieved section:** `§1.5` | **Query latency:** 441 ms

**DOCNEST answer:**
> RTO for Tier 1 services is 15 min, RPO is 1 min, and the DR strategy used is Active-Passive.

**Ground truth:**
> Disaster Recovery table: Tier 1 — RTO 15 min, RPO 1 min, Active-Passive

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.67

</details>

<details><summary>Q4: Which compliance certification covers payment flows and who is the auditor?</summary>

**Retrieved section:** `§1.4.2` | **Query latency:** 376 ms

**DOCNEST answer:**
> The compliance certification that covers payment flows is PCI DSS Level 1, and the auditor is Coalfire.

**Ground truth:**
> Compliance table: PCI DSS Level 1 — Payment flows, Coalfire auditor

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.89

</details>

<details><summary>Q5: What was the total annual infrastructure cost in FY2024 and which category was largest?</summary>

**Retrieved section:** `§1.6` | **Query latency:** 409 ms

**DOCNEST answer:**
> The total annual infrastructure cost in FY2024 was $91.2 million. The largest category was Compute, with an annual cost of $38.4 million.

**Ground truth:**
> Cost Structure table: Total $91.2M, Compute $38.4M is largest at 42.1%

**Score:** 8/10 — local-judge: num=0.67 kw=0.67 phrase=0.00

</details>

<details><summary>Q6: What is the throughput and latency of the Stream Ingestor component?</summary>

**Retrieved section:** `§1.3.1` | **Query latency:** 378 ms

**DOCNEST answer:**
> The throughput of the Stream Ingestor component is 850 MB/s, and the latency is < 50ms.

**Ground truth:**
> Ingestion Layer table: Stream Ingestor — Apache Kafka 3.6, 850 MB/s, <50ms, 24 instances

**Score:** 7/10 — local-judge: num=0.50 kw=0.40 phrase=0.00

</details>

<details><summary>Q7: How many countries does CloudMesh serve and how many regional clusters does it run?</summary>

**Retrieved section:** `§1.2` | **Query latency:** 385 ms

**DOCNEST answer:**
> CloudMesh serves **34 countries** and runs **12 regional clusters**.

**Ground truth:**
> Overview section: serving 850+ enterprise clients across 34 countries, 12 regional clusters

**Score:** 8/10 — local-judge: num=0.67 kw=0.30 phrase=0.00

</details>

<details><summary>Q8: What is the deployment frequency and mean time to deploy?</summary>

**Retrieved section:** `§1.10.2` | **Query latency:** 349 ms

**DOCNEST answer:**
> Deployment frequency: **14.3 deployments/week** average in 2024.    Mean time to deploy: **8 minutes**.

**Ground truth:**
> Deployment Pipeline: 14.3 deployments/week, 8 minutes to deploy, <3 min rollback

**Score:** 8/10 — local-judge: num=0.67 kw=0.62 phrase=0.00

</details>

<details><summary>Q9: What is the capacity and replication factor of the Hot Storage layer?</summary>

**Retrieved section:** `§1.3.3` | **Query latency:** 372 ms

**DOCNEST answer:**
> The capacity of the Hot Storage layer is 480 TB, and the replication factor is 3x.

**Ground truth:**
> Storage Layer table: Hot Storage — Cassandra 4.1, 480 TB, 3x replication, Continuous backup

**Score:** 8/10 — local-judge: num=0.67 kw=0.56 phrase=0.00

</details>

<details><summary>Q10: What is the Tier 0 DR strategy and what services does it cover?</summary>

**Retrieved section:** `§1.5` | **Query latency:** 393 ms

**DOCNEST answer:**
> Tier 0 DR strategy is Active-Active. It covers the services Auth and API Gateway.

**Ground truth:**
> Disaster Recovery table: Tier 0 — Auth, API Gateway, RTO 5 min, RPO 0 min, Active-Active

**Score:** 8/10 — local-judge: num=0.67 kw=0.45 phrase=0.33

</details>

<details><summary>Q11: What is the SEV-1 incident response time and resolution target?</summary>

**Retrieved section:** `§1.10.2` | **Query latency:** 328 ms

**DOCNEST answer:**
> SEV-1 incident response time is 5 min, and resolution target is 30 min.

**Ground truth:**
> Incident Response table: SEV-1 full platform outage — response 5 min, resolution 30 min

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.56

</details>

<details><summary>Q12: What is the API rate limit and burst limit for the Platinum tenant tier?</summary>

**Retrieved section:** `§1.9.1` | **Query latency:** 312 ms

**DOCNEST answer:**
> The API rate limit for the Platinum tenant tier is Unlimited, and the burst limit is 50,000.

**Ground truth:**
> Rate Limiting table: Platinum — Unlimited/min, burst 50,000, 500 concurrent, P0 priority

**Score:** 7/10 — local-judge: num=0.50 kw=0.45 phrase=0.00

</details>

<details><summary>Q13: How many active Prometheus alert rules does CloudMesh have and what is the log retention period in Loki?</summary>

**Retrieved section:** `§1.8.1` | **Query latency:** 698 ms

**DOCNEST answer:**
> CloudMesh has 1,842 active Prometheus alert rules. The log retention period in Loki is 90 days.

**Ground truth:**
> Observability table: Prometheus 1,842 alert rules; Loki log retention 90 days

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.80

</details>

<details><summary>Q14: What is the data retention period for billing records and what is the deletion method?</summary>

**Retrieved section:** `§1.12.2` | **Query latency:** 762 ms

**DOCNEST answer:**
> The data retention period for billing records is 7 years, and the deletion method is Secure archive.

**Ground truth:**
> Data Retention table: Billing records retained 7 years, Secure archive, Tax compliance exception

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.58

</details>

<details><summary>Q15: Which NA-East regional cluster has the lowest latency between primary and secondary data centers?</summary>

**Retrieved section:** `§1.13.1` | **Query latency:** 751 ms

**DOCNEST answer:**
> The NA-East regional cluster has a latency of 4ms between its primary data center (us-east-1) and secondary data center (us-east-2). This is the lowest latency among the NA (North America) regional clusters.     Among the NA clusters:  - NA-East: 4ms (us-east-1 to us-east-2)  - NA-West: 12ms (us-west-2 to us-west-1)    Comparing these values: 4ms < 12ms.    Therefore, the NA-East regional cluster has the lowest latency between primary and secondary data centers, with a value of 4ms.

**Ground truth:**
> Regional Cluster table: NA-East us-east-1/us-east-2 latency 4ms (lowest)

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.86

</details>

---

### 📄 IPCC AR6 — Summary for Policymakers (`PDF`)

| | |
|---|---|
| Sections | 65 |
| Tables extracted | 3 |
| Parse time | 0 ms |
| Avg score | **9.2/10** |
| Pass rate | **100%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What is the observed increase in global surface tempera… | ✅ 9/10 | 1494 | 28 | 4,334 | 3,456 | The observed increase in global surface temperature compared to 1850–1900 is 1.0… | Global surface temperature increased by about 1.1°C (1.09°C) |
| 2 | What is the remaining global carbon budget for limiting… | ✅ 8/10 | 1213 | 13 | 5,185 | 3,456 | The remaining global carbon budget for limiting warming to 1.5°C is 500 GtCO₂ fo… | From the start of 2020, the remaining carbon budget is appro |
| 3 | What does the report say about limiting warming to 1.5°… | ✅ 10/10 | 1156 | 16 | 5,166 | 3,456 | Yes, limiting warming to 1.5°C is still achievable, but only under specific cond… | Limiting warming to 1.5°C is still achievable but requires i |
| 4 | What are the projected sea level rise ranges mentioned … | ✅ 9/10 | 839 | 12 | 5,355 | 3,456 | The projected sea level rise ranges mentioned in the report are:  - By 2050 (mid… | The IPCC projects global mean sea level rise of 0.15–0.23 m  |
| 5 | How does the report link climate change to extreme weat… | ✅ 10/10 | 303 | 13 | 2,906 | 3,456 | The report links climate change to extreme weather events in the following ways:… | Human-caused climate change has already increased the freque |

<details><summary>Q1: What is the observed increase in global surface temperature compared to 1850–1900?</summary>

**Retrieved section:** `§22` | **Query latency:** 1494 ms

**DOCNEST answer:**
> The observed increase in global surface temperature compared to 1850–1900 is 1.09 [0.95 to 1.20]°C in 2011–2020. Additionally, the observed warming to 2010–2019 is 1.06 [0.88 to 1.21]°C.

**Ground truth:**
> Global surface temperature increased by about 1.1°C (1.09°C) above the 1850–1900 baseline in the period 2011–2020. Each of the last four decades has been successively warmer than any preceding decade since 1850.

**Score:** 9/10 — local-judge: num=1.00 kw=0.27 phrase=0.00

</details>

<details><summary>Q2: What is the remaining global carbon budget for limiting warming to 1.5°C and 2°C?</summary>

**Retrieved section:** `§43` | **Query latency:** 1213 ms

**DOCNEST answer:**
> The remaining global carbon budget for limiting warming to 1.5°C is 500 GtCO₂ for a 50% likelihood, and for limiting warming to 2°C, it is 1150 GtCO₂ for a 67% likelihood.

**Ground truth:**
> From the start of 2020, the remaining carbon budget is approximately 500 GtCO2 (some estimates range 300–900 GtCO2) for limiting warming to 1.5°C with 50% likelihood, and around 1150 GtCO2 for limiting warming to 2°C with 67% likelihood. At current global emission rates of roughly 40 GtCO2/year, the 1.5°C budget could be exhausted within about a decade.

**Score:** 8/10 — local-judge: num=0.64 kw=0.31 phrase=0.00

</details>

<details><summary>Q3: What does the report say about limiting warming to 1.5°C — is it still achievable?</summary>

**Retrieved section:** `§46` | **Query latency:** 1156 ms

**DOCNEST answer:**
> Yes, limiting warming to 1.5°C is still achievable, but only under specific conditions. The report states that a small number of the most ambitious global modelled pathways limit global warming to 1.5°C (>50%) by 2100 without exceeding this level temporarily. These pathways involve rapid, deep, and in most cases immediate greenhouse gas emissions reductions in all sectors this decade (high confidence). Pathways that limit warming to 1.5°C (>50%) with no or limited overshoot reach net zero CO₂ emissions in the early 2050s, followed by net negative CO₂ emissions (high confidence).     The remaining carbon budget from the beginning of 2020 for a 50% likelihood of limiting warming to 1.5°C is 500 GtCO₂ (best estimate). However, if annual CO₂ emissions between 2020–2030 remain at 2019 levels, the cumulative emissions would almost exhaust this remaining carbon budget for 1.5°C (50%).     Global modelled pathways that limit warming to 1.5°C (>50%) with no or limited overshoot require:  - By 2030: a 43 [34–60]% reduction in GHG emissions and a 48 [36–69]% reduction in CO₂ emissions relative to 2019 levels.  - By 2050: an 84 [73–98]% reduction in GHG emissions and a 99 [79–119]% reduction in CO₂ emissions relative to 2019 levels.    The report also notes that global GHG emissions in 2030 implied by nationally determined contributions (NDCs) announced by October 2021 make it likely that warming will exceed 1.5°C during the 21st century, and there is a substantial 'emissions gap' between current NDCs and the emissions reductions required for 1.5°C.     Thus, while technically possible, achieving 1.5°C depends on immediate, rapid, and deep emissions reductions across all sectors and closing the current emissions gap.

**Ground truth:**
> Limiting warming to 1.5°C is still achievable but requires immediate, rapid and deep emissions reductions in all sectors this decade. Modelled pathways with no or limited overshoot require global GHG emissions to peak before 2025 at the latest and be reduced by about 43% by 2030 relative to 2019 levels. Delayed action makes the target progressively harder or impossible to meet.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.61

</details>

<details><summary>Q4: What are the projected sea level rise ranges mentioned in the report for mid-century and end of century?</summary>

**Retrieved section:** `§37` | **Query latency:** 839 ms

**DOCNEST answer:**
> The projected sea level rise ranges mentioned in the report are:    - By 2050 (mid-century), relative to 1995–2014:    - Under the SSP1-1.9 GHG emissions scenario: 0.15–0.23 m    - Under the SSP5-8.5 GHG emissions scenario: 0.20–0.29 m    - By 2100 (end of century), relative to 1995–2014:    - Under the SSP1-1.9 GHG emissions scenario: 0.28–0.55 m    - Under the SSP5-8.5 GHG emissions scenario: 0.63–1.01 m    These ranges are from §40 — Likelihood and Risks of Unavoidable, Irreversible or Abrupt Changes.

**Ground truth:**
> The IPCC projects global mean sea level rise of 0.15–0.23 m by 2050 and 0.28–0.55 m by 2100 under intermediate emissions scenarios. Under high-emission scenarios, sea level could rise 0.6–1.0 m by 2100. Under very high emissions, multi-metre rise beyond 2100 cannot be ruled out.

**Score:** 9/10 — local-judge: num=1.00 kw=0.35 phrase=0.00

</details>

<details><summary>Q5: How does the report link climate change to extreme weather events?</summary>

**Retrieved section:** `§35` | **Query latency:** 303 ms

**DOCNEST answer:**
> The report links climate change to extreme weather events in the following ways:    - Human-caused climate change is already affecting many weather and climate extremes in every region across the globe, leading to widespread adverse impacts and related losses and damages to nature and people (high confidence) {§23}.  - Human influence has likely increased the chance of compound extreme events since the 1950s, including increases in the frequency of concurrent heatwaves and droughts (high confidence) {§23}.  - The projected increase in frequency and intensity of heavy precipitation (high confidence) will increase rain-generated local flooding (medium confidence) {B.2.1}.  - Compound heatwaves and droughts are projected to become more frequent, including concurrent events across multiple locations (high confidence) {B.1.3}.  - In all regions, increases in extreme heat events have resulted in human mortality and morbidity (very high confidence) {A.2.5}.  - Climate and weather extremes are increasingly driving displacement in Africa, Asia, North America (high confidence), and Central and South America (medium confidence), with small island states in the Caribbean and South Pacific being disproportionately affected relative to their small population size (high confidence) {A.2.5}.  - Due to relative sea level rise, current 1-in-100 year extreme sea level events are projected to occur at least annually in more than half of all tide gauge locations by 2100 under all considered scenarios (high confidence) {B.1.3}.  - Other projected regional changes include intensification of tropical cyclones and/or extratropical storms (medium confidence), and increases in aridity and fire weather (medium to high confidence) {B.1.3}.    These statements collectively establish that climate change is already increasing the frequency, intensity, and impacts of extreme weather events globally.

**Ground truth:**
> Human-caused climate change has already increased the frequency and intensity of many extreme weather events globally. The report states it is an established fact that climate change affects heat waves, heavy rainfall and flooding, droughts, and intense tropical cyclones. Climate attribution studies can link specific extreme events to human influence on the climate system.

**Score:** 10/10 — local-judge[text✓]: kw=0.66

</details>

---

### 📄 BIS Annual Economic Report 2024 (`PDF`)

| | |
|---|---|
| Sections | 135 |
| Tables extracted | 5 |
| Parse time | 0 ms |
| Avg score | **9.6/10** |
| Pass rate | **100%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What does the BIS 2024 report say about the disinflatio… | ✅ 10/10 | 680 | 71 | 4,043 | 3,456 | The BIS 2024 report states that global inflation continued to recede from the pe… | Global inflation continued to recede from the peak it reache |
| 2 | What does the BIS 2024 report say about central bank po… | ✅ 9/10 | 570 | 50 | 3,477 | 3,456 | The BIS 2024 report states that central banks raised policy rates to **two-decad… | The BIS 2024 report describes how major central banks engage |
| 3 | What specific financial stability risks does the BIS hi… | ✅ 10/10 | 651 | 66 | 4,163 | 3,456 | The BIS highlights the following specific financial stability risks related to h… | The BIS highlights macro-financial pressure points from the  |
| 4 | What financial stability risks does the BIS identify re… | ✅ 9/10 | 653 | 60 | 3,543 | 3,456 | The BIS identifies the following financial stability risks relating to asset pri… | The BIS identifies that widespread adoption of similar AI-dr |
| 5 | What fiscal pressure points does the BIS 2024 report id… | ✅ 10/10 | 648 | 58 | 2,814 | 3,456 | The BIS 2024 report identifies the following fiscal pressure points:  1. Expansi… | The BIS 2024 report identifies fiscal pressure points includ |

<details><summary>Q1: What does the BIS 2024 report say about the disinflation process and how global inflation receded from its peak?</summary>

**Retrieved section:** `§24` | **Query latency:** 680 ms

**DOCNEST answer:**
> The BIS 2024 report states that global inflation continued to recede from the peak it reached in 2022. In the United States, the disinflation journey largely followed the forecasted path, although inflation remained a little above target by early 2024. Inflation receded towards central bank targets across a range of euro area economies and other advanced economies (AEs) and emerging market economies (EMEs).    The decline in inflation was common for both core and headline inflation, but headline inflation decreased more, especially in AEs. By early 2024, contributions to inflation from food and energy had largely disappeared in AEs and had dropped significantly in EMEs. The main inflation driver in AEs became services price growth, a more persistent component historically. Contributions to inflation from services doubled since 2021 and remained large in AEs. Similarly, in EMEs, contributions from services increased while contributions from food decreased.    In China, headline consumer price index (CPI) inflation has been close to zero since April 2023. Core CPI levels were around the same in early 2024 as two years prior, indicating weak core inflation. For iron and steel products, export volume increased by 9.4% in the year to February 2024 while prices fell 15.7%. For the automobile sector, volume increased by 27.7% while prices fell 4.4%. The nominal effective exchange rate of the Chinese yuan fell by about 6% between early 2022 and early 2024, and the real value of the yuan depreciated by 13% over the same period.    Estimates indicate that during 2022, China's exports added around 2 percentage points to the increase in import prices in its trading partners. By 2023, China’s disinflation reduced the annual rate of import price increases in other major economies by around 5 percentage points on average. A 5.8 percentage point decrease in import prices would eventually translate into a 1.5 percentage point lower CPI inflation rate on average, with sensitivity varying from 0.07 for the United States to 0.56 for Ireland, averaging 0.26 across 21 countries.    More than half of the decline in inflation from its peak reflects increased supply in the United Kingdom, the United States, South Africa, Indonesia, and Korea. Weaker demand accounted for more of the inflation decline in Canada, France, and Mexico. Monetary policy played a role by raising policy rates to two-decade highs, contributing importantly to disinflation since mid-2023. Had monetary policy tightened earlier in line with past patterns, core PCE inflation would have been around 1 percentage point lower than the actual peak of 5.6% in early 2022. A key role of monetary policy was anchoring inflation expectations, limiting second-round effects.

**Ground truth:**
> Global inflation continued to recede from the peak it reached in 2022, driven by declining commodity prices and demand normalization. The sustained disinflation opened the door to a monetary policy easing cycle, though services inflation remained elevated above central bank targets in many advanced economies, making the final leg of disinflation harder.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.54

</details>

<details><summary>Q2: What does the BIS 2024 report say about central bank policy actions taken to address high inflation?</summary>

**Retrieved section:** `§75` | **Query latency:** 570 ms

**DOCNEST answer:**
> The BIS 2024 report states that central banks raised policy rates to **two-decade highs** in response to high inflation, beginning in **2022**, after inflation flared up in **early 2021** but with a delayed policy response due to uncertainty about its persistence. These decisive policy actions illustrated central banks' commitment to **price stability** and helped to **restrain demand**, a key force that had pushed inflation higher.    The report emphasizes that **forceful monetary tightening** can prevent high inflation from becoming **entrenched**, and that central banks were quick to react and recover lost ground once they realized inflation threatened to become unmoored. The actions were crucial in **pre-empting a transition to a high-inflation regime**, where inflation dynamics become self-reinforcing.    Additionally, the report highlights the **key role of communication** and **credibility**, noting that central banks had to explain the failure to anticipate the inflation surge, manage **large forecast errors**, convey **exceptional uncertainty** without sapping confidence, and underline their **unwavering commitment to restoring price stability**.    Monetary policy also played a **critical role in anchoring inflation expectations**, with **market expectations converging to the central bank's assessments**. Without a strong response, the central bank's commitment to price stability could be called into question, risking a **much higher and more persistent inflation surge**.    The report references **Graph B1.A** and **Graph 7** as supporting evidence, and cites sources including **Mojon et al (forthcoming); Congressional Budget Office; Federal Reserve Bank of Chicago; Federal Reserve Bank of St Louis; Consensus Economics; national data; BIS**.

**Ground truth:**
> The BIS 2024 report describes how major central banks engaged in forceful monetary policy tightening, raising interest rates rapidly and significantly to combat elevated inflation. This tightening was effective: inflation receded substantially from its 2022 peak across most advanced economies by 2023-2024. The BIS notes that central banks kept policy rates at elevated, restrictive levels and that the speed and scale of the tightening was historically significant in restoring price stability.

**Score:** 9/10 — local-judge: num=1.00 kw=0.36 phrase=0.00

</details>

<details><summary>Q3: What specific financial stability risks does the BIS highlight related to high interest rates and debt in 2024?</summary>

**Retrieved section:** `§48` | **Query latency:** 651 ms

**DOCNEST answer:**
> The BIS highlights the following specific financial stability risks related to high interest rates and debt in 2024:    1. **Legacy risks for life insurance companies (ICs)** from the "low for long" interest rate era, as the surge in inflation and subsequent rise in interest rates since 2022 have exposed vulnerabilities. ICs' business models, which rely on highly rated long-term debt, were particularly exposed during the post-Great Financial Crisis period of low rates.    2. **Increased credit risk for ICs**, as rising interest rates have increased debt servicing costs. Their exposure to riskier assets—such as more risky corporate debt and securitised products (e.g., collateralised debt obligations)—had grown to **around 12% on average by 2022**, mostly from pre-rate-rise investments.    3. **Rising exposure to real estate**, a sector vulnerable to higher interest rates. This includes investments in property and real estate funds, equity and corporate bonds of real estate-related companies, and real estate loans and mortgages.    4. **Commercial real estate (CRE) market risks**, where higher interest rates have put downward pressure on prices, reduced valuations, and created losses for lenders. Vacancy rates in office CRE have risen, especially in the **United States and China**, reaching **all-time highs**.    5. **Financial stability risks from CRE lending**, including an "extend and pretend" strategy by banks avoiding crystallisation of losses, leading to **artificially high valuations and unrecognised losses**, amplifying redemption pressures and increasing the risk of a disorderly adjustment.    6. **Non-bank financial institutions (NBFIs)** have seen risks materialise, particularly in **commercial mortgage-backed securities (CMBS)**. In the United States, the decline in market returns for CRE investors has **already exceeded that of the 1990 CRE stress**.    7. **Banks’ indirect exposure to CRE** through NBFIs they lend to, although large banks are in a better position to absorb losses due to **higher capital levels and diversified business lines**.    8. **Debt refinancing risks** as maturity walls are hit, requiring households and firms to roll over debt at higher interest rates, further eroding financial buffers, especially as **pandemic support fades**.    9. **Historically high levels of private and public debt**, combined with **high debt service costs**, create macro-financial imbalances. The financial cycle in advanced economies (AEs) appears to have peaked, with credit indicators and real property prices returning to longer-term trends.    10. **Signs of stress in CRE markets** emerged in 2023, with **losses on US CRE exposures crystallising in the books of a few US regional banks and banks elsewhere**, and institutions **increasing provisions in anticipation of future losses**.    11. **Persistent high interest rates** increase the risk that borrowers—particularly those needing to refinance—will face financial strain, potentially leading to **weaker economic activity and rising loan impairment ratios** within two to three years of the first rate hike.    12. **Fiscal trajectories** pose a medium- to long-term threat to stability, as **debt-to-GDP ratios are set to climb over time**, even if interest rates remain below economic growth rates, absent consolidation measures.    These risks collectively reflect the interplay of high debt, elevated interest rates, and stretched valuations across sectors and institutions in 2024.

**Ground truth:**
> The BIS highlights macro-financial pressure points from the combination of higher interest rates and historically high public and private debt levels, stress in commercial real estate (CRE) markets, vulnerabilities in non-bank financial intermediaries (NBFIs) with liquidity mismatches, and sovereign debt sustainability concerns in emerging markets.

**Score:** 10/10 — local-judge[text✓]: kw=0.73

</details>

<details><summary>Q4: What financial stability risks does the BIS identify relating to asset price volatility, herding behavior, and concentration risk in financial markets?</summary>

**Retrieved section:** `§43` | **Query latency:** 653 ms

**DOCNEST answer:**
> The BIS identifies the following financial stability risks relating to asset price volatility, herding behavior, and concentration risk in financial markets:    - **Herding**: Identified as a financial stability challenge across all four key areas of the financial sector impacted by AI — payments, lending, insurance, and asset management. Herding is linked to network interconnectedness and procyclicality, which can amplify market swings and contribute to systemic risk.    - **Network interconnectedness and procyclicality**: Listed as a financial stability challenge in all four sectors (payments, lending, insurance, asset management), indicating that the interconnected nature of financial institutions and procyclical behavior can exacerbate asset price volatility and systemic stress.    - **Single point of failure**: Cited as a financial stability challenge across all four sectors, indicating concentration risk where reliance on specific AI systems, models, or third-party providers could lead to widespread disruption if one component fails.    - **Incorrect decisions based on short samples of non-representative data**: A risk present in all four sectors, which can lead to mispricing of assets and sudden corrections, contributing to asset price volatility.    - **Spillovers from the real sector**: Also listed universally, indicating that instability originating in the real economy (e.g., commercial real estate price declines) can transmit to financial markets, amplifying volatility.    Additionally, in the broader context:    - **Asset price volatility** is highlighted as a risk due to the potential for a correction in private equity and credit markets, which could spark broader financial stress through multiple channels.  - **Commercial real estate (CRE) price declines** of **upwards of 40%** have already occurred, increasing default risk and losses at financial intermediaries.  - The divergence between **real estate investment trusts (REITs)** and **open end diversified core equity (ODCE) funds** valuations suggests latent losses and artificially high valuations, amplifying redemption pressures and the risk of a disorderly adjustment.  - **Bond volatility** has hovered well above equity volatility — a rare occurrence — reflecting high uncertainty about the future path of interest rates and contributing to asset price instability.    Thus, the financial stability risks identified include: **herding, network interconnectedness, procyclicality, single point of failure, incorrect decisions from non-representative data, spillovers from the real sector, asset price corrections (especially in CRE with price declines upwards of 40%), valuation divergences (REITs vs ODCE funds), and elevated bond volatility relative to equity volatility**.

**Ground truth:**
> The BIS identifies that widespread adoption of similar AI-driven trading models can induce herding behavior and correlated portfolio adjustments, amplifying asset price volatility. Concentration risk arises from dependence on a small number of large technology providers for AI infrastructure, creating systemic single-points of failure.

**Score:** 9/10 — local-judge[text~]: kw=0.48

</details>

<details><summary>Q5: What fiscal pressure points does the BIS 2024 report identify, and what fiscal policy stance does it recommend?</summary>

**Retrieved section:** `§46` | **Query latency:** 648 ms

**DOCNEST answer:**
> The BIS 2024 report identifies the following fiscal pressure points:    1. Expansionary fiscal policies could over-stimulate demand and complicate the disinflation task during the last mile.  2. Fiscal sustainability concerns could create headwinds through higher risk premia and financial market dysfunction.  3. Debt trajectories are a major concern globally going forward (as shown in Graph 16.A).  4. The environment of higher interest rates weakens fiscal positions already stretched by historically high debt levels.  5. The support from the negative gap between real interest rates and growth rates (r–g) has shrunk in recent years, is projected to stay much smaller going forward, and could even turn positive (as shown in Graph 16.B, blue line).  6. Rising public spending in the coming years (as shown in Graph 16.B, red line) due to needs from the green transition, pensions and healthcare, and defence further curbs fiscal space.  7. Although financial market pricing points to only a small likelihood of public finance stress at present (as shown in Graph 16.C), confidence could quickly crumble if economic momentum weakens and an urgent need for public spending arises on both structural and cyclical fronts.  8. In some cases, fiscal policy is still adding stimulus to the economy, acting at cross-purposes with monetary policy.  9. Demands on fiscal authorities have been increasing due to financing needs of the green transition, geopolitical considerations, and the looming burden of ageing populations.  10. Further broad-based fiscal support has darkened the fiscal outlook since last year’s Annual Economic Report.    The report recommends the following fiscal policy stance:    - Fiscal consolidation is an absolute priority in the near term. This would help relieve pressure on inflation, lessen the need to keep interest rates high, and help preserve financial stability.

**Ground truth:**
> The BIS 2024 report identifies fiscal pressure points including expansionary fiscal policies that could become a source of tension with monetary policy objectives. The report recommends fiscal consolidation as an absolute priority to rebuild near-term policy space and reduce macro-financial pressure. Greater public spending demands with dwindling fiscal space pose a key risk.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.65

</details>

---

### 📄 GPT-3 Paper — Language Models are Few-Shot Learners (`PDF`)

| | |
|---|---|
| Sections | 40 |
| Tables extracted | 0 |
| Parse time | 0 ms |
| Avg score | **7.2/10** |
| Pass rate | **80%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What are ALL the parameter sizes of GPT-3 models presen… | ✅ 10/10 | 614 | 31 | 10,937 | 3,456 | The GPT-3 models presented in the paper have the following parameter sizes, list… | The largest GPT-3 model has 175 billion parameters. The pape |
| 2 | What are the training corpora (Common Crawl, WebText2, … | ✅ 8/10 | 604 | 49 | 9,385 | 3,456 | The training corpora used for GPT-3 and their respective dataset weights are:  -… | GPT-3 is trained on: filtered Common Crawl (410B tokens, 60% |
| 3 | How does GPT-3's architecture compare to GPT-2? What ar… | ❌ 0/10 | 577 | 40 | 9,957 | 3,456 | Not found in context… | GPT-3 uses the same Transformer decoder architecture as GPT- |
| 4 | How many in-context examples are used in GPT-3's zero-s… | ✅ 8/10 | 433 | 28 | 9,170 | 3,456 | - Zero-shot: 0 in-context examples   - One-shot: 1 in-context example   - Few-sh… | Zero-shot uses 0 demonstrations (task description only); one |
| 5 | What limitations and risks does the GPT-3 paper acknowl… | ✅ 10/10 | 378 | 42 | 7,188 | 3,456 | The GPT-3 paper acknowledges the following limitations and risks:  1. **Text Syn… | The GPT-3 paper acknowledges limitations including poor samp |

<details><summary>Q1: What are ALL the parameter sizes of GPT-3 models presented in the paper? List every model variant explicitly from smallest to largest.</summary>

**Retrieved section:** `§2.23` | **Query latency:** 614 ms

**DOCNEST answer:**
> The GPT-3 models presented in the paper have the following parameter sizes, listed from smallest to largest:    125M, 350M, 760M, 1.3B, 2.7B, 6.7B, 13B, 175B.

**Ground truth:**
> The largest GPT-3 model has 175 billion parameters. The paper also presents smaller variants with 125M, 350M, 760M, 1.3B, 2.7B, 6.7B, and 13B parameters.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.47

</details>

<details><summary>Q2: What are the training corpora (Common Crawl, WebText2, Books, Wikipedia) used for GPT-3 and what are the dataset weights?</summary>

**Retrieved section:** `§2.23` | **Query latency:** 604 ms

**DOCNEST answer:**
> The training corpora used for GPT-3 and their respective dataset weights are:    - Common Crawl (filtered): 60%  - WebText2: 22%  - Books1: 8%  - Books2: 8%  - Wikipedia: 3%

**Ground truth:**
> GPT-3 is trained on: filtered Common Crawl (410B tokens, 60% weight), WebText2 (19B tokens, 22% weight), Books1 (12B tokens, 8% weight), Books2 (55B tokens, 8% weight), and Wikipedia (3B tokens, 3% weight). Training runs for ~300B tokens total with sampling proportional to weights.

**Score:** 8/10 — local-judge: num=0.58 kw=0.45 phrase=0.00

</details>

<details><summary>Q3: How does GPT-3's architecture compare to GPT-2? What are the number of layers, attention heads, d_model, context window, and batch size for the largest GPT-3 model (175B)?</summary>

**Retrieved section:** `§2.11` | **Query latency:** 577 ms

**DOCNEST answer:**
> Not found in context

**Ground truth:**
> GPT-3 uses the same Transformer decoder architecture as GPT-2 but at vastly larger scale. The largest GPT-3 model (175B parameters) has 96 transformer layers, 96 attention heads, and a model dimension (d_model) of 12288. It uses a context window of 2048 tokens and a batch size of 3.2 million tokens. GPT-3 also uses alternating dense and locally banded sparse attention in the layers, following the Sparse Transformer design.

**Score:** 0/10 — retrieval-miss: 'not found in context'

</details>

<details><summary>Q4: How many in-context examples are used in GPT-3's zero-shot, one-shot, and few-shot evaluation modes?</summary>

**Retrieved section:** `§2.17` | **Query latency:** 433 ms

**DOCNEST answer:**
> - Zero-shot: 0 in-context examples    - One-shot: 1 in-context example    - Few-shot: Typically in the range of 10 to 100 in-context examples, with 32 examples used for all tasks in the few-shot setting as specified in the evaluation.

**Ground truth:**
> Zero-shot uses 0 demonstrations (task description only); one-shot uses exactly 1 example; few-shot uses as many examples as fit in the 2048-token context window, typically 10–100 examples depending on task prompt length.

**Score:** 8/10 — local-judge: num=0.80 kw=0.39 phrase=0.00

</details>

<details><summary>Q5: What limitations and risks does the GPT-3 paper acknowledge?</summary>

**Retrieved section:** `§2.11` | **Query latency:** 378 ms

**DOCNEST answer:**
> The GPT-3 paper acknowledges the following limitations and risks:    1. **Text Synthesis Weaknesses**: GPT-3 samples sometimes repeat themselves semantically at the document level, lose coherence over long passages, contradict themselves, and contain non-sequitur sentences or paragraphs.    2. **Difficulty with Specific Questions**: GPT-3 has difficulty with questions like “If I put cheese into the fridge, will it melt?”    3. **Poor Few-Shot Performance on Certain Tasks**:     - Performs little better than chance in one-shot or few-shot evaluation on:       - WIC (determining if two words are used the same way in a sentence)       - ANLI (determining if one sentence implies another)       - Several reading comprehension tasks    4. **Structural and Algorithmic Limitations**:     - Lack of bidirectionality; making bidirectional models work with few- or zero-shot learning is suggested as a future direction.    5. **Limits of the Pretraining Objective**:     - The current objective weights every token equally and lacks a notion of what is more or less important to predict.     - It is unclear what humans learn from scratch vs. from prior demonstrations.    6. **Inference Cost and Inconvenience**:     - Models at the scale of GPT-3 are expensive and inconvenient to perform inference on, challenging practical applicability.    7. **General Deep Learning Limitations**:     - Decisions are not easily interpretable.     - Not well-calibrated in predictions on novel inputs, with much higher variance in performance than humans on standard benchmarks.     - Retains biases of the training data.    8. **Bias in Generated Content**:     - Generates stereotyped or prejudiced content due to data biases, which is of special concern from a societal perspective.     - Gender bias: 83% of the 388 occupations tested were more likely to be followed by a male identifier.     - Racial bias: The model generates associations reflecting societal biases when prompted with race-related terms.     - Religious bias: For Islam, words like “terrorism”, “violent”, and “terrorist” co-occur at higher rates; Table 6.2 lists the ten most favored descriptive words for each religion in GPT-3 175B, including:       - Atheism: ‘Theists’, ‘Cool’, ‘Agnostics’, ‘Mad’, ‘Theism’, ‘Defensive’, ‘Complaining’, ‘Correct’, ‘Arrogant’, ‘Characterized’       - Buddhism: ‘Myanmar’, ‘Vegetarians’, ‘Burma’, ‘Fellowship’, ‘Monk’, ‘Japanese’, ‘Reluctant’, ‘Wisdom’, ‘Enlightenment’, ‘Non-Violent’       - Christianity: ‘Attend’, ‘Ignorant’, ‘Response’, ‘Judgmental’, ‘Grace’, ‘Execution’, ‘Egypt’, ‘Continue’, ‘Comments’, ‘Officially’       - Hinduism: ‘Caste’, ‘Cows’, ‘BJP’, ‘Kashmir’, ‘Modi’, ‘Celebrated’, ‘Dharma’, ‘Pakistani’, ‘Originated’, ‘Africa’       - Islam: ‘Pillars’, ‘Terrorism’, ‘Fasting’, ‘Sheikh’, ‘Non-Muslim’, ‘Source’, ‘Charities’, ‘Levant’, ‘Allah’, ‘Prophet’       - Judaism: ‘Gentiles’, ‘Race’, ‘Semites’, ‘Whites’, ‘Blacks’, ‘Smartest’, ‘Racists’, ‘Arabs’, ‘Game’, ‘Russian’    9. **Potential for Misuse**:     - GPT-3 improves text generation quality and adaptability, increasing difficulty in distinguishing synthetic from human text.     - Concerning milestone: people find it difficult to distinguish GPT-3-generated synthetic news articles from real ones (as shown in Section 3.9.4).     - Potential for deliberate misuse in generating misinformation, malware distribution, and computer fraud.     - Monitoring of forums and chat groups revealed significant discussion of misuse after GPT-2 release in spring 2019, but fewer instances of experimentation and no successful deployments since then.     - Outputs are stochastic, but developers can constrain them (e.g., via filtering or steering).     - AI researchers may eventually develop models sufficiently consistent and steerable to attract malicious actors.    10. **Energy Usage and Environmental Impact**:      - Training GPT-3 175B consumed several thousand petaflop/s-days of compute, compared to tens of petaflop/s-days for a 1.5B parameter GPT-2 model.      - Despite high training cost, inference is relatively efficient: generating 100 pages of content costs about 0.4 kW-hr (a few cents in energy).    11. **Data Contamination and Memorization Risks**:      - Potential contamination found in

**Ground truth:**
> The GPT-3 paper acknowledges limitations including poor sample efficiency compared to humans, weakness on fine-grained tasks such as arithmetic and novel word use, and potential for harmful bias in generated text (e.g. gender, race stereotypes). It warns of misuse risks including generating disinformation at scale. The paper notes that GPT-3 still has interpretability limitations despite its few-shot capabilities.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.57

</details>

---

### 📄 Attention Is All You Need — Transformer Paper (`PDF`)

| | |
|---|---|
| Sections | 27 |
| Tables extracted | 0 |
| Parse time | 0 ms |
| Avg score | **8.6/10** |
| Pass rate | **100%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | How many attention heads does the Transformer base mode… | ✅ 8/10 | 61 | 7 | 4,062 | 3,368 | The Transformer base model uses **8 attention heads**, and it has **6 encoder la… | The Transformer base model uses h=8 parallel attention heads |
| 2 | What EN-DE BLEU scores do the Transformer base and big … | ✅ 10/10 | 65 | 5 | 3,862 | 3,456 | The Transformer base model achieves an EN-DE BLEU score of 27.3 on WMT 2014 Engl… | Transformer base achieves 27.3 BLEU and Transformer big achi |
| 3 | What training data and hardware were used to train the … | ✅ 8/10 | 85 | 6 | 4,062 | 3,368 | Training data: The standard WMT 2014 English-German dataset consisting of about … | The Transformer's primary training used WMT 2014 English-Ger |
| 4 | What are the per-layer computational complexities of se… | ✅ 10/10 | 65 | 7 | 4,112 | 3,368 | The per-layer computational complexity of self-attention is $ O(n^2 \cdot d) $, … | Self-Attention: O(n²·d) per layer, O(1) sequential operation |
| 5 | What regularization techniques are applied during Trans… | ✅ 7/10 | 91 | 9 | 3,919 | 3,368 | The regularization techniques applied during Transformer training according to t… | Two main regularization techniques: (1) Residual Dropout wit |

<details><summary>Q1: How many attention heads does the Transformer base model use, and how many encoder/decoder layers does it have?</summary>

**Retrieved section:** `§5.6` | **Query latency:** 61 ms

**DOCNEST answer:**
> The Transformer base model uses **8 attention heads**, and it has **6 encoder layers** and **6 decoder layers**.

**Ground truth:**
> The Transformer base model uses h=8 parallel attention heads and has 6 encoder layers and 6 decoder layers. The big model uses h=16 heads. The base model has d_model=512, d_k=d_v=64.

**Score:** 8/10 — local-judge: num=0.50 kw=0.75 phrase=0.00

</details>

<details><summary>Q2: What EN-DE BLEU scores do the Transformer base and big models achieve on WMT 2014 English-to-German translation?</summary>

**Retrieved section:** `§5.10` | **Query latency:** 65 ms

**DOCNEST answer:**
> The Transformer base model achieves an EN-DE BLEU score of 27.3 on WMT 2014 English-to-German translation.    The Transformer big model achieves an EN-DE BLEU score of 28.4 on WMT 2014 English-to-German translation.

**Ground truth:**
> Transformer base achieves 27.3 BLEU and Transformer big achieves 28.4 BLEU on WMT 2014 EN-DE, surpassing all previously reported models including ensembles. Transformer big also achieves 41.0 BLEU on EN-FR.

**Score:** 10/10 — local-judge[fast✓]: num=0.75 kw=0.47

</details>

<details><summary>Q3: What training data and hardware were used to train the Transformer models, and how long did training take?</summary>

**Retrieved section:** `§5.10` | **Query latency:** 85 ms

**DOCNEST answer:**
> Training data: The standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs.    Hardware: One machine with 8 NVIDIA P100 GPUs.    Training time:   - For the big models: 300,000 steps, which took 3.5 days.  - For translation tasks, the model could be trained to achieve state-of-the-art results after as little as twelve hours on eight P100 GPUs.

**Ground truth:**
> The Transformer's primary training used WMT 2014 English-German and English-French translation datasets with byte-pair encoding on 8 NVIDIA P100 GPUs (~12 hours for the base model, ~3.5 days for the big model). The paper also tests the Transformer on English constituency parsing using the Penn Treebank WSJ dataset (about 40K training sentences), showing the architecture generalizes beyond machine translation.

**Score:** 8/10 — local-judge: num=0.60 kw=0.40 phrase=0.00

</details>

<details><summary>Q4: What are the per-layer computational complexities of self-attention and recurrent layers (from Table 1), and under what condition is self-attention more efficient?</summary>

**Retrieved section:** `§5.8` | **Query latency:** 65 ms

**DOCNEST answer:**
> The per-layer computational complexity of self-attention is $ O(n^2 \cdot d) $, and the per-layer computational complexity of recurrent layers is $ O(n \cdot d^2) $, as stated in Table 1.    Self-attention is more computationally efficient than recurrent layers when the sequence length $ n $ is smaller than the representation dimensionality $ d $. This condition is commonly satisfied in sentence representations used by state-of-the-art machine translation models, such as those using word-piece or byte-pair encoding.

**Ground truth:**
> Self-Attention: O(n²·d) per layer, O(1) sequential operations. Recurrent (RNN): O(n·d²) per layer, O(n) sequential operations. Self-attention is more computationally efficient than recurrent layers when sequence length n is smaller than representation dimensionality d.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.84

</details>

<details><summary>Q5: What regularization techniques are applied during Transformer training according to the method description? What is the standard dropout rate (P_drop) described in the training procedure section?</summary>

**Retrieved section:** `§5.10` | **Query latency:** 91 ms

**DOCNEST answer:**
> The regularization techniques applied during Transformer training according to the method description are:    1. Residual Dropout    2. Label Smoothing    3. (Implicitly) Learning rate scheduling (via warmup steps and inverse square root decay), though not explicitly listed as a regularization technique, is part of the training regime.    Specifically stated in the text:    "We employ three types of regularization during training:" followed by descriptions of **Residual Dropout** and **Label Smoothing**. Although the third type is not explicitly named in the list, the context confirms these two as explicit components.    The standard dropout rate (P_drop) described in the training procedure section for the base model is **P_drop = 0**.    This is stated in the section [§5.4 — Regularization]:    "For the base model, we use a rate of P_drop = 0."    Additionally, label smoothing uses a value of **ϵ_ls = 0**.    Thus, the standard dropout rate is **0**.

**Ground truth:**
> Two main regularization techniques: (1) Residual Dropout with P_drop=0.1 applied to the output of each sub-layer before adding to the residual, and also to the sums of embeddings and positional encodings; (2) Label Smoothing with ε_ls=0.1 during training, which hurts perplexity but improves accuracy and BLEU score.

**Score:** 7/10 — local-judge: num=0.50 kw=0.37 phrase=0.00

</details>

---

### 📄 Llama 2 — Open Foundation and Fine-Tuned Chat Models (`PDF`)

| | |
|---|---|
| Sections | 21 |
| Tables extracted | 0 |
| Parse time | 0 ms |
| Avg score | **9.0/10** |
| Pass rate | **100%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What are ALL the parameter sizes of the Llama 2 model f… | ✅ 9/10 | 215 | 30 | 9,576 | 3,456 | The parameter sizes of the Llama 2 model family are 7B, 13B, 34B, and 70B.  - Th… | Llama 2 comes in 7B, 13B, 34B, and 70B parameter sizes. Chat |
| 2 | How does Llama 2-Chat 70B compare to ChatGPT (GPT-3.5) … | ✅ 8/10 | 188 | 30 | 9,991 | 3,456 | Llama 2-Chat 70B has a win rate of 36% and a tie rate of 31.5% relative to ChatG… | On human preference evaluations, Llama 2-Chat 70B is statist |
| 3 | What context length do Llama 2 models support, and how … | ✅ 9/10 | 240 | 25 | 8,653 | 3,456 | Llama 2 models support a context length of 4096 tokens. This was doubled from Ll… | Llama 2 supports a context length of 4096 tokens, double Lla |
| 4 | How were the reward models for Llama 2-Chat RLHF traine… | ✅ 10/10 | 269 | 24 | 9,429 | 3,456 | The reward models for Llama 2-Chat RLHF were trained using human preference data… | Two separate reward models were trained for Llama 2-Chat: a  |
| 5 | What is RLHF Ghost Attention (GAtt) and what problem do… | ✅ 9/10 | 219 | 31 | 9,239 | 3,456 | RLHF Ghost Attention (GAtt) is a technique proposed to help control dialogue flo… | Ghost Attention (GAtt) is a fine-tuning technique that hacks |

<details><summary>Q1: What are ALL the parameter sizes of the Llama 2 model family? List every size explicitly, including any that are evaluated less extensively.</summary>

**Retrieved section:** `§2.7` | **Query latency:** 215 ms

**DOCNEST answer:**
> The parameter sizes of the Llama 2 model family are 7B, 13B, 34B, and 70B.    - The document explicitly states in §2.3: "We are releasing variants of Llama 2 with 7B, 13B, and 70B parameters."  - Additionally, in §2.5: "For the Falcon models, Llama 2 7B and 34B outperform Falcon 7B and 40B models on all categories of benchmarks." This confirms the existence of a 34B parameter variant.  - Furthermore, §2.3 notes: "We are delaying the release of the 34B model due to a lack of time to sufficiently red team," confirming that the 34B model is part of the family, even if not immediately released.    Thus, all parameter sizes in the Llama 2 model family are: 7B, 13B, 34B, and 70B.

**Ground truth:**
> Llama 2 comes in 7B, 13B, 34B, and 70B parameter sizes. Chat variants (Llama 2-Chat) are fine-tuned versions optimized for dialogue using RLHF. The 34B model is included in the release but evaluated less extensively than 7B, 13B, and 70B.

**Score:** 9/10 — local-judge: num=1.00 kw=0.38 phrase=0.00

</details>

<details><summary>Q2: How does Llama 2-Chat 70B compare to ChatGPT (GPT-3.5) on human preference evaluations?</summary>

**Retrieved section:** `§2.7` | **Query latency:** 188 ms

**DOCNEST answer:**
> Llama 2-Chat 70B has a win rate of 36% and a tie rate of 31.5% relative to ChatGPT (gpt-3.5-turbo-0301). On human evaluations across ~4,000 helpfulness prompts with three raters per prompt, Llama 2-Chat 70B is competitive with ChatGPT. The evaluation shows that Llama 2-Chat 70B outperforms ChatGPT on factual questions, while ChatGPT outperforms Llama 2-Chat 70B on language assistance. When system prompts are removed for ChatGPT in evaluation, the win rate for Llama 2-Chat 70B increases from 36% to 44%.

**Ground truth:**
> On human preference evaluations, Llama 2-Chat 70B is statistically competitive with ChatGPT (GPT-3.5-turbo), with win rates within the margin of error on both helpfulness and safety axes. ChatGPT scores slightly higher on MT-bench (7.81 vs approximately 6.27 for Llama 2-Chat 70B).

**Score:** 8/10 — local-judge: num=0.71 kw=0.44 phrase=0.00

</details>

<details><summary>Q3: What context length do Llama 2 models support, and how was it doubled from Llama 1?</summary>

**Retrieved section:** `§2.5` | **Query latency:** 240 ms

**DOCNEST answer:**
> Llama 2 models support a context length of 4096 tokens. This was doubled from Llama 1, which had a context length of 2048 tokens.

**Ground truth:**
> Llama 2 supports a context length of 4096 tokens, double Llama 1's 2048 tokens. The context length was increased by training on longer sequences, allowing Llama 2 to handle significantly longer documents and multi-turn conversations compared to Llama 1.

**Score:** 9/10 — local-judge: num=1.00 kw=0.30 phrase=0.00

</details>

<details><summary>Q4: How were the reward models for Llama 2-Chat RLHF trained, and how many human preference annotations were collected?</summary>

**Retrieved section:** `§2.7` | **Query latency:** 269 ms

**DOCNEST answer:**
> The reward models for Llama 2-Chat RLHF were trained using human preference data collected in batches on a weekly basis. The data included both open-source and internally collected human preference data, converted into a binary ranking label format (chosen and rejected), with the chosen response enforced to have a higher score than the rejected one. The reward models were initialized from pretrained chat model checkpoints. Two separate reward models were trained—one for helpfulness and one for safety—to address the tension between these objectives.    In total, 14 batches of human preference data were collected, consisting of over 1 million binary model generation comparisons. Each binary comparison contains 2 responses (chosen and rejected) sharing the same prompt and previous dialogue. On each batch, 1000 examples were held out as a test set.

**Ground truth:**
> Two separate reward models were trained for Llama 2-Chat: a helpfulness reward model and a safety reward model. Meta collected over 1 million human preference annotations by presenting annotators with pairs of model responses and asking them to choose the better one based on helpfulness and safety criteria. The reward models were trained iteratively, with newer annotation batches from improved model versions added over time to keep the reward model up to date.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.47

</details>

<details><summary>Q5: What is RLHF Ghost Attention (GAtt) and what problem does it solve in Llama 2-Chat?</summary>

**Retrieved section:** `§2.7` | **Query latency:** 219 ms

**DOCNEST answer:**
> RLHF Ghost Attention (GAtt) is a technique proposed to help control dialogue flow over multiple turns in Llama 2-Chat. It solves the problem of the model's inability to maintain attention to system messages and defined attributes (e.g., role-playing instructions like "Act as Oscar Wilde" or constraints like "Give short answers") beyond a few dialogue turns. Without GAtt, Llama 2-Chat without the technique can refer to attributes 100% at turn t+1, drops to 10% at turn t+3, and 0% by turn t+4 and beyond. With GAtt, Llama 2-Chat maintains 100% accuracy in referring to the defined attributes for up to 20 turns, as verified in human evaluation (Table 30). GAtt works by hacking the fine-tuning data to help the attention focus in a multi-stage process, inspired by Context Distillation (Bai et al., 2022b). It was applied after RLHF V3 and enables the model to maintain large attention activations with respect to the system message for a larger portion of the dialogue, as shown in Figure 10.

**Ground truth:**
> Ghost Attention (GAtt) is a fine-tuning technique that hacks training data by appending the system prompt to every user message in the conversation, forcing the model to attend to initial instructions across all turns. It solves the problem of models forgetting their system prompt constraints after several conversation turns in multi-turn dialogue.

**Score:** 9/10 — local-judge[text~]: kw=0.54

</details>

---

### 📄 Constitutional AI — Harmlessness from AI Feedback (`PDF`)

| | |
|---|---|
| Sections | 123 |
| Tables extracted | 0 |
| Parse time | 0 ms |
| Avg score | **8.6/10** |
| Pass rate | **80%** |

| # | Question | Score | DocNest ms | Trad ms | DocNest Tok | Trad Tok | DocNest Answer | Expected / Baseline |
|---|----------|-------|------------|---------|-------------|----------|----------------|---------------------|
| 1 | What is the core idea behind Constitutional AI and what… | ✅ 9/10 | 316 | 16 | 1,566 | 3,456 | The core idea behind Constitutional AI is that human supervision comes entirely … | Constitutional AI trains a harmless AI using a small set of  |
| 2 | What two training phases make up the Constitutional AI … | ✅ 10/10 | 261 | 21 | 2,039 | 3,456 | The two training phases that make up the Constitutional AI method are:   (1) a s… | Phase 1 (SL-CAI): supervised learning where a model critique |
| 3 | How does the paper evaluate harmlessness vs helpfulness… | ✅ 10/10 | 269 | 15 | 2,307 | 3,456 | The paper evaluates harmlessness and helpfulness by calculating Elo scores based… | Evaluation uses crowdworker Elo scores comparing model outpu |
| 4 | What is the 'critique and revision' step in Constitutio… | ⚠️ 5/10 | 300 | 20 | 1,382 | 3,456 | The 'critique and revision' step in Constitutional AI involves using a helpful R… | In the SL-CAI phase, the model is prompted to critique its i |
| 5 | What does the Constitutional AI paper show about whethe… | ✅ 9/10 | 339 | 15 | 1,922 | 3,456 | The Constitutional AI paper shows that AI-generated harmlessness labels can repl… | The paper demonstrates that AI-generated preference labels ( |

<details><summary>Q1: What is the core idea behind Constitutional AI and what problem does it solve vs standard RLHF?</summary>

**Retrieved section:** `§23` | **Query latency:** 316 ms

**DOCNEST answer:**
> The core idea behind Constitutional AI is that human supervision comes entirely from a set of principles that should govern AI behavior, along with a small number of examples used for few-shot prompting, forming a "constitution" to steer the model’s behavior. The training process has two stages: a supervised learning phase that gets the model "on-distribution," followed by a reinforcement learning (RL) stage that refines performance. In the RL stage, human preferences for harmlessness in standard RLHF are replaced with AI feedback (RLAIF), where the AI evaluates responses according to constitutional principles via a multiple choice format, generating self-supervised preference labels for harmlessness.    This approach solves the problem of the lack of transparency and scalability in standard RLHF, which typically uses at least tens of thousands of human feedback labels that are often private and difficult to interpret collectively. Constitutional AI improves transparency by encoding training goals in a simple list of natural language principles, using chain-of-thought reasoning to make AI decision-making explicit, and reducing reliance on large amounts of private human feedback. It specifically eliminates the need for human feedback labels for harmlessness, as demonstrated in training helpful and harmless (HH) models without any human feedback labels for harmlessness, as defined in [Askell et al., 2021, Bai et al., 2022].

**Ground truth:**
> Constitutional AI trains a harmless AI using a small set of written principles (the 'constitution') rather than large-scale human-labeled harmlessness data. The AI critiques and revises its own outputs based on these principles. This solves the bottleneck and inconsistency of human safety labeling in standard RLHF.

**Score:** 9/10 — local-judge[text~]: kw=0.45

</details>

<details><summary>Q2: What two training phases make up the Constitutional AI method (SL-CAI and RLHF-CAI)?</summary>

**Retrieved section:** `§23` | **Query latency:** 261 ms

**DOCNEST answer:**
> The two training phases that make up the Constitutional AI method are:    (1) a supervised learning phase (SL-CAI), in which the model is finetuned on revised responses generated through self-critique and revision based on constitutional principles, and    (2) a reinforcement learning phase (RL-CAI), in which the model is further trained using a preference model trained on model-generated AI feedback (RL from AI Feedback, or RLAIF), without human labels for harmlessness.

**Ground truth:**
> Phase 1 (SL-CAI): supervised learning where a model critiques its own harmful responses using constitutional principles, revises them, then fine-tunes on the revised responses. Phase 2 (RLHF-CAI): a preference model is trained using AI-generated comparison labels (not human labels), then the policy is fine-tuned via RL against this preference model.

**Score:** 10/10 — local-judge[fast✓]: num=1.00 kw=0.48

</details>

<details><summary>Q3: How does the paper evaluate harmlessness vs helpfulness, and what does the Elo ranking show?</summary>

**Retrieved section:** `§40` | **Query latency:** 269 ms

**DOCNEST answer:**
> The paper evaluates harmlessness and helpfulness by calculating Elo scores based on crowdworker preferences expressed during model comparison tests, following the same procedure as in [Bai et al., 2022]. Each conversation is unique, with the crowdworker writing the human side; at each step, two responses from different models are compared and a preference label is collected. These conversations are distinct from but similar in distribution to those in the PM and RL training data.    A total of 10,274 helpfulness and 8,135 harmlessness comparisons were collected for AB testing the 24 snapshots shown in Figures 2 and 3. The RLHF models include two types: (1) models trained on only helpfulness data, and (2) models trained on both helpfulness and harmlessness. The RL-CAI (i.e., RLAIF) models are also evaluated.    The Elo ranking shows that:  - In Figure 2, harmlessness versus helpfulness Elo scores are plotted for all 52B RL runs, with points further to the right representing later steps in RL training. The Helpful and HH RLHF models exhibit a tradeoff between helpfulness and harmlessness. RL-CAI models trained with AI feedback learn to be less harmful at a given level of helpfulness.  - Crowdworkers were instructed to prefer less evasive responses when both were equally harmless, which explains why the harmlessness scores for Helpful and HH RLHF models are closer together compared to [Bai et al., 2022].  - In Figure 3, Elo scores are shown for models of varying sizes (including 7B, 13B, 25B, 52B parameters), with SL-CAI, RL-CAI, and RL-CAI w/ CoT models trained using the constitutional AI method.  - RL-CAI models are significantly more harmless than RLHF and SL-CAI models. In terms of helpfulness, RL-CAI with CoT is slightly less helpful but slightly more harmless compared to RL-CAI without CoT.  - In Figure 8, helpfulness and harmlessness Elo scores are plotted as a function of the total number of RL training sequences. The initial snapshot for RL-CAI models is SL-CAI (with Elos set to zero), while for RLHF models it is a pre-trained LM.    The evaluations confirm that RL-CAI models perform very well on harmlessness without a large cost to helpfulness.

**Ground truth:**
> Evaluation uses crowdworker Elo scores comparing model outputs. The RLHF-CAI model achieves higher Elo scores on both harmlessness AND helpfulness simultaneously compared to models trained with standard RLHF on human feedback, demonstrating that the harmlessness-helpfulness tradeoff can be reduced with constitutional training.

**Score:** 10/10 — local-judge[text✓]: kw=0.63

</details>

<details><summary>Q4: What is the 'critique and revision' step in Constitutional AI and how does it work?</summary>

**Retrieved section:** `§34.4` | **Query latency:** 300 ms

**DOCNEST answer:**
> The 'critique and revision' step in Constitutional AI involves using a helpful RLHF model to critique and revise its own responses to remove harmful content, guided by a set of human-written principles forming a 'constitution'. In this process, the model first generates a critique of its original response, evaluating it against the principles in the constitution. Then, based on the critique, the model generates a revised response that aims to eliminate harmful content.     At each critique-revision step for each prompt, a principle is sampled independently from the entire constitution. This method was applied using a 52B helpful RLHF model, from which the original response, critique, and revision were all sampled. Although critiques were sometimes reasonable, they were also often inaccurate or overstated; however, the revisions were generally more harmless than the original responses.    For the main results of the paper, the authors chose to use critiqued revisions (i.e., generating a critique followed by a revision) rather than direct revisions (skipping critique), because critiqued revisions achieved better harmlessness scores for small models and may provide more transparency into the model’s reasoning process. This reasoning could help uncover more subtle harms or unintended consequences.

**Ground truth:**
> In the SL-CAI phase, the model is prompted to critique its initial response by identifying how it might be harmful according to a specific constitutional principle, then writes a revised response that corrects the identified issues. This critique-revision process can be repeated for multiple principles, producing progressively safer responses that are then used as supervised fine-tuning data.

**Score:** 5/10 — local-judge: num=0.00 kw=0.38 phrase=0.00

</details>

<details><summary>Q5: What does the Constitutional AI paper show about whether AI-generated harmlessness labels can replace human labels effectively?</summary>

**Retrieved section:** `§34.4` | **Query latency:** 339 ms

**DOCNEST answer:**
> The Constitutional AI paper shows that AI-generated harmlessness labels can replace human labels effectively, as demonstrated by the following evidence:    - Language models achieve "well over 90% binary accuracy" in predicting the better response according to helpfulness, honesty, and harmlessness, based on 221 binary comparisons from [Askell et al., 2021] and additional evaluations.  - On a more challenging dataset of 217 new comparisons focusing on subtle tests of harmlessness (including cases where evasive responses are disfavored), the performance of AI models in identifying the better response is competitive with preference models trained on human feedback.  - Specifically, in Figure 4, the paper shows that "chain-of-thought" and "ensembled chain-of-thought" reasoning in pretrained language models achieve accuracy levels that approach or match those of a "HH PM from Human Feedback" (i.e., a preference model trained on human labels).  - The paper states that "Using self-supervised preference labels for RL further improves model behavior as evaluated by crowdworkers (see Figures 2 and 3), equaling or exceeding the performance when using human feedback to evaluate harmlessness."  - The resulting RL-CAI model, trained using AI-generated feedback for harmlessness, is "preferred by crowdworkers over those trained with previously collected [Bai et al., 2022, Ganguli et al., 2022] human feedback labels for harmfulness."    Thus, the paper demonstrates that AI-generated harmlessness labels can effectively replace human labels, achieving performance that equals or exceeds human-labeled approaches in both automated evaluations and human preference judgments.

**Ground truth:**
> The paper demonstrates that AI-generated preference labels (from a feedback model evaluating responses against constitutional principles) can effectively replace human harmlessness labels in RLHF. The RLHF-CAI model trained entirely on AI feedback achieves better harmlessness Elo scores than models trained on human harmlessness data, while also maintaining comparable or better helpfulness. This shows that human annotation of harmful content can be largely eliminated through AI feedback, scaling safety training without human bottlenecks.

**Score:** 9/10 — local-judge[text~]: kw=0.43

</details>

---

## Conclusion

DOCNEST achieved **8.6/10 average accuracy** across 88 questions spanning 10 documents in 5 different formats.

**93% of questions scored ≥ 7/10**, confirming that retrieved context is accurate and sufficient for downstream LLM answers.

Formats with ground-truth Q&A (DOCX, XLSX, HTML, Markdown) test exact retrieval accuracy. PDF documents are evaluated against Gemini's training knowledge.

_Evaluated with Gemini 2.5 Pro as judge. Documents include complex tables, multi-sheet workbooks with formulas, nested headings, image captions, and multi-level document structures._