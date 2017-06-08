from flask import Flask, jsonify, abort, make_response, request, url_for
from datetime import datetime

app = Flask(__name__)

# Dados para testes iniciais
invoices = [
{
	'id': 1,
	'ReferenceMonth': 1,
	'ReferenceYear': 2016,
    'Document': 'Outback',
    'Description': 'Batata, Cebola, 5 Refil',
    'Amount': 99.35,
    'IsActive': 1,
    'CreatedAt': datetime(2016, 1, 3, hour = 12, minute = 54, second = 3),
    'DeactiveAt': None
},
{
	'id': 2,
	'ReferenceMonth': 4,
	'ReferenceYear': 2016,
    'Document': 'Bodytech Academia',
    'Description': 'Plano Silver 6 meses',
    'Amount': 350*6,
    'IsActive': 1,
    'CreatedAt': datetime(2016, 4, 25, hour = 17, minute = 37, second = 48),
    'DeactiveAt': None
},
{
	'id': 3,
	'ReferenceMonth': 5,
	'ReferenceYear': 2016,
    'Document': 'Big Bi',
    'Description': 'Coco Gelado',
    'Amount': 6.5,
    'IsActive': 0,
    'CreatedAt': datetime(2016, 5, 12, hour = 10, minute = 3, second = 4),
    'DeactiveAt': datetime(2016, 5, 19, hour = 16)
}]

field_list = ['ReferenceMonth', 'ReferenceYear', 'Document', 'Description', 'Amount', 'IsActive', 'CreatedAt', 'DeactiveAt']


#GET ALL
@app.route('/nf/api/v1.0/invoices', methods=['GET'])
def get_invoices():
    return jsonify({'invoices': [invoice_publica(invoice) for invoice in invoices]})


#GET ID
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
	invoice = [invoice for invoice in invoices if invoice['id'] == invoice_id]
	if len(invoice) == 0:
		abort(404)
	return jsonify({'invoice': invoice_publica(invoice[0])})


#POST
@app.route('/nf/api/v1.0/invoices', methods = ['POST'])
def create_invoice():
	# if not request.json or not 'ReferenceMonth' in request.json or not 'cod' in request.json or not 'valor total' in request.json:
	# 	abort(400)
	for field in field_list:
		if not field in request.json:
			abort(400)
	if not request.json:
		abort(400)
	invoice = {
	'id': invoices[-1]['id'] + 1, #id da ultima invoice +1
	'ReferenceMonth': request.json['ReferenceMonth'],
	'ReferenceYear': request.json['ReferenceYear'],
	'Document': request.json['Document'],
	'Description': request.json['Description'],
	'Amount': request.json['Amount'],
	'IsActive': request.json['IsActive'],
	'CreatedAt': request.json['CreatedAt'],
	'DeactiveAt': request.json['DeactiveAt']
	}
	invoices.append(invoice)
	return jsonify({'invoice': invoice_publica(invoice)}), 201


#UPDATE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['PUT'])
def update_invoice(invoice_id):
	invoice = [invoice for invoice in invoices if invoice['id'] == invoice_id]
	
	# Restricoes e conferencia das informacoes
	if len(invoice) == 0:
		abort(404)
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
	# if 'CreatedAt' in request.json and type(request.json['CreatedAt']) != float:
	# 	abort(404)
	# if 'DeactiveAt' in request.json and type(request.json['DeactiveAt']) != float:
	# 	abort(404)

	for campo in field_list:
		invoice[0][campo] = request.json[campo]
	return jsonify({"invoice": invoice_publica(invoice[0])})

#DELETE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['DELETE'])
def delete_invoice(invoice_id):
	invoice = [invoice for invoice in invoices if invoice['id'] == invoice_id]
	if len(invoice) == 0:
		abort(404)
	invoices.remove(invoice[0])
	return jsonify({"result": True})

#Retornar URI, no lugar do ID
def invoice_publica(invoice):
	nova_invoice = {}
	for campo in invoice:
		if campo == 'id':
			nova_invoice['uri'] = url_for('get_invoice', invoice_id = invoice['id'], _external = True)
		else:
			nova_invoice[campo] = invoice[campo]
	return nova_invoice



# quando ocorrer erro 404 retornar Json em vez de HTTP
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)