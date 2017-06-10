from flask import Flask, jsonify, abort, make_response, request, url_for
from datetime import datetime
import app.models as models

app = Flask(__name__)

field_list = ['ReferenceMonth', 'ReferenceYear', 'Document', 'Description', 'Amount', 'IsActive', 'CreatedAt', 'DeactiveAt']


#GET ALL
@app.route('/nf/api/v1.0/invoices', methods=['GET'])
def get_invoices():
	invoices = models.select_invoices()
	invoices = fetch_dict(invoices)
	return jsonify({'invoices': [invoice_uri(invoice) for invoice in invoices]})

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
	# Conferindo os parametros obrigatorios.
	# Se nao fornecidos, 'CreatedAt' = <Hora e Data de insersao no banco de dados
	# e 'DeactiveAt' = <None>
	for field in field_list:
		if (not field in request.json) and (field not in ["CreatedAt", "DeactiveAt"]):
			abort(400)
	if not request.json:
		abort(400)

	created_invoice = fetch_dict(models.insert_invoice(**request.json))
	return jsonify({'invoice': invoice_uri(created_invoice[0])}), 201


#UPDATE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['PUT'])
def update_invoice(invoice_id):
	# Restricoes e conferencia das informacoes:
	if not request.json:
		abort (404)
	if 'ReferenceMonth' in request.json and type(request.json['ReferenceMonth']) != int:
		abort(404)
	if 'ReferenceYear' in request.json and type(request.json['ReferenceYear']) != int:
		abort(404)
	if 'Description' in request.json and (type(request.json['Description']) != str or len(request.json['Description']) > 256):
		abort(404)
	if 'Document' in request.json and (type(request.json['Document']) != str or len(request.json['Document']) > 14):
		abort(404)
	if 'Amount' in request.json and type(request.json['Amount']) != float:
		abort(404)
	if 'IsActive' in request.json and (type(request.json['IsActive']) != int or request.json['IsActive'] < 0 or request.json['IsActive'] > 256):
		abort(404)
	if 'CreatedAt' in request.json and type(request.json['CreatedAt']) != str:
	 	abort(404)
	if 'DeactiveAt' in request.json and type(request.json['DeactiveAt']) != str:
	 	abort(404)

	updated_invoice = fetch_dict(models.update_invoice(invoice_id, **request.json))
	return jsonify({'invoice': invoice_uri(updated_invoice[0])})

	# return jsonify({"invoice": invoice_uri(invoice[0])})

#DELETE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['DELETE'])
def delete_invoice(invoice_id):
	try:
		models.delete_invoice(invoice_id)
		return jsonify({"result": True})
	except:
		abort(404)


#Retornar URI, no lugar do ID
def invoice_uri(invoice):
	nova_invoice = {}
	for campo in invoice:
		if campo == 'id':
			nova_invoice['uri'] = url_for('get_invoice', invoice_id = invoice['id'], _external = True)
		else:
			nova_invoice[campo] = invoice[campo]
	return nova_invoice

# quando ocorrer erro 404 retornar Json em vez de somente HTTP
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

#popula uma lista de dicionários com o resulatdo de uma <query.fetchall()>
def fetch_dict(fetch):
	lista = [{}]
	field_list_id = ['id'] + field_list
	for row in range(len(fetch)):
		lista.append({})
		for i in range(len(fetch[0])):
			lista[row][field_list_id[i]] = fetch[row][i]
	return lista[:-1]

if __name__ == '__main__':
    app.run(debug=True)