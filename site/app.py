import yaml
import string
import os
import glob
import time
import socket

from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g, Blueprint, send_from_directory, make_response
from flask.ext.login import login_user , logout_user , current_user , login_required
from flask.ext.login import LoginManager

from butterfly_file_handlers import build_unlabelled_img_set, get_user_counts, getpaths
from userclass import User

import chartkick


# Initialize the Flask application and login manager
app = Flask(__name__)
app.config.from_object("config")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

global tic
tic = time.time()


# adding chartkick
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

# setting some constants
debug = True
num_labellers_required_per_image = 3
data_dir, yaml_name = getpaths(debug)

# creating the list of unlabelled images
global unlabelled_imgs
unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)


def get_new_images(username):
    '''
    Returns a tuple with info about an image suitable for this user to label
    '''
    global unlabelled_imgs

    if not unlabelled_imgs:
        # might have run out, or might have missed one. Check all the files...
        print "Checking again..."
        unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)

        # now check again, if still empty then we're done
        if not unlabelled_imgs:
            return None, None, None

    # iterate until we have found one that this user hasn't labelled
    for (sighting_id, img_id), tmp in unlabelled_imgs.iteritems():
        if username not in tmp['labellers']:
            return sighting_id, img_id, tmp['img_name']

    # should only get here if this user has labelled all the images which
    # haven't been labelled enough
    return None, None, None


def remember_user_labelling(sighting_id, img_id, username):
    '''
    Adds the fact that a user has done a labelling to the main dictionary
    Will remove the image if it get above a threshold
    '''
    global unlabelled_imgs

    unlabelled_imgs[(sighting_id, img_id)]['labellers'].add(username)

    num_labellers = len(unlabelled_imgs[(sighting_id, img_id)]['labellers'])

    if num_labellers >= num_labellers_required_per_image:
        print "Removing image %s, %s" % (sighting_id, img_id)
        del unlabelled_imgs[(sighting_id, img_id)]


# this gets a specific image file, and is used in the form_submit.html
@app.route('/<sighting_id>/<img_id>')
def download_image(sighting_id, img_id):
    print sighting_id, img_id
    print "In app", data_dir + sighting_id, img_id
    return send_from_directory(data_dir + sighting_id, img_id,
        as_attachment=True)


# Define a route for the default URL, which loads the form
@app.route('/cropper')
@login_required
def form():
    '''This is run the first time the page is loaded'''
    global tic
    tic = time.time()
    new_sighting_id, new_img_id, new_img_name = get_new_images(g.user.username)

    if new_sighting_id is None:
        return render_template('form_finished.html')
    else:
        # start the clock and render the new page
        tic = time.time()
        print new_img_name
        return render_template('form_submit.html', sighting_id=new_sighting_id,
            img_id=new_img_name)


@app.route('/leaderboard')
def leaderboard():
    user_counts = get_user_counts(data_dir)
    user_counts.append(('Mark', max([xx for _, xx in user_counts]) + 10))
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
    savepath = data_dir + sighting_id + '/' + \
        img_id.split('.')[0] + '_' + g.user.username + '_crop.yaml'

    remember_user_labelling(sighting_id, img_id.split('.')[0], g.user.username)

    with open(savepath, 'w') as f:
        yaml.dump(results, f)

    # get a new image from the set of unlabelled images
    new_tic = time.time()
    new_sighting_id, new_img_id, new_img_name = get_new_images(g.user.username)
    print "Took %fs to get new images" % (time.time() - new_tic)

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
        return render_template('register.html', error="Passwords did not match")

    extra_letters = set(request.form['username']) - set(
        string.ascii_lowercase + string.ascii_uppercase + string.digits)

    if extra_letters:
        return render_template(
            'register.html', error="Please make sure username"
            " contains letters and digits only, no funny business.")

    user = User.new_user(request.form['username'],
        request.form['password'], request.form['email'])

    if user:
        user.dump()
        return render_template('login.html', welcome='Thanks for registering! Now log in below to get started.')
    else:
        return render_template('register.html', error="User already exists")


def load_user(username, password):

    user = User.from_id(username)

    if user and user.pw_correct(password):
        return user
    else:
        return None


@app.route('/')
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
    return redirect('/')


@app.before_request
def before_request():
    g.user = current_user


if __name__ == '__main__':
    app.secret_key = "\x7f\x83\x91\xb6O\x0b\x7f\xf4\xf3\xddD\x1b\xb5\x00|\x16\x90\x83U(E\xfb\x8as"
    import socket
    if socket.gethostname() == 'oisin':
        app.run(
            debug=debug,
            host="0.0.0.0",
            port=int("80")
        )
    else:
        app.run(debug=True)
