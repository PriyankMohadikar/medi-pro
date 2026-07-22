# MediPrice Pro -- AI Provider Benchmark Report

**Generated:** 2026-07-21 11:57:43
**Questions Tested:** 7
**Providers:** OLLAMA, OPENROUTER, GEMINI

---

## Executive Summary

| Metric | OLLAMA | OPENROUTER | GEMINI |
|:-------|:------:|:------:|:------:|
| Avg Response Time | 93.1s | 20.6s | 4.5s |
| Success Rate | 5/7 | 6/7 | 2/7 |
| Quality Score | 7.0/10 | 7.6/10 | 6.4/10 |
| Reasoning Score | 4.9/10 | 4.6/10 | 2.3/10 |
| Formatting Score | 4.9/10 | 5.7/10 | 5.1/10 |
| Overall Score | 5.6/10 | 6.0/10 | 4.6/10 |

---

## Performance Comparison

| Metric | OLLAMA | OPENROUTER | GEMINI |
|:-------|:------:|:------:|:------:|
| Avg Latency | 93.1s | 20.6s | 4.5s |
| Fastest | 55.1s | 3.8s | 4.2s |
| Slowest | 115.5s | 47.4s | 4.7s |

---

## Detailed Results Per Question

### Q1: What is the market average price for CBC?
**Category:** Data Retrieval | **Difficulty:** Easy | **Expected Tool:** `get_market_average`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 106.34s | 6/10 | 0/10 | 5/10 | 3.7/10 | PASS |
| OPENROUTER | 5.47s | 6/10 | 0/10 | 5/10 | 3.7/10 | PASS |
| GEMINI | 4.2s | 10/10 | 6/10 | 7/10 | 7.7/10 | PASS |

**Response Previews:**

<details><summary>OLLAMA (106.34s)</summary>

```
The market average price for CBC across all cities is approximately $310.56.
```

</details>

<details><summary>OPENROUTER (5.47s)</summary>

```
The market average price for CBC is **₹310.56**. Prices range from ₹110.00 (lowest) to ₹400.00 (highest) across all cities.

```

</details>

<details><summary>GEMINI (4.2s)</summary>

```
Based on our latest market intelligence, here is the pricing analysis for a **Complete Blood Count (CBC)** test:

*   **Market Average Price:** $310.56
*   **Price Range:** $110.00 – $400.00

This indicates a highly competitive pricing landscape, with significant opportunities for cost optimization depending on the provider network.
```

</details>


### Q2: Compare Vitamin D prices across all providers.
**Category:** Data Retrieval | **Difficulty:** Easy | **Expected Tool:** `compare_tests`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 218.12s | 5/10 | 0/10 | 7/10 | 4.0/10 | FAIL |
| OPENROUTER | 11.32s | 10/10 | 6/10 | 7/10 | 7.7/10 | PASS |
| GEMINI | 6.39s | 5/10 | 0/10 | 7/10 | 4.0/10 | FAIL |

**Response Previews:**

<details><summary>OLLAMA (218.12s)</summary>

```
The prices for Vitamin D tests across various providers in Ahmedabad range from ₹499 to ₹1500, with the following notable prices:

- **Aarthi Scan & Labs**: ₹950
- **Redcliffe Labs**: ₹499
- **Neuberg Supratech Labs**: ₹1500

In Surat, the prices range from ₹399 to ₹1800, with some notable providers:

- **PharmaEasy**: ₹399
- **Thyrocare**: ₹1300
- **Metropolis Healthcare**: ₹1800

For Vadodara, the prices vary between ₹399 and ₹1400, including:

- **Healthians**: ₹440
- **Sterling Acquris**: ₹1200
- **Dr. LalPathLabs**: ₹1180

In Gandhinagar, the prices are in the range of ₹440 to ₹1300, with:

- **Healthians**: ₹440
- **Green Cross**: ₹1000

For Rajkot, ES Healthcare offers Vitamin D at ₹1300.

These comparisons can help you choose a provider based on your budget and location.
```

</details>

<details><summary>OPENROUTER (11.32s)</summary>

```
The price of Vitamin D testing varies significantly across providers in Gujarat. Here's a summary of the pricing:

**Lowest Prices:**
- **PharmaEasy (Vadodara):** ₹399
- **Redcliffe Labs (Ahmedabad):** ₹499
- **Healthians (Gandhinagar):** ₹440

**Highest Prices:**
- **Apollo Diagnostics (Ahmedabad):** ₹1,900
- **Metropolis Healthcare (Surat):** ₹1,800

**Average Price Range:** ₹400–₹1,900  
**Most Competitive Providers:** PharmaEasy, Redcliffe Labs, Healthians, and AacharyaTulsi Diagnostic Center (Surat: ₹800).  
**Premium Providers:** Apollo Diagnostics, Metropolis Healthcare.  

Prices are consistent across cities (Ahmedabad, Surat, Vadodara, Gandhinagar) for the same provider (e.g., ES Healthcare charges ₹1,300 in all cities). Consider budget-friendly options like PharmaEasy or Redcliffe Labs for cost savings.

```

</details>

<details><summary>GEMINI (6.39s)</summary>

```
Here is a professional market comparison of **Vitamin D** prices across different providers, categorized by city:

### **1. Ahmedabad**
*   **Lowest Price:** Redcliffe Labs — **₹499**
*   **Highest Price:** Apollo Diagnostics — **₹1,900**
*   **Mid-Range Providers:**
    *   Aarthi Scan & Labs: ₹950
    *   Tata1mg: ₹1,000
    *   MediBuddy: ₹1,149
    *   Qline Diagnostics / Unipath: ₹1,200
    *   ES Healthcare / MaxLab: ₹1,300
    *   Usmanpura: ₹1,320
    *   Shraddha Pathology Laboratory: ₹1,400
    *   Krsnaa Diagnostics / Neuberg Supratech Labs: ₹1,500

### **2. Surat**
*   **Lowest Price:** AacharyaTulsi Diagnostic Center — **₹800**
*   **Highest Price:** Metropolis Healthcare — **₹1,800**
*   **Mid-Range Providers:**
    *   NobelMicropath: ₹1,000
    *   Vahcare: ₹1,200
    *   ES Healthcare / Thyrocare / Lifeline Laboratory: ₹1,300

### **3. Vadodara**
*   **Lowest Price:** PharmaEasy — **₹399**
*   **Highest Price:** Total Health Solution — **₹1,400**
*   **Mid-Range Providers:**
    *   Recross: ₹570
    *   Dr. LalPathLabs: ₹1,180
    *   Sterling Acquris: ₹1,200
    *   ES Healthcare: ₹1,300

### **4. Gandhinagar**
*   **Lowest Price:** Healthians — **₹440**
*   **Highest Price:** ES Healthcare — **₹1,300**
*   **Mid-Range Providers:**
    *   Endocrine & Allergy Lab: ₹800
    *   Green Cross: ₹1,000

### **5. Rajkot**
*   **Provider:** ES Healthcare — **₹1,300**

---
### **Key Business Insights:**
*   **Market Leader (Budget):** **PharmaEasy** offers the most 
```

</details>


### Q3: Which tests are overpriced compared to the market? Show top 5.
**Category:** Analysis | **Difficulty:** Medium | **Expected Tool:** `get_pricing_analysis`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 110.55s | 10/10 | 10/10 | 7/10 | 9.0/10 | PASS |
| OPENROUTER | 10.45s | 10/10 | 4/10 | 7/10 | 7.0/10 | PASS |
| GEMINI | 4.71s | 10/10 | 10/10 | 10/10 | 10.0/10 | PASS |

**Response Previews:**

<details><summary>OLLAMA (110.55s)</summary>

```
Based on the analysis, the top five overpriced tests compared to the market are:

1. **LFT** in Ahmedabad - Current price: ₹1000.00, Market average: ₹813.25 (23% overpriced)
2. **FBS** in Vadodara - Current price: ₹80.00, Market average: ₹67.80 (18% overpriced)
3. **RFT / KFT** in Gandhinagar - Current price: ₹900.00, Market average: ₹769.25 (17% overpriced)
4. **Lipid Profile** in Ahmedabad - Current price: ₹700.00, Market average: ₹602.42 (16.2% overpriced)

Recommendation: Consider reducing the prices of these tests to align with market averages.

Would you like to create a custom package based on any of these tests?
```

</details>

<details><summary>OPENROUTER (10.45s)</summary>

```
**Top 5 Overpriced Tests (vs. Market Average)**  

1. **LFT – Rajkot** – ₹1,000 (Market: ₹525) – **90.5% overpriced**  
2. **Vitamin D – Gandhinagar** – ₹1,300 (Market: ₹746.67) – **74.1% overpriced**  
3. **LFT – Gandhinagar** – ₹1,000 (Market: ₹607.25) – **64.7% overpriced**  
4. **RFT / KFT – Rajkot** – ₹900 (Market: ₹600) – **50.0% overpriced**  
5. **Urine Routine – Gandhinagar** – ₹200 (Market: ₹137.25) – **45.7% overpriced**
```

</details>

<details><summary>GEMINI (4.71s)</summary>

```
Based on our latest market pricing analysis, here are the top 5 tests that are currently overpriced compared to the market average. 

### **Top 5 Overpriced Tests**

| Test Name | City | Our Price (₹) | Market Average (₹) | Markup (%) | Recommendation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **LFT** | Rajkot | 1,000.00 | 525.00 | **+90.5%** | Review Immediately |
| **Vitamin D** | Gandhinagar | 1,300.00 | 746.67 | **+74.1%** | Review Immediately |
| **LFT** | Gandhinagar | 1,000.00 | 607.25 | **+64.7%** | Review Immediately |
| **RFT / KFT** | Rajkot | 900.00 | 600.00 | **+50.0%** | Review Immediately |
| **Urine Routine** | Gandhinagar | 200.00 | 137.25 | **+45.7%** | Review Immediately |

### **Strategic Insight:**
These tests are significantly above the market average, particularly **LFT in Rajkot** and **Vitamin D in Gandhinagar**, which carry markups of over 70%. We recommend an immediate downward price adjustment for these specific regions to remain competitive and prevent volume loss to local competitors.
```

</details>


### Q4: If our CBC cost is Rs.200, calculate prices at 15% and 25% margins.
**Category:** Calculation | **Difficulty:** Medium | **Expected Tool:** `calculate_margin`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 55.12s | 8/10 | 8/10 | 3/10 | 6.3/10 | PASS |
| OPENROUTER | 3.82s | 6/10 | 2/10 | 3/10 | 3.7/10 | PASS |
| GEMINI | 5.59s | 5/10 | 0/10 | 3/10 | 2.7/10 | FAIL |

**Response Previews:**

<details><summary>OLLAMA (55.12s)</summary>

```
At a 15% margin, the suggested selling price for the CBC test is Rs.230. At a 25% margin, the suggested selling price is Rs.250. These prices ensure adequate profit while remaining competitive in the market.
```

</details>

<details><summary>OPENROUTER (3.82s)</summary>

```
<TOOLCALL>[{"name": "calculate_margin", "arguments": {"cost": 200, "margin_percentage": 25}}]</TOOLCALL>

```

</details>

<details><summary>GEMINI (5.59s)</summary>

```
Error connecting to AI Assistant: Error code: 429 - [{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3.5-flash\nPlease retry in 34.536139291s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.5-flash'}, 'quotaValue': '5'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '34s'}]}}]
```

</details>


### Q5: Create a Women's Wellness Package with appropriate tests and 20% margin.
**Category:** Package Creation | **Difficulty:** Hard | **Expected Tool:** `build_custom_package`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 115.45s | 10/10 | 6/10 | 7/10 | 7.7/10 | PASS |
| OPENROUTER | 3.17s | 1/10 | 0/10 | 1/10 | 0.7/10 | FAIL |
| GEMINI | 2.45s | 5/10 | 0/10 | 3/10 | 2.7/10 | FAIL |

**Response Previews:**

<details><summary>OLLAMA (115.45s)</summary>

```
The Women's Wellness Package includes the following tests with a 20% margin:

- CBC: $315.00
- Iron Profile: $1200.00
- LH (Luteinizing Hormone): $450.00
- Prolactin: $450.00
- TSH: $250.00

The total suggested package price is **$3,198.00**.

This pricing ensures a 20% margin on the total base cost of $2,665.00.
```

</details>

<details><summary>OPENROUTER (3.17s)</summary>

```
Error connecting to AI Assistant: Expecting ',' delimiter: line 1 column 42 (char 41)
```

</details>

<details><summary>GEMINI (2.45s)</summary>

```
Error connecting to AI Assistant: Error code: 429 - [{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3.5-flash\nPlease retry in 30.087349942s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'model': 'gemini-3.5-flash', 'location': 'global'}, 'quotaValue': '5'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '30s'}]}}]
```

</details>


### Q6: Compare CBC and HbA1c prices in Ahmedabad. Which one has better competitive positioning?
**Category:** Business Intelligence | **Difficulty:** Hard | **Expected Tool:** `compare_tests`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 78.06s | 10/10 | 10/10 | 5/10 | 8.3/10 | PASS |
| OPENROUTER | 45.21s | 10/10 | 10/10 | 10/10 | 10.0/10 | PASS |
| GEMINI | 2.36s | 5/10 | 0/10 | 3/10 | 2.7/10 | FAIL |

**Response Previews:**

<details><summary>OLLAMA (78.06s)</summary>

```
In Ahmedabad, the average price for CBC is approximately ₹319.77, while the average price for HbA1c is around ₹485.54. 

From a competitive positioning standpoint, CBC appears to have better value due to its lower average price compared to HbA1c. However, it's important to consider the clinical significance and patient demand for each test when making pricing decisions.

For package creation or comparison purposes, you might want to include both tests in relevant packages to cater to a broader range of needs while maintaining competitive pricing.
```

</details>

<details><summary>OPENROUTER (45.21s)</summary>

```
### Price Comparison Analysis: CBC vs. HbA1c (Ahmedabad)

Based on current market data for Ahmedabad, here is the pricing comparison and competitive positioning analysis:

#### **1. Price Comparison Summary**
| Metric | CBC (Complete Blood Count) | HbA1c (Glycated Hemoglobin) |
| :--- | :--- | :--- |
| **Price Range** | ₹200.00 – ₹395.00 | ₹299.00 – ₹610.00 |
| **Market Average** | ~₹315.00 | ~₹465.00 |
| **Lowest Price** | ₹200.00 (Usmanpura) | ₹299.00 (Redcliffe Labs) |
| **Highest Price** | ₹395.00 (Apollo Diagnostics) | ₹610.00 (Apollo Diagnostics) |

#### **2. Competitive Positioning Insights**

*   **CBC (High Volume/Low Margin):**
    *   **Positioning:** CBC acts as a "commodity" test with high price sensitivity. The price variance is relatively narrow (approx. ₹200 difference between lowest and highest), indicating a highly standardized market.
    *   **Strategy:** Providers like **Krsnaa Diagnostics** and **Usmanpura** hold a strong cost-leadership position. To compete here, volume and accessibility are critical.

*   **HbA1c (Specialized/Higher Margin):**
    *   **Positioning:** HbA1c shows significantly higher price volatility (approx. ₹311 difference). There is a clear tiering in the market: budget-friendly options (Redcliffe Labs at ₹299) versus premium diagnostic services (Apollo Diagnostics at ₹610).
    *   **Strategy:** There is a significant opportunity for "Value-Based Positioning." Providers like **Tata1mg** and **Aarthi Scan & Labs** are positioned in 
```

</details>

<details><summary>GEMINI (2.36s)</summary>

```
Error connecting to AI Assistant: Error code: 429 - [{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3.5-flash\nPlease retry in 25.713913379s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'location': 'global', 'model': 'gemini-3.5-flash'}, 'quotaValue': '5'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '25s'}]}}]
```

</details>


### Q7: What factors should we consider when setting prices for a new diagnostic test?
**Category:** General Knowledge | **Difficulty:** Medium | **Expected Tool:** `None`

| Provider | Time | Quality | Reasoning | Format | Overall | Status |
|:---------|:-----|:--------|:----------|:-------|:--------|:-------|
| OLLAMA | 120.03s | 0/10 | 0/10 | 0/10 | 0.0/10 | FAIL |
| OPENROUTER | 47.36s | 10/10 | 10/10 | 7/10 | 9.0/10 | PASS |
| GEMINI | 2.41s | 5/10 | 0/10 | 3/10 | 2.7/10 | FAIL |

**Response Previews:**

<details><summary>OLLAMA (120.03s)</summary>

```
Connection Error: 
```

</details>

<details><summary>OPENROUTER (47.36s)</summary>

```
As a Senior Healthcare Pricing Analyst, here are the key factors to consider when setting prices for a new diagnostic test:

## Market-Based Factors
- **Competitive landscape**: Prices of similar/competing tests in your region
- **Test complexity and technology**: Advanced diagnostics typically command premium pricing
- **Clinical value and outcomes**: Demonstrated impact on patient care and cost savings
- **Regulatory requirements**: Compliance costs influence pricing structure

## Cost Considerations
- **Direct costs**: Reagents, equipment, consumables, and laboratory supplies
- **Indirect costs**: Staff training, quality control, maintenance, and facility overhead
- **Volume expectations**: Expected test utilization and economies of scale
- **Supply chain dynamics**: Sourcing costs and vendor negotiations

## Positioning Strategy
- **Target market segment**: Hospital labs vs. outpatient clinics vs. home testing
- **Customer type**: Insurance reimbursement rates vs. self-pay patients
- **Geographic considerations**: Regional cost of living and purchasing power
- **Test urgency**: Stat/emergency testing vs. routine screening pricing

## Business Factors
- **Desired margin**: Profitability targets and return on investment
- **Market penetration strategy**: Introductory pricing vs. premium positioning
- **Bundling opportunities**: Integration with existing test packages
- **Value-based pricing**: Outcomes-based contracts when applicable

## External Influences
- **Reimbursemen
```

</details>

<details><summary>GEMINI (2.41s)</summary>

```
Error connecting to AI Assistant: Error code: 429 - [{'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. \n* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3.5-flash\nPlease retry in 21.318788615s.', 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Learn more about Gemini API quotas', 'url': 'https://ai.google.dev/gemini-api/docs/rate-limits'}]}, {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{'quotaMetric': 'generativelanguage.googleapis.com/generate_content_free_tier_requests', 'quotaId': 'GenerateRequestsPerMinutePerProjectPerModel-FreeTier', 'quotaDimensions': {'model': 'gemini-3.5-flash', 'location': 'global'}, 'quotaValue': '5'}]}, {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '21s'}]}}]
```

</details>


---

## Final Rankings

| Rank | Provider | Quality (40%) | Speed (30%) | Reliability (30%) | **Final Score** |
|:-----|:---------|:-------------|:-----------|:-----------------|:---------------|
| 1st | **OPENROUTER** | 6.0/10 | 3.1/10 | 86% | **5.9/10** |
| 2nd | **GEMINI** | 4.6/10 | 8.5/10 | 29% | **5.27/10** |
| 3rd | **OLLAMA** | 5.6/10 | 0/10 | 71% | **4.37/10** |

### Winner: **OPENROUTER** with a final score of **5.9/10**

---

*Report generated automatically by MediPrice Pro Benchmark Suite.*
