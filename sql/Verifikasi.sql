use RetailSalesDB;
go

-- Verifikasi jumlah baris sama dengan transaksi unik, tidak ada produk yang kosong
select count(*) AS Total_Rows,
count(DISTINCT Transaction_ID) AS Unique_Transactions,
sum(Case when Product is null Then 1 else 0 end) as Missing_product,
sum(Sales) AS Total_Sales
from dbo.RetailTransactions;
go

-- Verifikasi Hasil dari ETL_pipeline
select count(*) AS Total_Transactions,
sum(Quantity) AS Total_Units,
sum(Quantity * Sales) AS Total_Sales
from dbo.RetailTransactions

select Product,
sum(Quantity) AS Total_Units,
sum(Quantity * Sales) AS Total_Sales
from dbo.RetailTransactions
group by Product
order by Total_Sales DESC;

-- Verifikasi data transaksi
select count(*) AS Total_Transaksi,
sum(Quantity) AS Total_Produk_Terjual,
sum(Quantity * Unit_Price) AS Total_Penjualan,
min([Date]) AS Tanggal_Awal,
max([Date]) AS Tanggal_Akhir
from dbo.RetailTransactions;
go
