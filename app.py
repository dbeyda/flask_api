from flask import Flask, jsonify, abort, make_response, request, url_for
from datetime import datetime
import app.models as models

app = Flask(__name__)

field_list = ['ReferenceMonth', 'ReferenceYear', 'Document', 'Description', 'Amount', 'IsActive', 'CreatedAt', 'DeactiveAt']


#GET ALL
@app.route('/nf/api/v1.0/invoices', methods=['GET'])
@app.route('/nf/api/v1.0/invoices/index', methods=['GET'])
@app.route('/nf/api/v1.0/invoices/index/', methods=['GET'])
@app.route('/nf/api/v1.0/invoices/index/<int:page>', methods=['GET'])
def get_invoices(page = 1):
	INVOICES_PER_PAGE = 5
	#orderby:
	orderby1 = request.args.get("OrderBy1")
	orderby2 = request.args.get("OrderBy2")
	orderby3 = request.args.get("OrderBy3")
	#filters:
	year = request.args.get("ReferenceYear")
	month = request.args.get("ReferenceMonth")
	doc = request.args.get("Document")
	#get invoices:
	invoices = models.select_invoices(year, month, doc, orderby1, orderby2, orderby3, page, INVOICES_PER_PAGE)
	invoices = fetch_dict(invoices)
	if len(invoices) == 0:
		abort(404)

	#pagination:
	params_url = build_params_url(year, month, doc, orderby1, orderby2, orderby3)
	if page == 1:
		prev_url = None
	else:
		prev_url = url_for('get_invoices', page = page - 1, _external = True) + params_url

	if len(invoices) < INVOICES_PER_PAGE:
		next_url = None
	elif len(invoices) == INVOICES_PER_PAGE:
		if invoices[-1]['id'] == models.last_invoice_id(year, month, doc, orderby1, orderby2, orderby3):
			next_url = None
		else:
			next_url = url_for('get_invoices', page = page + 1, _external = True) + params_url

	invoices = {
	'prev': prev_url,
	'invoices': [invoice_uri(invoice) for invoice in invoices],
	'next': next_url
	}
	return jsonify(invoices)

#GET ID
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
	invoice = models.select_invoice(invoice_id)
	invoice = fetch_dict(invoice)
	if len(invoice) == 0:
		abort(404)
	return jsonify({'invoice': invoice_uri(invoice[0])})

#POST
@app.route('/nf/api/v1.0/invoices', methods = ['POST'])
def create_invoice():
	# Conferindo os parametros obrigatorios:
	for field in field_list:
		if (not field in request.json) and (field not in ["CreatedAt", "DeactiveAt", "IsActive"]):
			abort(400)
	for field in ["CreatedAt", "DeactiveAt", "IsActive"]:
		if field in request.json:
			abort(400)
	if not request.json:
		abort(400)
	valida_campos(request.json)

	created_invoice = fetch_dict(models.insert_invoice(**request.json))
	return jsonify({'invoice': invoice_uri(created_invoice[0])}), 201


#UPDATE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['PUT'])
def update_invoice(invoice_id):
	for field in ["CreatedAt", "DeactiveAt", "IsActive"]:
		if field in request.json:
			abort(400)
	if not request.json:
		abort(400)
	valida_campos(request.json)
	
	updated_invoice = fetch_dict(models.update_invoice(invoice_id, **request.json))
	if len(updated_invoice) == 0:
		abort(404)
	return jsonify({'invoice': invoice_uri(updated_invoice[0])})
	# return jsonify({"invoice": invoice_uri(invoice[0])})

#DELETE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['DELETE'])
def delete_invoice(invoice_id):
	if models.delete_invoice(invoice_id):
		return jsonify({"result": True})
	abort(404)



#-----------FUNCOES AUXILIARES----------

# quando ocorrer erros, retornar JSON em vez de somente HTTP:
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)


def fetch_dict(fetch):
#popula uma lista de dicionários com o resulatdo de uma <query.fetchall()>
	lista = [{}]
	field_list_id = ['id'] + field_list
	for row in range(len(fetch)):
		lista.append({})
		for i in range(len(fetch[0])):
			lista[row][field_list_id[i]] = fetch[row][i]
	return lista[:-1]


def invoice_uri(invoice):
#Retornar URI, no lugar do ID
	nova_invoice = {}
	for campo in invoice:
		if campo == 'id':
			nova_invoice['uri'] = url_for('get_invoice', invoice_id = invoice['id'], _external = True)
		else:
			nova_invoice[campo] = invoice[campo]
	return nova_invoice

def valida_campos(invoice):
#valida se os valores fornecidos estao adequados aos tipos dos campos do banco de dados
	if not invoice:
		abort (400)
	if 'ReferenceMonth' in invoice and type(invoice['ReferenceMonth']) != int:
		abort(400)
	if 'ReferenceYear' in invoice and type(invoice['ReferenceYear']) != int:
		abort(400)
	if 'Description' in invoice and (type(invoice['Description']) != str or len(invoice['Description']) > 256):
		abort(400)
	if 'Document' in invoice and (type(invoice['Document']) != str or len(invoice['Document']) > 14):
		abort(400)
	if 'Amount' in invoice and type(invoice['Amount']) != float:
		abort(400)

def build_params_url(year, month, doc, orderby1, orderby2, orderby3):
	params_url = "?"
	if year != None:
		params_url += "ReferenceYear={}&".format(year)
	if month != None:
		params_url += "ReferenceMonth={}&".format(month)
	if doc != None:
		params_url += "Document={}&".format(doc)
	if orderby1 != None:
		params_url += "OrderBy1={}&".format(orderby1.replace(" ", ""))
	if orderby2 != None:
		params_url += "OrderBy2={}&".format(orderby2.replace(" ", ""))
	if orderby3 != None:
		params_url += "OrderBy3={}&".format(orderby3.replace(" ", ""))
	return params_url[:-1]


if __name__ == '__main__':
    app.run(debug=True)