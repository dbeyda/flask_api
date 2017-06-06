from flask import Flask, jsonify, abort, make_response, request, url_for

app = Flask(__name__)

notas = [
{
	'id': 1,
	'cod': 285,
	'title': 'Farmacia da Republica',
	'valor total': 20.0
},
{
	'id': 2,
	'cod': 937,
	'title': 'Outback Steakhouse',
	'valor total': 42.99
}]



#GET ALL
@app.route('/nf/api/v1.0/notas', methods=['GET'])
def get_notas():
    return jsonify({'notas': [nota_publica(nota) for nota in notas]})


#GET ID
@app.route('/nf/api/v1.0/notas/<int:nota_id>', methods=['GET'])
def get_nota(nota_id):
	nota = [anota for anota in notas if anota['id'] == nota_id]
	if len(nota) == 0:
		abort(404)
	return jsonify({'nota': nota_publica(nota[0])})


#POST
@app.route('/nf/api/v1.0/notas', methods = ['POST'])
def create_nota():
	if not request.json or not 'title' in request.json or not 'cod' in request.json or not 'valor total' in request.json:


		abort(400)
	nota = {
	'id': notas[-1]['id'] + 1, #id da ultima nota +1
	'cod': request.json['cod'],
	'title': request.json['title'],
	'valor total': request.json['valor total']
	}
	notas.append(nota)
	return jsonify({'nota': nota_publica(nota)}), 201


#UPDATE
@app.route('/nf/api/v1.0/notas/<int:nota_id>', methods = ['PUT'])
def update_nota(nota_id):
	nota = [nota for nota in notas if nota['id'] == nota_id]
	
	# Restricoes e conferencia das informacoes
	if len(nota) == 0: abort(404)
	if not request.json: abort (404)
	if 'cod' in request.json and type(request.json['cod']) != int: abort(404)
	if 'title' in request.json and type(request.json['title']) != str: abort(404)
	if 'valor total' in request.json and type(request.json['valor total']) != float: abort(404)

	nota[0] ['cod'] = request.json['cod']
	nota[0]['title'] = request.json['title']
	nota[0]['valor total'] = request.json['valor total']
	return jsonify({"nota": nota_publica(nota[0])})

#DELETE
@app.route('/nf/api/v1.0/notas/<int:nota_id>', methods = ['DELETE'])
def delete_nota(nota_id):
	nota = [nota for nota in notas if nota['id'] == nota_id]
	if len(nota) == 0:
		abort(404)
	notas.remove(nota[0])
	return jsonify({"result": True})

#Retornar URI, além do ID
def nota_publica(nota):
	nova_nota = {}
	for campo in nota:
		if campo == 'id':
			nova_nota['uri'] = url_for('get_nota', nota_id = nota['id'], _external = True)
		else:
			nova_nota[campo] = nota[campo]
	return nova_nota




@app.errorhandler(404)  # para retornar Json em vez de HTTP
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)