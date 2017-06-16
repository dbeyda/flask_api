import sqlite3 as sql
from datetime import datetime
from flask import abort


def select_invoices(year, month, doc, orderby1, orderby2, orderby3, page, INVOICES_PER_PAGE):
	filter_str = build_filter_str(year, month, doc)
	pagination_str = build_pagination_str(page, INVOICES_PER_PAGE)
	orderby_str = build_orderby_str(orderby1, orderby2, orderby3)
	query_str = ""
	if len(filter_str) > 0:
		query_str += "{} ".format(filter_str)
	if len(orderby_str) > 0:
		query_str += "{} ".format(orderby_str)
	if len(pagination_str) > 0:
		query_str += "{} ".format(pagination_str)

	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoices = cursor.execute("SELECT * FROM invoices WHERE IsActive = 1 {}".format(query_str))
	invoices_return = invoices.fetchall()
	con.close()
	return invoices_return

def last_invoice_id(year, month, doc, orderby1, orderby2, orderby3):
	# Retorna o ID do ultimo registro da ultima pagina de uma query.
	filter_str = build_filter_str(year, month, doc)
	orderby_str = build_orderby_str(orderby1, orderby2, orderby3)
	query_str = ""
	if len(filter_str) > 0:
		query_str += "{} ".format(filter_str)
	if len(orderby_str) > 0:
		query_str += "{} ".format(orderby_str)
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	last_id = cursor.execute("SELECT id FROM invoices WHERE IsActive = 1 {}".format(query_str)).fetchall()
	con.close()
	return last_id[-1][0]

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

	update_string = update_string[:-2]
	cursor.execute("UPDATE invoices SET {} WHERE id = ? AND IsActive = 1".format(update_string), (str(invoice_id),))
	con.commit()
	updated = cursor.execute("SELECT * FROM invoices WHERE id = ? AND IsActive = 1", (str(invoice_id),)).fetchall()
	con.close()
	return updated



def delete_invoice(id):
	DeactiveAt = datetime.today().isoformat()
	con = sql.connect("app/database.db")
	cursor = con.cursor()
	target = cursor.execute("SELECT * FROM invoices WHERE id = ? AND IsActive = 1", (str(id),)).fetchall()
	if len(target) == 0:
		return 0
	cursor.execute("UPDATE invoices SET IsActive = 0, DeactiveAt = ?  WHERE id = ? AND IsActive = 1", (DeactiveAt, id, ))
	con.commit()
	con.close()
	return 1

def build_filter_str(year, month, doc):
	filter_str = ""
	if year != None:
		filter_str = filter_str + "AND ReferenceYear = {} ".format(str(year))
	if month != None:
		filter_str = filter_str + "AND ReferenceMonth = {} ".format(str(month))
	if doc != None:
		filter_str = filter_str + "AND Document = '{}' ".format(str(doc))
	return filter_str[:-1]

def build_pagination_str(page, INVOICES_PER_PAGE):
	offset = (INVOICES_PER_PAGE * (page-1))
	limit = INVOICES_PER_PAGE
	pagination_str = "LIMIT {} OFFSET {}".format(limit, offset)
	return pagination_str

def build_orderby_str(orderby1, orderby2, orderby3):
	orderby_str = ""
	if orderby1 != None:
		orderby1 = split_orderby(orderby1)
		if len(orderby_str)>0:
			orderby_str += ', '
		orderby_str +=  orderby1[0] + " " + orderby1[1]
	if orderby2 != None:
		orderby2 = split_orderby(orderby2)
		if len(orderby_str)>0:
			orderby_str += ', '
		orderby_str +=  orderby2[0] + " " + orderby2[1]
	if orderby3 != None:
		orderby3 = split_orderby(orderby3)
		if len(orderby_str)>0:
			orderby_str += ', '
		orderby_str +=  orderby3[0] + " " + orderby3[1]
	
	if len(orderby_str) > 0:
		orderby_str = 'ORDER BY ' + orderby_str
	return orderby_str

def split_orderby(orderby):
	if (orderby.count('(')!=1) or (orderby.count(')')!=1) or (orderby.count(',')!=1):
		abort(400)
	orderby = orderby.replace(" ", "")
	orderby = orderby.split(',')
	orderby[0] = orderby[0][1:]
	orderby[1] = orderby[1][:-1]
	if orderby[0] not in ["ReferenceMonth", "ReferenceYear", "Document"]:
		abort(400)
	if orderby[1] not in ["ASC", "DESC"]:
		abort(400)
	return orderby