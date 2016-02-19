Web-based image cropper
=======================

This is the front and back-end to a website designed to allow users to crop images. This is designed with crowd-sourcing annotations in mind.

Features:

- Allows for multiple user accounts
- Leaderboard
- All data saved as small separate .yaml files

Technologies used:

- cropper.js for the cropping
- Bootstrap
- Flask
- jQuery
- chartkick (for the leaderboard)

Python libraries you probably need:

- Flask
- Flask-login
- Yaml


Getting Started
---------------

    cd site
    python app.py

Then navigate your browser to the web address shown (probably `http://127.0.0.1:5000/`)
