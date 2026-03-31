-- ============================================================
-- PHARMACEUTICAL SALES DATA ANALYSIS — SQL QUERIES
-- Database: pharma_sales   Table: sales_data
-- Columns: Date, State, City, Product, Category, Units_Sold, Revenue_INR
-- ============================================================

-- ── TABLE SETUP (SQLite / MySQL / PostgreSQL compatible) ─────────────────────
CREATE TABLE IF NOT EXISTS sales_data (
    Date          DATE,
    State         VARCHAR(50),
    City          VARCHAR(50),
    Product       VARCHAR(50),
    Category      VARCHAR(50),
    Units_Sold    INT,
    Revenue_INR   DECIMAL(12, 2)
);

-- ============================================================
-- 1. BASIC KPIs — OVERALL SUMMARY
-- ============================================================

-- Total Revenue, Units, Avg Order Value
SELECT
    COUNT(*)                          AS Total_Records,
    SUM(Units_Sold)                   AS Total_Units_Sold,
    ROUND(SUM(Revenue_INR), 2)        AS Total_Revenue_INR,
    ROUND(AVG(Revenue_INR), 2)        AS Avg_Revenue_Per_Row,
    ROUND(SUM(Revenue_INR) / SUM(Units_Sold), 2) AS Avg_Revenue_Per_Unit
FROM sales_data;


-- ============================================================
-- 2. PRODUCT PERFORMANCE
-- ============================================================

-- Revenue & Units by Product (Ranked)
SELECT
    Product,
    Category,
    SUM(Units_Sold)                              AS Total_Units,
    ROUND(SUM(Revenue_INR), 2)                   AS Total_Revenue,
    ROUND(SUM(Revenue_INR) * 100.0 /
          SUM(SUM(Revenue_INR)) OVER (), 2)      AS Revenue_Share_Pct,
    RANK() OVER (ORDER BY SUM(Revenue_INR) DESC) AS Revenue_Rank
FROM sales_data
GROUP BY Product, Category
ORDER BY Total_Revenue DESC;


-- Top 3 Products per Category
SELECT *
FROM (
    SELECT
        Category,
        Product,
        ROUND(SUM(Revenue_INR), 2)                                          AS Total_Revenue,
        RANK() OVER (PARTITION BY Category ORDER BY SUM(Revenue_INR) DESC)  AS Rank_In_Category
    FROM sales_data
    GROUP BY Category, Product
) ranked
WHERE Rank_In_Category <= 3
ORDER BY Category, Rank_In_Category;


-- ============================================================
-- 3. REGIONAL PERFORMANCE (State & City)
-- ============================================================

-- Revenue by State
SELECT
    State,
    SUM(Units_Sold)                   AS Total_Units,
    ROUND(SUM(Revenue_INR), 2)        AS Total_Revenue,
    ROUND(AVG(Revenue_INR), 2)        AS Avg_Monthly_Revenue
FROM sales_data
GROUP BY State
ORDER BY Total_Revenue DESC;


-- Top 10 Cities by Revenue
SELECT
    City,
    State,
    SUM(Units_Sold)                              AS Total_Units,
    ROUND(SUM(Revenue_INR), 2)                   AS Total_Revenue,
    RANK() OVER (ORDER BY SUM(Revenue_INR) DESC) AS City_Rank
FROM sales_data
GROUP BY City, State
ORDER BY Total_Revenue DESC
LIMIT 10;


-- City × Product Revenue Matrix (Top insight for dashboards)
SELECT
    City,
    Product,
    ROUND(SUM(Revenue_INR), 2) AS Revenue
FROM sales_data
GROUP BY City, Product
ORDER BY City, Revenue DESC;


-- ============================================================
-- 4. TIME-BASED TRENDS
-- ============================================================

-- Monthly Revenue Trend
SELECT
    DATE_FORMAT(Date, '%Y-%m')        AS Month,      -- MySQL
    -- TO_CHAR(Date, 'YYYY-MM')        AS Month,     -- PostgreSQL
    -- STRFTIME('%Y-%m', Date)         AS Month,     -- SQLite
    ROUND(SUM(Revenue_INR), 2)        AS Monthly_Revenue,
    SUM(Units_Sold)                   AS Monthly_Units
FROM sales_data
GROUP BY DATE_FORMAT(Date, '%Y-%m')
ORDER BY Month;


-- Month-over-Month (MoM) Revenue Growth
WITH monthly AS (
    SELECT
        DATE_FORMAT(Date, '%Y-%m')   AS Month,
        SUM(Revenue_INR)             AS Revenue
    FROM sales_data
    GROUP BY DATE_FORMAT(Date, '%Y-%m')
)
SELECT
    Month,
    ROUND(Revenue, 2)                                                              AS Revenue,
    ROUND(LAG(Revenue) OVER (ORDER BY Month), 2)                                   AS Prev_Month_Revenue,
    ROUND((Revenue - LAG(Revenue) OVER (ORDER BY Month)) /
           LAG(Revenue) OVER (ORDER BY Month) * 100, 2)                            AS MoM_Growth_Pct
FROM monthly
ORDER BY Month;


-- Year-over-Year (YoY) Revenue by Product
SELECT
    Product,
    ROUND(SUM(CASE WHEN YEAR(Date) = 2023 THEN Revenue_INR ELSE 0 END), 2)  AS Revenue_2023,
    ROUND(SUM(CASE WHEN YEAR(Date) = 2024 THEN Revenue_INR ELSE 0 END), 2)  AS Revenue_2024,
    ROUND(
        (SUM(CASE WHEN YEAR(Date) = 2024 THEN Revenue_INR ELSE 0 END) -
         SUM(CASE WHEN YEAR(Date) = 2023 THEN Revenue_INR ELSE 0 END)) /
         NULLIF(SUM(CASE WHEN YEAR(Date) = 2023 THEN Revenue_INR ELSE 0 END), 0) * 100
    , 2)                                                                     AS YoY_Growth_Pct
FROM sales_data
GROUP BY Product
ORDER BY YoY_Growth_Pct DESC;


-- ============================================================
-- 5. CATEGORY-LEVEL ANALYSIS
-- ============================================================

-- Revenue & Units by Drug Category
SELECT
    Category,
    COUNT(DISTINCT Product)                  AS Num_Products,
    SUM(Units_Sold)                          AS Total_Units,
    ROUND(SUM(Revenue_INR), 2)               AS Total_Revenue,
    ROUND(AVG(Revenue_INR / Units_Sold), 2)  AS Avg_Unit_Price
FROM sales_data
GROUP BY Category
ORDER BY Total_Revenue DESC;


-- Category Performance by State (Cross-tab)
SELECT
    Category,
    ROUND(SUM(CASE WHEN State = 'Uttar Pradesh' THEN Revenue_INR ELSE 0 END), 2)  AS UP_Revenue,
    ROUND(SUM(CASE WHEN State = 'Uttarakhand'   THEN Revenue_INR ELSE 0 END), 2)  AS UK_Revenue,
    ROUND(SUM(Revenue_INR), 2)                                                     AS Total_Revenue
FROM sales_data
GROUP BY Category
ORDER BY Total_Revenue DESC;


-- ============================================================
-- 6. ADVANCED — RUNNING TOTALS & CUMULATIVE REVENUE
-- ============================================================

-- Cumulative Monthly Revenue (Running Total)
WITH monthly AS (
    SELECT
        DATE_FORMAT(Date, '%Y-%m')  AS Month,
        ROUND(SUM(Revenue_INR), 2)  AS Monthly_Revenue
    FROM sales_data
    GROUP BY DATE_FORMAT(Date, '%Y-%m')
)
SELECT
    Month,
    Monthly_Revenue,
    ROUND(SUM(Monthly_Revenue) OVER (ORDER BY Month), 2) AS Cumulative_Revenue
FROM monthly
ORDER BY Month;


-- Best Performing City per State (Window Function)
SELECT *
FROM (
    SELECT
        State,
        City,
        ROUND(SUM(Revenue_INR), 2)                                           AS Total_Revenue,
        RANK() OVER (PARTITION BY State ORDER BY SUM(Revenue_INR) DESC)      AS Rank_In_State
    FROM sales_data
    GROUP BY State, City
) ranked
WHERE Rank_In_State = 1;


-- ============================================================
-- 7. DATA QUALITY CHECKS
-- ============================================================

-- Check for NULLs
SELECT
    SUM(CASE WHEN Date        IS NULL THEN 1 ELSE 0 END) AS Null_Date,
    SUM(CASE WHEN State       IS NULL THEN 1 ELSE 0 END) AS Null_State,
    SUM(CASE WHEN City        IS NULL THEN 1 ELSE 0 END) AS Null_City,
    SUM(CASE WHEN Product     IS NULL THEN 1 ELSE 0 END) AS Null_Product,
    SUM(CASE WHEN Category    IS NULL THEN 1 ELSE 0 END) AS Null_Category,
    SUM(CASE WHEN Units_Sold  IS NULL THEN 1 ELSE 0 END) AS Null_Units,
    SUM(CASE WHEN Revenue_INR IS NULL THEN 1 ELSE 0 END) AS Null_Revenue
FROM sales_data;

-- Check for Negative or Zero Values
SELECT COUNT(*) AS Invalid_Rows
FROM sales_data
WHERE Units_Sold <= 0 OR Revenue_INR <= 0;

-- Distinct values per column
SELECT
    COUNT(DISTINCT State)    AS Distinct_States,
    COUNT(DISTINCT City)     AS Distinct_Cities,
    COUNT(DISTINCT Product)  AS Distinct_Products,
    COUNT(DISTINCT Category) AS Distinct_Categories
FROM sales_data;

-- ============================================================
-- END OF QUERIES
-- ============================================================
