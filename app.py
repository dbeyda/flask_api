from flask import Flask, jsonify, abort, make_response, request, url_for, g
from datetime import datetime
import app.models as models
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
import app.security as sec
import jwt

app = Flask(__name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')

field_list = ['ReferenceMonth', 'ReferenceYear', 'Document', 'Description', 'Amount', 'IsActive', 'CreatedAt', 'DeactiveAt']
private_field_list = ['IsActive', 'CreatedAt', 'DeactiveAt']

##########    USER AND SECURITY RELATED:
@basic_auth.verify_password
def verify_password(user, password):
	user_hash = sec.get_user_hash(user)
	if len(user_hash) > 0 and sec.verify_password(password, user_hash[0][0]):
		return True
	return False

@token_auth.verify_token
def verify_token(token):
	try:
		data = jwt.decode(token, sec.secret, algorithms=['HS256'])
		return True
	except:
		return False

@app.route('/nf/api/v1.0/users/get_token')
@basic_auth.login_required
def get_token():
	token = sec.generate_auth_token(request.authorization.username).decode("UTF-8")
	return jsonify({'Token': token})

@app.route('/nf/api/v1.0/users/register')
def register_new_user():
	user = request.authorization.username
	password = request.authorization.password
	if (user is None) or (password is None):
		abort(400)
	if sec.register_user(user, password):
		return jsonify({'User': user, 'Status': 'Created'}), 201

@app.route('/nf/api/v1.0/users/delete')
@basic_auth.login_required
def del_user():
	user = request.authorization.username
	if sec.delete_user(user):
		return jsonify({'User': user, "result": True})
	abort(404)


########### INVOICES RELATED:
#GET ALL
@app.route('/nf/api/v1.0/invoices', methods=['GET'])
@token_auth.login_required
def get_invoices():
	#invoices_per_page:
	invoices_per_page = request.args.get("per-page")
	if (invoices_per_page is None):
		invoices_per_page = 5
	elif not invoices_per_page.isdigit():
		abort(400)
	#Limit for invoices_per_page:
	invoices_per_page = int(invoices_per_page)
	if invoices_per_page > 50:
		invoices_per_page = 50
	#page:
	page = request.args.get("page")
	if page is None:
		page = 1
	elif not page.isdigit():
		abort(400)
	page = int(page)

	#sort:
	sort = request.args.get("sort")
	if sort is not None:
		sort = sort.replace(" ", "")

	#filters:
	year = request.args.get("referenceyear")
	month = request.args.get("referencemonth")
	doc = request.args.get("document")

	#getting invoices from database:
	invoices = models.select_invoices(year, month, doc, sort, page, invoices_per_page)
	invoices = fetch_dict(invoices)
	if len(invoices) == 0:
		abort(404)

	#building 'next' and 'prev' urls for pagination:
	params_url = build_params_url(year, month, doc, sort, invoices_per_page)
	if page == 1:
		prev_url = None
	else:
		prev_url = url_for('get_invoices', _external = True) + "?page=" + str(page-1) + params_url

	if len(invoices) < invoices_per_page:
		next_url = None
	elif len(invoices) == invoices_per_page:
		if invoices[-1]['id'] == models.last_invoice_id(year, month, doc, sort):
			next_url = None
		else:
			next_url = url_for('get_invoices', _external = True) + "?page=" + str(page+1) + params_url

	invoices = {
	'prev': prev_url,
	'invoices': [invoice_uri(invoice) for invoice in invoices],
	'next': next_url
	}
	return jsonify(invoices)

#GET ID
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods=['GET'])
@token_auth.login_required
def get_invoice(invoice_id):
	invoice = models.select_invoice(invoice_id)
	invoice = fetch_dict(invoice)
	if len(invoice) == 0:
		abort(404)
	return jsonify({'invoice': invoice_uri(invoice[0])})

#POST
@app.route('/nf/api/v1.0/invoices', methods = ['POST'])
def create_invoice():
	# Checking for the obligatory parameters:
	for field in field_list:
		if (not field in request.json) and (field not in private_field_list):
			abort(400)
	if not valida_entrada(request.json):
		abort(400)
	created_invoice = fetch_dict(models.insert_invoice(**request.json))
	return jsonify({'invoice': invoice_uri(created_invoice[0])}), 201

#UPDATE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['PUT'])
@token_auth.login_required
def update_invoice(invoice_id):
	if not valida_entrada(request.json):
		abort(400)
	updated_invoice = fetch_dict(models.update_invoice(invoice_id, **request.json))
	if len(updated_invoice) == 0:
		abort(404)
	return jsonify({'invoice': invoice_uri(updated_invoice[0])})

#DELETE
@app.route('/nf/api/v1.0/invoices/<int:invoice_id>', methods = ['DELETE'])
@token_auth.login_required
def delete_invoice(invoice_id):
	if models.delete_invoice(invoice_id):
		return jsonify({"result": True})
	abort(404)

# when errors occur, return JSON instead of only HTTP:
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)
@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)
@app.errorhandler(401)
def unauthorized_access(error):
	return make_response(jsonify({'error': 'Unauthorized Access'}), 401)


#-----------AUXILIARY FUNCTIONS----------


def fetch_dict(fetch):
	#Receives a tuple that is a result from a <databse-query.fetchall()>
	#Returns a list of invoices, where each invoice is represented by a dictionary, with the field_list fields and also 'id' related to each invoice filled.
	lista = [{}]
	field_list_id = ['id'] + field_list
	for row in range(len(fetch)):
		lista.append({})
		for i in range(len(fetch[0])):
			lista[row][field_list_id[i]] = fetch[row][i]
	return lista[:-1]


def invoice_uri(invoice):
	#Receives an invoice in the format of a dictionary.
	#Returns the same dictionary (invoice), changing the field 'id' for the field 'uri'
	nova_invoice = {}
	for campo in invoice:
		if campo == 'id':
			nova_invoice['uri'] = url_for('get_invoice', invoice_id = invoice['id'], _external = True)
		else:
			nova_invoice[campo] = invoice[campo]
	return nova_invoice

def valida_entrada(invoice):
	#Receives a dictionary with keys and values for the fields of a POST or UPDATE request.
	#Returns True if all the fields and values are valid, False if any field is not valid.
	if not invoice:
		return False
	#Search for fields that shouldn't be inputted by the user:
	for field in private_field_list:
		if field in invoice:
			return False
	#Validates the types of the values provided in each parameter:
	if 'ReferenceMonth' in invoice and type(invoice['ReferenceMonth']) != int:
		return False
	if 'ReferenceYear' in invoice and type(invoice['ReferenceYear']) != int:
		return False
	if 'Description' in invoice and (type(invoice['Description']) != str or len(invoice['Description']) > 256):
		return False
	if 'Document' in invoice and (type(invoice['Document']) != str or len(invoice['Document']) > 14):
		return False
	if 'Amount' in invoice and type(invoice['Amount']) != float:
		return False
	return True

def build_params_url(year, month, doc, sort, per_page):
	#Receives parameters that are passed through URL.
	#Returns a string containing those params in the format to be used in an URL.
	params_url = "&per-page={}&".format(per_page)
	if year is not None:
		params_url += "referenceyear={}&".format(year)
	if month is not None:
		params_url += "referencemonth={}&".format(month)
	if doc is not None:
		params_url += "document={}&".format(doc)
	if sort is not None:
		params_url += "sort={}&".format(sort)
	return params_url[:-1]

if __name__ == '__main__':
    app.run(debug=True)