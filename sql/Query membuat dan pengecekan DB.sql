-- Pengecekan DB dan membuat DB baru
if DB_ID('RetailSalesDB') IS NULL
begin
create database RetailSalesDB;
end;
go

-- Pemilihan DB
use RetailSalesDB;
go

-- Pengecekan TABEL dan pembuatan TABEL baru
if object_id('dbo.RetailTransactions','U') IS NULL
begin
create table dbo.RetailTransactions(
Transaction_ID varchar(20) not null,
[Date] DATE not null,
Product nvarchar(100) not null,
Category nvarchar(50) not null,
Quantity int not null,
Unit_Price decimal(18,2) not null,
Payment_Method nvarchar(30) not null,
City nvarchar(100) not null,
Sales as (Quantity * Unit_Price) PERSISTED,

CONSTRAINT PK_RetailTransactions PRIMARY KEY (Transaction_ID),
CONSTRAINT CK_RetailTransactions_Quantity CHECK (Quantity > 0),
CONSTRAINT CK_RetailTransaction_UnitPrice CHECK (Unit_Price > 0)
);
end;
go

-- Cek DB yang di pakai
select DB_NAME() AS CurrentDatabase;

-- Cek apakah DB yang dibuar sudah ada di SCHEMA dbo
select TABLE_NAME
from INFORMATION_SCHEMA.TABLES
where TABLE_SCHEMA = 'dbo'
and TABLE_NAME = 'RetailTransactions';
go