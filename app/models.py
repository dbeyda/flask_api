import sqlite3 as sql
from datetime import datetime

def insert_invoice(ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, DeactiveAt = None):
	agora = datetime.today()
	CreatedAt = agora.isoformat()
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("INSERT INTO invoices (ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
		(ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt))
	con.commit()
	con.close()

#insert_invoice(5, 2017, "Outback", "ablablabl", 25.99, 2)

def select_invoices():
	con = sql.connect("database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices")
	con.close()
	return invoice_return.fetchall()

def select_invoice(invoice_id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id))
	con.close()
	return invoice_return.fetchall()

def update_invoice(id, ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt):
	