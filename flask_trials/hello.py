from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    # sd
    a = 2
    return '<h1>Hello World! %d</h1>' % a

if __name__ == '__main__':
    app.run(debug=True)
