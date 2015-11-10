# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for, send_from_directory
import yaml
import os
import random
from time import time

# Initialize the Flask application
app = Flask(__name__)

global tic
tic = time()

data_dir = ('/home/michael/projects/butterflies/data/web_scraping/'
            'ispot/sightings_subset/')


def build_unlabelled_img_set():
    '''
    Returns set of unlabelled images, consisting of tuples of
    (sightingID, imageID)
    '''
    unlabelled_imgs = set()

    for sighting_id in os.listdir(data_dir):

        meta = yaml.load(open(data_dir + sighting_id + '/meta.yaml'))

        for img_id in meta['ImageIds']:
            crop_path = data_dir + sighting_id + '/' + img_id + '_crop.yaml'

            if not os.path.exists(crop_path):
                unlabelled_imgs.add((sighting_id, img_id))

    return unlabelled_imgs


global unlabelled_imgs
unlabelled_imgs = build_unlabelled_img_set()


@app.route('/<sighting_id>/<img_id>')
def download_image(sighting_id, img_id):
    print sighting_id, img_id
    return send_from_directory(data_dir + sighting_id, img_id + '.jpg',
        as_attachment=True)


def get_new_images():
    global unlabelled_imgs

    if not unlabelled_imgs:
        # might have run out, or might have missed one. Check all the files...
        unlabelled_imgs = build_unlabelled_img_set()

        # now check again, if still empty then we're done
        if not unlabelled_imgs:
            return None, None

    return unlabelled_imgs.pop()


# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    """
    This is run the first time the page is loaded
    """
    global tic, unlabelled_imgs
    tic = time()
    new_sighting_id, new_img_id = get_new_images()
    return render_template('form_submit.html', sighting_id=new_sighting_id,
        img_id=new_img_id)


# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/', methods=['POST'])
def form_submission():
    """
    This is run when the user clicks 'submit'
    """

    global tic

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
    savepath = data_dir + sighting_id + '/' + img_id + '_crop.yaml'

    print "Saving results to ", savepath
    with open(savepath, 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    # get a new image from the set of unlabelled images
    new_sighting_id, new_img_id = get_new_images()
    print "Loading : ", new_sighting_id, new_img_id

    if new_sighting_id is None:
        return render_template('form_finished.html')
    else:
        # start the clock and render the new page
        tic = time()
        return render_template('form_submit.html', sighting_id=new_sighting_id,
            img_id=new_img_id)



# Run the app :)
if __name__ == '__main__':
    app.run(
        debug=True
        # host="0.0.0.0",
        # port=int("80")
    )
