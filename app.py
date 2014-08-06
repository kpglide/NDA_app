from flask import Flask, request, render_template, jsonify
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap


app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

@app.route('/')
def home():
	return render_template('home.html')
	#return jsonify({'ip': request.remote_addr}), 200

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
	
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500
	
if __name__ == '__main__':
	manager.run()