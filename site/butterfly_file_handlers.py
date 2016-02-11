import yaml
import os

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
