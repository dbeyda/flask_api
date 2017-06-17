import sqlite3 as sql
from datetime import datetime
from flask import abort


def select_invoices(year, month, doc, sort, page, INVOICES_PER_PAGE):
	filter_str = build_filter_str(year, month, doc)
	pagination_str = build_pagination_str(page, INVOICES_PER_PAGE)
	sort_str = build_sort_str(sort)
	query_str = ""
	if len(filter_str) > 0:
		query_str += "{} ".format(filter_str)
	if len(sort_str) > 0:
		query_str += "{} ".format(sort_str)
	if len(pagination_str) > 0:
		query_str += "{} ".format(pagination_str)

	con = sql.connect("app/database.db")
	cursor = con.cursor()
	invoices = cursor.execute("SELECT * FROM invoices WHERE IsActive = 1 {}".format(query_str))
	invoices_return = invoices.fetchall()
	con.close()
	return invoices_return

def last_invoice_id(year, month, doc, sort):
	# Retorna o ID do ultimo registro da ultima pagina de uma query.
	filter_str = build_filter_str(year, month, doc)
	sort_str = build_sort_str(sort)
	query_str = ""
	if len(filter_str) > 0:
		query_str += "{} ".format(filter_str)
	if len(sort_str) > 0:
		query_str += "{} ".format(sort_str)
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


########## Auxiliary functions #############

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

def build_sort_str(sort):
	if sort is None:
		return ""
	sort_str = "ORDER BY "
	sort_dict = split_sort(sort)
	for param in sort_dict:
		sort_str += "{} {}, ".format(param, sort_dict[param])
	print(sort_str[:-2])
	return sort_str[:-2]

def split_sort(sort):
	#receives: the sorting parameter as a string (ex: 'referencemonth,-referenceyear')
	# no signal means ascending order, '-' signal means descending order
	#returns: a dictionary {'param1': <ASC or DESC>, 'param2': <ASC or DESC>}
	# ASC for ascending order
	# DESC for descending order

	sort = sort.split(',')
	print(sort)
	sort_dict = {}
	for param in sort:
		if param[0] == '-':
			sort_dict[param[1:]] = "DESC"
		else:
			sort_dict[param] = "ASC"
	print(sort_dict)
	sort_dict2 = {}
	for param in sort_dict:
		if param.lower() == "referencemonth":
			sort_dict2["ReferenceMonth"] = sort_dict[param]
		elif param.lower() == "referenceyear":
			sort_dict2["ReferenceYear"] = sort_dict[param]
		elif param.lower() == "document":
			sort_dict2["Document"] = sort_dict[param]
		else:
			abort(400)
	
	print(sort_dict2)
	return sort_dict2