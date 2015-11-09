from flask import abort
from flask import Flask
app = Flask(__name__)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.get(request.form['uuid'])

        if user and hash_password(request.form['password']) == user._password:
            login_user(user, remember=True)
            return redirect('/home/')
        else:
            return abort(401)  # 401 Unauthorized
    else:
        return abort(405)  # 405 Method Not Allowed
