import yaml
import string
import os
import glob
import time
import socket

from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g, Blueprint, send_from_directory, make_response
from flask.ext.login import login_user , logout_user , current_user , login_required
from flask.ext.login import LoginManager

from butterfly_file_handlers import build_unlabelled_img_set, get_user_counts, getpaths, logfilename
from userclass import User

import chartkick
import logging
logging.basicConfig(level=logging.DEBUG, filename=logfilename())
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger()


# Initialize the Flask application and login manager
app = Flask(__name__)
app.config.from_object("config")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


# adding chartkick
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

# setting some constants
debug = False
training_debug = False
if socket.gethostname() == 'oisin' and training_debug:
    raise Exception("Should not be allowed")

num_labellers_required_per_image = 3
data_dir, yaml_name = getpaths(debug)

# creating the list of unlabelled images
global unlabelled_imgs
unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)


def get_new_images(username):
    '''
    Returns a tuple with info about an image suitable for this user to label
    '''
    logger.info("Checking for new images")
    global unlabelled_imgs

    if not unlabelled_imgs:
        # might have run out, or might have missed one. Check all the files...
        logger.info("Checking again for new images")
        unlabelled_imgs = build_unlabelled_img_set(data_dir, yaml_name)

        # now check again, if still empty then we're done
        if not unlabelled_imgs:
            logger.critical("Can't find any more unlabelled images")
            return None, None, None

    # iterate until we have found one that this user hasn't labelled
    for (sighting_id, img_id), tmp in unlabelled_imgs.iteritems():
        if username not in tmp['labellers']:
            return sighting_id, img_id, tmp['img_name']

    logger.warning("No more unlabelled images for user %s" % username)

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
        logger.info("Removing image %s, %s" % (sighting_id, img_id))
        del unlabelled_imgs[(sighting_id, img_id)]


# this gets a specific image file, and is used in the form_submit.html
@app.route('/<sighting_id>/<img_id>')
def download_image(sighting_id, img_id):
    return send_from_directory(data_dir + sighting_id, img_id,
        as_attachment=True)

# giving robots.txt to prevent crawlers
@app.route('/robots.txt')
def robots():
    logger.info("Robots page requested")
    response = make_response("User-agent: *\nDisallow: /")
    response.headers["content-type"] = "text/plain"
    return response


@app.route('/training')
@login_required
def training():

    if session['training_step'] <= 5:

        logger.info("User %s on training step : %d" % (
            g.user.username, session['training_step']))

        return render_template('form_submit.html', sighting_id='', img_id='',
            training_step=session['training_step'])

    elif session['training_step'] == 6:
        session['training_step'] += 1
        return redirect(url_for('training'))

    else:
        # let's startin a new training session
        session['training_step'] = 1

        return render_template('form_submit.html', sighting_id='', img_id='',
            training_step=session['training_step'])


# Define a route for the default URL, which loads the form
@app.route('/cropper')
@login_required
def cropper():
    '''This is run the first time the page is loaded'''

    if session['training_step'] < 6:
        if g.user.done_training:
            # ok, the user is allowed to quit
            session['training_step'] = 8
        else:
            # naughty - redirect back to training
            return redirect(url_for('training'))

    logger.info("First time loading cropper for user %s" % g.user.username)
    new_sighting_id, new_img_id, new_img_name = get_new_images(g.user.username)

    if new_sighting_id is None:
        return render_template('form_finished.html')
    else:
        # start the clock and render the new page
        session['tic'] = time.time()
        logger.info("Serving %s, %s to user %s" % (
            new_sighting_id, new_img_name, g.user.username))
        return render_template('form_submit.html',
                               sighting_id=new_sighting_id,
                               img_id=new_img_name,
                               training_step=session['training_step'])


@app.route('/leaderboard')
def leaderboard():
    logging.info("Serving leaderboard")
    user_counts = get_user_counts(data_dir)
    user_counts = [[str(xx), float(yy)] for xx, yy in user_counts][::-1]
    return render_template('leaderboard.html', user_counts=user_counts)


@app.route('/cropper', methods=['POST'])
@login_required
def form_submission():
    '''This is run when the user clicks 'submit', with a POST request'''

    session['training_step'] += 1
    if session['training_step'] < 6:
        return redirect(url_for('training'))

    elif session['training_step'] == 6:

        # we've just finished training
        logger.info("User %s finished training" % g.user.username)

        if g.user.done_training:
            # we've done training before
            return redirect('/')
        else:
            # first time training
            g.user.done_training = True
            g.user.dump()
            return redirect(url_for('cropper'))

    # get the results from the form
    results = {
        'number_butterflies': str(request.form['number_butterflies']),
        'time_taken': time.time() - session['tic'],
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

    try:
        savepath = data_dir + sighting_id + '/' + \
            img_id.split('.')[0] + '_' + g.user.username + '_crop.yaml'

        remember_user_labelling(
            sighting_id, img_id.split('.')[0], g.user.username)

        logging.info("Saving crop to %s" % savepath)
        with open(savepath, 'w') as f:
            yaml.dump(results, f)

    except Exception as e:
        # todo - log this
        logger.error("Failed to save " + str(e))
        logger.error("Sighting id: %s image id: %s " % (sighting_id, img_id))

    # get a new image from the set of unlabelled images
    new_tic = time.time()
    new_sighting_id, new_img_id, new_img_name = get_new_images(g.user.username)
    logger.info("Took %fs to get new images" % (time.time() - new_tic))

    return redirect(url_for('cropper'))


@app.errorhandler(500)
def error500(e):
    return render_template('500.html'), 500


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
        logger.info("Failed to register user %s" % request.form['username'])
        return render_template(
            'register.html', error="Please make sure username"
            " contains letters and digits only, no funny business.")

    user = User.new_user(request.form['username'],
        request.form['password'], request.form['email'])

    if user:
        logger.info("Registered new user %s" % user.username)
        user.dump()
        return redirect(url_for('login', welcome=True))
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
        return render_template('login.html', welcome=request.args.get('welcome'))

    username = request.form['username']
    password = request.form['password']
    registered_user = load_user(username, password)

    if registered_user is None:
        logger.warning("Incorrect username or pw: %s" % username)
        return render_template('login.html', error = "Error - Username or Password is invalid")

    # setting this here so new users are immediately taken to training
    if registered_user.done_training:
        session['training_step'] = 8
    else:
        session['training_step'] = 1

    login_user(registered_user)
    logger.info("User %s logged in successfully" % username)
    return redirect('/')


@app.before_request
def before_request():
    g.user = current_user


if __name__ == '__main__':
    app.secret_key = "\x7f\x83\x91\xb6O\x0b\x7f\xf4\xf3\xddD\x1b\xb5\x00|\x16\x90\x83U(E\xfb\x8as"
    logger.info("Started app")
    if socket.gethostname() == 'oisin':
        app.run(
            debug=False,
            host="0.0.0.0",
            port=int("80")
        )
    elif socket.gethostname() == 'biryani':
        app.run(debug=True)
    else:
        raise Exception("Unknown host")
