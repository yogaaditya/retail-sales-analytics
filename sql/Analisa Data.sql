use RetailSalesDB;
go

-- Verifikasi jumlah transaksi
select count(*) AS Total_Transactions,
SUM(Quantity) as Total_Unit,
SUM(Sales) AS Total_Sales
from dbo.RetailTransactions;
go

-- Total penjualan per produk
select Product,
sum(Quantity) as Total_Unit,
sum(Sales) as Total_Sales
from dbo.RetailTransactions
group by Product
order by Total_Sales DESC;
go

-- Tren penjualan harian
select [Date],
count(*) AS Total_Transactions,
SUM(Sales) AS Daily_Sales
from dbo.RetailTransactions
group by [Date]
order by [Date];
go

-- Penjualan per metode pembayaran
select
Payment_Method,
count(*) AS Total_Transactions,
SUM(Sales) AS Total_Sales
from dbo.RetailTransactions
group by Payment_Method
order by Total_Sales DESC;
go