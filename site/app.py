# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for, send_from_directory
import yaml
import os
import glob
from time import time
import bcrypt

# Initialize the Flask application
app = Flask(__name__)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import flash, redirect


from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g
from flask.ext.login import login_user , logout_user , current_user , login_required


from flask.ext.login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

global tic
tic = time()

debug = True

if debug:
    data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/sightings_subset/'
    yaml_name = 'sightings_subset.yaml'
else:
    data_dir = '/media/michael/Engage/data/butterflies/web_scraping/ispot/butterfly_subset/'
    yaml_name = 'butterflies.yaml'


def extract_latin_name(name):
    if '(' in name:# and ')' in name:
        return name.split('(')[1].split(')')[0].strip().lower()
    else:
        return name.lower()


def build_unlabelled_img_set():
    '''
    Returns set of unlabelled images, consisting of tuples of
    (sightingID, imageID)
    '''
    unlabelled_imgs = set()

    # yaml_paths = glob.glob(data_dir + '*/*meta.yaml')
    sighting_ids = yaml.load(
        open(data_dir + '../' + yaml_name), Loader=yaml.CLoader)

    for sighting_id, img_id, img_name in sighting_ids:

        # skip images with spaces, these are kind of broken
        if ' ' in img_id:
            continue

        meta = yaml.load(open(data_dir + sighting_id + '/meta.yaml'),
            Loader=yaml.CLoader)

        likely_id = extract_latin_name(meta['meta_tags']['likely_id'])

        # if likely_id != "pieris brassicae":
        #     continue

        crop_path = data_dir + sighting_id + '/' + img_id + '_crop.yaml'

        # could run glob.glob on data_dir just once to speed this up
        if not os.path.exists(crop_path):
            unlabelled_imgs.add((sighting_id, img_id, img_name))
        else:
            pass

    if len(unlabelled_imgs) == 0:
        print "No unlabelled images!"

    return unlabelled_imgs


global unlabelled_imgs
unlabelled_imgs = build_unlabelled_img_set()


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
        unlabelled_imgs = build_unlabelled_img_set()

        # now check again, if still empty then we're done
        if not unlabelled_imgs:
            return None, None, None

    return unlabelled_imgs.pop()


# Define a route for the default URL, which loads the form
@app.route('/')
@login_required
def form():
    """
    This is run the first time the page is loaded
    """
    global tic, unlabelled_imgs
    tic = time()
    T = get_new_images()
    print "T is ", T
    new_sighting_id, new_img_id, new_img_name = T
    return render_template('form_submit.html', sighting_id=new_sighting_id,
        img_id=new_img_name)


# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/', methods=['POST'])
@login_required
def form_submission():
    """
    This is run when the user clicks 'submit'
    """
    global tic

    # print "Getting form", request.form['option1']
    # get the results from the form
    results = {
        'number_butterflies': str(request.form['number_butterflies']),
        'time_taken': time() - tic
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

    print "Saving results to ", savepath
    with open(savepath, 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    # get a new image from the set of unlabelled images
    new_sighting_id, new_img_id, new_img_name = get_new_images()
    print "Loading : ", new_sighting_id, new_img_id

    if new_sighting_id is None:
        return render_template('form_finished.html')
    else:
        # start the clock and render the new page
        tic = time()
        print new_img_name
        return render_template('form_submit.html', sighting_id=new_sighting_id,
            img_id=new_img_name)


class User():
    # __tablename__ = "users"
    # id = db.Column('user_id',db.Integer , primary_key=True)
    # username = db.Column('username', db.String(20), unique=True , index=True)
    # password = db.Column('password' , db.String(10))
    # email = db.Column('email',db.String(50),unique=True , index=True)
    # registered_on = db.Column('registered_on' , db.DateTime)

    def __init__(self):
        pass

    @classmethod
    def new_user(cls, username, password, email):
        usr = cls()
        usr.username = username
        usr.id = username
        # hash password immediately
        usr.salt = bcrypt.gensalt()
        usr.hashed_password = bcrypt.hashpw(password, usr.salt)
        usr.email = email
        usr.registered_on = datetime.utcnow()
        return usr

    # overload init
    @classmethod
    def from_dict(cls, dic):
        usr = cls()
        usr.__dict__ = dic
        usr.id = usr.username
        return usr

    @classmethod
    def from_id(cls, id):
        foldername = '../users/'
        fname = foldername + id + '.yaml'
        print "Loading"
        # check user exists in our 'database'
        if os.path.exists(fname):
            # load user from file
            return  User.from_dict(yaml.load(open(fname)))
        else:
            return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r, pw: %s>' % (self.username, self.hashed_password)

    def dump(self, foldername='../users/'):
        fname = foldername + self.username + '.yaml'
        yaml.dump(self.__dict__, open(fname, 'w'))

    def pw_correct(self, pw_guess):
        hashed_guess = bcrypt.hashpw(pw_guess, self.salt)
        correct = self.hashed_password == hashed_guess
        print "Correct: ", correct
        return correct


@login_manager.user_loader
def load_user(id):
    return User.from_id(id)


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User.new_user(request.form['username'] , request.form['password'],request.form['email'])
    print user

    # todo - check if user exists

    user.dump()
    # db.session.add(user)
    # db.session.commit()
    flash('User successfully registered')
    print 'User successfully registered'
    return redirect(url_for('login'))


def load_user(username, password):

    user = User.from_id(username)

    if user and user.pw_correct(password):
        return user
    else:
        return None

@app.route('/index')
@login_required
def index():
    print "Username", g.user.username
    return render_template('index.html')


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
        flash('Username or Password is invalid' , 'error')

        return redirect(url_for('login'))
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
