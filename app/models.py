import sqlite3 as sql
from datetime import datetime

def insert_invoice(ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, DeactiveAt = None):
	agora = datetime.today()
	CreatedAt = agora.isoformat()
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	cursor.execute("INSERT INTO invoices (ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
		(ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt))
	con.commit()
	created = cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 1").fetchall()
	con.close()
	return created

#insert_invoice(5, 2017, "Outback", "ablablabl", 25.99, 2)

def select_invoices():
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices").fetchall()
	con.close()
	return invoice_return

def select_invoice(invoice_id):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices WHERE id = ?", (str(invoice_id), )).fetchall()
	con.close()
	return invoice_return

def update_invoice(invoice_id,**kwargs):
# ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	update_string = ""
	for key in kwargs:
		if type(kwargs[key]) == str:
			update_string += "{} = '{}', ".format(key, kwargs[key])
		else:
			update_string += "{} = {}, ".format(key, kwargs[key])
	update_string = update_string[:-2]
	print(update_string)
	cursor.execute("UPDATE invoices SET {} WHERE id = ?".format(update_string), (str(invoice_id)))
	con.commit()
	con.close()



def delete_invoice(id):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	cursor.execute("DELETE FROM invoices WHERE id = ?", (id, ))
	con.commit()
	con.close()
