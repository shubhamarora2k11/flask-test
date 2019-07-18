from flask import Flask, render_template, redirect,  url_for, request, Response, current_app, flash, jsonify, make_response

app = Flask(__name__)

@app.route('/home')
def home():
	return render_template('index.html')


@app.route('/home/create-entry', methods = ['POST'])
def create_entry():

	req = request.get_json()

	print(req)

	res = make_response(jsonify({"message":"JSON Recieved"}), 200)
	res = make_response(jsonify(req), 200)
	
	return res


if __name__ == '__main__':
	app.run(debug=True, port=5001)
