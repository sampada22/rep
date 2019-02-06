from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/profile/<name>')
def profile(name):
	return render_template('hello.html',name = name)

if __name__  == '__main__':
	app.run(debug = True)

