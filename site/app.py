# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for, send_from_directory
import yaml
import os
import random
from time import time

data_dir = 'test_site_data/imgs'

# Initialize the Flask application
app = Flask(__name__)

global tic
tic = time()


def get_unlabelled_img():
    """
    Returns label of a single unlabelled image
    """
    return random.choice(['12', '34', '10299'])
    for folder in os.listdir(data_dir):
        if not os.path.exists(data_dir + folder + '/crop.yaml'):
            return folder

@app.route('/test_site_data/')
def download_image(filename='34.jpg'):
    print filename
    return send_from_directory('test_site_data/', filename, as_attachment=True)

# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    global tic
    tic = time()
    new_img = get_unlabelled_img()
    print "in form", new_img
    return render_template('form_submit.html', img=new_img,
        imagename=new_img + ".jpg")

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    # name=request.form['yourname']
    # email=request.form['youremail']
    global tic

    results = {
        'number_butterflies': str(request.form['number_butterflies']),
        'top_bottom': str(request.form['topbottom']),
        'time_taken': time() - tic
    }
    try:
        results['crop']= {
            'x': float(request.form['x']),
            'y': float(request.form['y']),
            'width': float(request.form['width']),
            'height': float(request.form['height'])
            }
    except:
        pass
    print results
    with open('crop.yaml', 'w') as f:
        yaml.dump(results, f, default_flow_style=False)

    new_img = get_unlabelled_img()
    print "in hello", new_img

    tic = time()
    return render_template('form_submit.html', img=new_img,
        imagename=new_img + ".jpg")

# Run the app :)
if __name__ == '__main__':
  app.run(
  debug=True
        # host="0.0.0.0",
        # port=int("80")
  )
