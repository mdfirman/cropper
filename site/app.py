import yaml
import os
import glob
import time

from flask_sqlalchemy import SQLAlchemy

from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g, Blueprint, send_from_directory, make_response
from flask.ext.login import login_user , logout_user , current_user , login_required
from flask.ext.login import LoginManager

from butterfly_file_handlers import build_unlabelled_img_set, get_user_counts
from userclass import User

import chartkick


# Initialize the Flask application and login manager
app = Flask(__name__)
app.config.from_object("config")
login_manager = LoginManager()
login_manager.init_app(app)

global tic
tic = time.time()

debug = True

# adding chartkick
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")


if debug:
    data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/sightings_subset/'
    yaml_name = 'sightings_subset.yaml'
else:
    data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/butterfly_subset/'
    yaml_name = 'butterflies.yaml'

global unlabelled_imgs
unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)


# this gets a specific image file, and is used in the form_submit.html
@app.route('/<sighting_id>/<img_id>')
def download_image(sighting_id, img_id):
    print sighting_id, img_id
    print "In app", data_dir + sighting_id, img_id
    return send_from_directory(data_dir + sighting_id, img_id,
        as_attachment=True)


def get_new_images():
    global unlabelled_imgs

    if not unlabelled_imgs:
        # might have run out, or might have missed one. Check all the files...
        unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)

        # now check again, if still empty then we're done
        if not unlabelled_imgs:
            return None, None, None

    return unlabelled_imgs.pop()


# Define a route for the default URL, which loads the form
@app.route('/cropper')
@login_required
def form():
    '''This is run the first time the page is loaded'''
    global tic
    tic = time.time()
    new_sighting_id, new_img_id, new_img_name = get_new_images()
    return render_template('form_submit.html', sighting_id=new_sighting_id,
        img_id=new_img_name)


@app.route('/leaderboard')
def leaderboard():
    user_counts = get_user_counts(data_dir)
    user_counts.append(('Lisa', 50))
    user_counts.append(('Mark', 23))
    user_counts = [[str(xx), float(yy)] for xx, yy in user_counts][::-1]
    return render_template('leaderboard.html', user_counts=user_counts)


@app.route('/cropper', methods=['POST'])
@login_required
def form_submission():
    '''This is run when the user clicks 'submit', with a POST request'''
    global tic

    # get the results from the form
    results = {
        'number_butterflies': str(request.form['number_butterflies']),
        'time_taken': time.time() - tic,
        'username': g.user.username,
        'datetime': time.time()
    }
    try:
        results['top_bottom'] = str(request.form['topbottom'])
        results['crop'] = {
            'x': float(request.form['x']),
            'y': float(request.form['y']),
            'width': float(request.form['width']),
            'height': float(request.form['height'])
        }
        results['notes'] = str(request.form['notes'])
    except:
        pass

    # save the results to disk
    sighting_id = request.form['sighting_id']
    img_id = request.form['img_id']
    savepath = data_dir + sighting_id + '/' + img_id.split('.')[0] + '_crop.yaml'

    with open(savepath, 'w') as f:
        yaml.dump(results, f)

    # get a new image from the set of unlabelled images
    new_sighting_id, new_img_id, new_img_name = get_new_images()

    if new_sighting_id is None:
        return render_template('form_finished.html')
    else:
        # start the clock and render the new page
        tic = time.time()
        print new_img_name
        return render_template('form_submit.html', sighting_id=new_sighting_id,
            img_id=new_img_name)


@login_manager.user_loader
def load_user(id):
    return User.from_id(id)


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.form['passwordcheck'] != request.form['password']:
        return render_template('register.html', error = "Error - passwords did not match")

    user = User.new_user(request.form['username'] , request.formindex['password'],request.form['email'])

    # todo - check if user exists
    if user:
        user.dump()
        return redirect(url_for('login'))
    else:
        return render_template('register.html', error = "Error - user already exists")


def load_user(username, password):

    user = User.from_id(username)

    if user and user.pw_correct(password):
        return user
    else:
        return None


@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = load_user(username, password)

    if registered_user is None:
        return render_template('login.html', error = "Error - Username or Password is invalid")

    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))


@app.before_request
def before_request():
    g.user = current_user

# Run the app :)
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(
        debug=True
        # host="0.0.0.0",
        # port=int("80")
    )
