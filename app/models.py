import sqlite3 as sql
from datetime import datetime


#insert_invoice(5, 2017, "Outback", "ablablabl", 25.99, 2)

def select_invoices():
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices WHERE IsActive = 1").fetchall()
	con.close()
	return invoice_return

def select_invoice(invoice_id):
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoice_return = cursor.execute("SELECT * FROM invoices WHERE id = ? AND IsActive = 1", (str(invoice_id), )).fetchall()
	con.close()
	return invoice_return

def insert_invoice(ReferenceMonth, ReferenceYear, Document, Description, Amount):
	IsActive = 1
	CreatedAt = datetime.today().isoformat()
	DeactiveAt = None

	con = sql.connect("app/database.db")
	cursor = con.cursor()
	cursor.execute("INSERT INTO invoices (ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
		(ReferenceMonth, ReferenceYear, Document, Description, Amount, IsActive, CreatedAt, DeactiveAt))
	con.commit()
	created = cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 1").fetchall()
	con.close()
	return created

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

	# retirando o ultimo ", " da update_string:
	update_string = update_string[:-2]
	cursor.execute("UPDATE invoices SET {} WHERE id = ? AND IsActive = 1".format(update_string), (str(invoice_id)))
	con.commit()
	updated = cursor.execute("SELECT * FROM invoices WHERE id = ? AND IsActive = 1", (str(invoice_id))).fetchall()
	con.close()
	return updated



def delete_invoice(id):
	DeactiveAt = datetime.today().isoformat()
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	target = cursor.execute("SELECT * FROM invoices WHERE id = ? AND IsActive = 1", (str(id))).fetchall()
	if len(target) == 0:
		return 0
	cursor.execute("UPDATE invoices SET IsActive = 0, DeactiveAt = ?  WHERE id = ? AND IsActive = 1", (DeactiveAt, id, ))
	con.commit()
	con.close()
	return 1
