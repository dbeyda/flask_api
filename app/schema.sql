drop table if exists invoices;
create table invoices (
id integer primary key autoincrement,
ReferenceMonth integer,
ReferenceYear integer,
Document varchar(14),
Description varchar(256),
Amount decimal(16, 2),
IsActive tinyint,
CreatedAt datetime,
DeactivatedAt datetime
);