from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

notas = [
{
	'id': 1,
	'cod': 285,
	'title': 'Farmacia da Republica',
	'valor total': 20
},
{
	'id': 2,
	'cod': 937,
	'title': 'Outback Steakhouse',
	'valor total': 42.99
}]


@app.route('/nf/api/v1.0/notas', methods=['GET'])
def get_notas():
    return jsonify({'notas': notas})

@app.route('/nf/api/v1.0/notas/<int:nota_id>', methods=['GET'])
def get_nota(nota_id):
	nota = [anota for anota in notas if anota['id'] == nota_id]
	if len(nota) == 0:
		abort(404)
	return jsonify({'nota': nota[0]})

@app.route('/nf/api/v1.0/notas', methods = ['POST'])
def create_nota():
	if not request.json or not 'title' in request.json or not 'cod' in request.json:
		abort(400)
	nota = {
	'id': notas[-1]['id'] + 1, #id da ultima nota +1
	'cod': request.json['cod'],
	'title': request.json['title']
	}
	notas.append(nota)
	return jsonify({'nota': nota}), 201


@app.errorhandler(404)  # para retornar Json em vez de HTTP
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)