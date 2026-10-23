USE RetailSalesDB;
GO

-- 1. Detail transaksi untuk analisis
CREATE OR ALTER VIEW dbo.vw_RetailSalesDetail
AS
SELECT
 Transaction_ID,
 [Date],
 Product,
 Category,
 Quantity,
 Unit_Price,
 CAST(Quantity * Unit_Price AS DECIMAL(18,2)) AS Sales,
 Payment_Method,
 City
FROM dbo.RetailTransactions;
GO

-- 2. Ringkasan penjualan per hari
CREATE OR ALTER VIEW dbo.vw_DailySales
AS
SELECT
 [Date],
 COUNT(*) AS Total_Transactions,
 SUM(Quantity) AS Total_Units,
 CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2))
 AS Total_Sales
FROM dbo.RetailTransactions
GROUP BY [Date];
GO

-- 3. Ringkasan penjualan per produk
CREATE OR ALTER VIEW dbo.vw_ProductSales
AS
SELECT
 Product,
 Category,
 SUM(Quantity) AS Total_Units,
 COUNT(*) AS Total_Transactions,
 CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2))
 AS Total_Sales,
 CAST(
 SUM(Quantity * Unit_Price)
 / NULLIF(SUM(Quantity), 0)
 AS DECIMAL(18,2)
 ) AS Average_Unit_Revenue
FROM dbo.RetailTransactions
GROUP BY Product, Category;
GO

-- 4. Ringkasan penjualan per kota
CREATE OR ALTER VIEW dbo.vw_CitySales
AS
SELECT
 City,
 COUNT(*) AS Total_Transactions,
 SUM(Quantity) AS Total_Units,
 CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2))
 AS Total_Sales
FROM dbo.RetailTransactions
GROUP BY City;
GO

-- 5. Ringkasan penjualan per metode pembayaran
CREATE OR ALTER VIEW dbo.vw_PaymentSales
AS
SELECT
 Payment_Method,
 COUNT(*) AS Total_Transactions,
 CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2))
 AS Total_Sales
FROM dbo.RetailTransactions
GROUP BY Payment_Method;
GO

-- 6. Sales KPI

CREATE OR ALTER VIEW dbo.vw_SalesKPI
AS
SELECT
COUNT(*) AS Total_Transactions,
COALESCE(SUM(Quantity), 0) AS Total_Units,
COALESCE(
CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2)),
0
) AS Total_Sales,
COALESCE(
CAST(AVG(Quantity * Unit_Price) AS DECIMAL(18,2)),
0
) AS Average_Transaction_Value,
COUNT(DISTINCT Product) AS Unique_Products,
COUNT(DISTINCT City) AS Cities_Served
FROM dbo.RetailTransactions;
GO