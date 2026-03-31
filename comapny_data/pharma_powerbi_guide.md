# 🔬 Pharmaceutical Sales — Power BI Report Guide
**Dataset:** pharma_sales_data.xlsx | **Period:** 2023–2024 | **Region:** UP & Uttarakhand

---

## STEP 1 — Import Data into Power BI

1. Open **Power BI Desktop**
2. Click **Home → Get Data → Excel Workbook**
3. Select `pharma_sales_data.xlsx` → choose sheet **"Sales Data"** → click **Load**

---

## STEP 2 — Transform Data (Power Query)

Go to **Home → Transform Data** and apply these steps:

| Step | Action |
|------|--------|
| Change Type | Set `Date` column → **Date** type |
| Add Column | **Year** = `Date.Year([Date])` |
| Add Column | **Month Name** = `Date.MonthName([Date])` |
| Add Column | **Month Number** = `Date.Month([Date])` |
| Add Column | **Quarter** = `"Q" & Text.From(Date.QuarterOfYear([Date]))` |
| Close & Apply | Click **Home → Close & Apply** |

---

## STEP 3 — Create a Date Table (Best Practice)

In **Home → New Table**, paste:

```dax
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2023,1,1), DATE(2024,12,31)),
    "Year",        YEAR([Date]),
    "Month Num",   MONTH([Date]),
    "Month Name",  FORMAT([Date], "MMM"),
    "Quarter",     "Q" & FORMAT([Date], "Q"),
    "Year-Month",  FORMAT([Date], "MMM YYYY")
)
```

Then go to **Model View** → drag `DateTable[Date]` → connect to `Sales Data[Date]` (Many-to-One).

---

## STEP 4 — DAX Measures

Create these in **Home → New Measure**:

### 💰 Core Revenue Measures

```dax
Total Revenue = SUM('Sales Data'[Revenue_INR])

Total Units Sold = SUM('Sales Data'[Units_Sold])

Avg Revenue Per Unit = DIVIDE([Total Revenue], [Total Units Sold])

Avg Monthly Revenue = 
AVERAGEX(
    VALUES('DateTable'[Year-Month]),
    [Total Revenue]
)
```

### 📈 Time Intelligence

```dax
Revenue LY = 
CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('DateTable'[Date]))

YoY Growth % = 
DIVIDE([Total Revenue] - [Revenue LY], [Revenue LY])

Revenue MoM Growth % = 
VAR CurrentRev = [Total Revenue]
VAR PrevRev = CALCULATE([Total Revenue], DATEADD('DateTable'[Date], -1, MONTH))
RETURN DIVIDE(CurrentRev - PrevRev, PrevRev)

Cumulative Revenue = 
CALCULATE(
    [Total Revenue],
    DATESYTD('DateTable'[Date])
)

Revenue 2023 = CALCULATE([Total Revenue], 'DateTable'[Year] = 2023)
Revenue 2024 = CALCULATE([Total Revenue], 'DateTable'[Year] = 2024)
```

### 🏆 Ranking Measures

```dax
Product Revenue Rank = 
RANKX(ALL('Sales Data'[Product]), [Total Revenue], , DESC, DENSE)

City Revenue Rank = 
RANKX(ALL('Sales Data'[City]), [Total Revenue], , DESC, DENSE)

Top Product = 
CALCULATE(
    FIRSTNONBLANK('Sales Data'[Product], 1),
    TOPN(1, ALL('Sales Data'[Product]), [Total Revenue], DESC)
)

Top City = 
CALCULATE(
    FIRSTNONBLANK('Sales Data'[City], 1),
    TOPN(1, ALL('Sales Data'[City]), [Total Revenue], DESC)
)
```

### 📊 Share & Contribution

```dax
Revenue Share % = 
DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL('Sales Data')))

State Revenue Share % = 
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL('Sales Data'[City]), ALL('Sales Data'[Product]))
)
```

---

## STEP 5 — Report Pages & Visuals

### Page 1 — Executive Summary

| Visual | Type | Fields |
|--------|------|--------|
| Total Revenue | **Card** | `[Total Revenue]` |
| Total Units | **Card** | `[Total Units Sold]` |
| YoY Growth | **Card** | `[YoY Growth %]` → format as % |
| Top Product | **Card** | `[Top Product]` |
| Revenue by Month | **Line Chart** | X: `Month Name`, Y: `[Total Revenue]` |
| Revenue by Product | **Bar Chart** | Y: `Product`, X: `[Total Revenue]`, Sort descending |
| Revenue by Category | **Donut Chart** | Legend: `Category`, Values: `[Total Revenue]` |

**Formatting tips:**
- Card visuals: set background to `#1F4E79`, font white, bold
- Line chart: use marker style, enable data labels
- Donut chart: set inner radius to 50%

---

### Page 2 — Regional Analysis

| Visual | Type | Fields |
|--------|------|--------|
| Revenue by State | **Pie / Donut** | Legend: `State`, Values: `[Total Revenue]` |
| City Revenue | **Clustered Bar** | Y: `City`, X: `[Total Revenue]`, Color by `State` |
| State × Category Matrix | **Matrix** | Rows: `State`, Cols: `Category`, Values: `[Total Revenue]` |
| Map Visual | **Map** | Location: `City`, Size: `[Total Revenue]`, Color: `State` |
| Slicers | **Slicer** | `Year`, `State`, `Category` |

---

### Page 3 — Product Deep Dive

| Visual | Type | Fields |
|--------|------|--------|
| Revenue by Product & Year | **Clustered Column** | X: `Product`, Y: `[Revenue 2023]` + `[Revenue 2024]` |
| YoY Growth % by Product | **Bar Chart** | Y: `Product`, X: `[YoY Growth %]`, conditional formatting green/red |
| Units vs Revenue scatter | **Scatter** | X: `[Total Units Sold]`, Y: `[Total Revenue]`, Details: `Product` |
| Product Rank Table | **Table** | `Product`, `[Total Revenue]`, `[Product Revenue Rank]`, `[Revenue Share %]` |

---

### Page 4 — Trend Analysis

| Visual | Type | Fields |
|--------|------|--------|
| Monthly Revenue Line | **Line Chart** | X: `Year-Month`, Y: `[Total Revenue]` |
| Cumulative Revenue | **Area Chart** | X: `Year-Month`, Y: `[Cumulative Revenue]` |
| MoM Growth % | **Column Chart** | X: `Year-Month`, Y: `[Revenue MoM Growth %]` |
| Revenue by Quarter | **Clustered Bar** | X: `Quarter`, Y: `[Total Revenue]`, Legend: `Year` |

---

## STEP 6 — Slicers & Filters (Add to All Pages)

Add these slicers on every page using **Sync Slicers** (View → Sync Slicers):

- **Year** → Dropdown slicer
- **State** → Dropdown slicer  
- **Category** → List slicer
- **Quarter** → Tile slicer

---

## STEP 7 — Formatting & Theme

### Recommended Color Theme

| Element | Color |
|---------|-------|
| Primary | `#1F4E79` (Dark Navy) |
| Secondary | `#2E75B6` (Mid Blue) |
| Accent | `#F4A261` (Orange) |
| Positive | `#2D9E6B` (Green) |
| Negative | `#E63946` (Red) |
| Background | `#F0F4F8` (Light Gray) |

### Apply a Custom Theme:
1. Go to **View → Themes → Customize Current Theme**
2. Set Name/Data colors to the palette above
3. Save as `pharma_theme.json` and reuse

---

## STEP 8 — Key Insights to Highlight (For Portfolio)

Include these callouts in your report:

1. **Atorvastatin** is the highest-revenue product across both states
2. **Lucknow** leads all cities; **Antibiotics** dominate by category (35%+ share)
3. Revenue is nearly flat YoY (–0.2%), indicating market saturation — opportunity for growth strategy
4. **Uttarakhand** has lower revenue but smaller population — per-capita efficiency is comparable
5. **Q1 & Q3** show seasonal peaks across most drug categories

---

## STEP 9 — Publish & Share

1. **File → Publish → Publish to Power BI**
2. Sign in with your Microsoft account
3. Select **My Workspace**
4. Share link or embed in portfolio

---

*Built for Portfolio Project | Data: Synthetic Pharma Sales | Python + SQL + Excel + Power BI*
