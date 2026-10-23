USE RetailSalesDB;
GO

-- A. Detail transaksi
SELECT TOP 10 *
FROM dbo.vw_RetailSalesDetail
ORDER BY [Date], Transaction_ID;
GO

-- B. Tren penjualan harian
SELECT *
FROM dbo.vw_DailySales
ORDER BY [Date];
GO

-- C. Produk dengan penjualan tertinggi
SELECT *
FROM dbo.vw_ProductSales
ORDER BY Total_Sales DESC;
GO

-- D. Penjualan per kota
SELECT *
FROM dbo.vw_CitySales
ORDER BY Total_Sales DESC;
GO

-- E. Penjualan per metode pembayaran
SELECT *
FROM dbo.vw_PaymentSales
ORDER BY Total_Sales DESC;
GO

-- F. Sales KPI
SELECT *
FROM dbo.vw_SalesKPI;
GO