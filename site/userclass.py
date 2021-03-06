import bcrypt
import yaml
import os
from datetime import datetime
import logging
logger = logging.getLogger()

users_folder = '../data/users/'

class User():

    def __init__(self):
        pass

    @classmethod
    def new_user(cls, username, password, email):
        # check if user exists
        usernamepath = users_folder + username.lower() + '.yaml'
        if os.path.exists(usernamepath):
            logger.info("Username %s exists" % username)
            return None

        usr = cls()
        usr.username = username
        usr.id = username
        # hash password immediately
        usr.salt = bcrypt.gensalt()
        usr.hashed_password = bcrypt.hashpw(password.encode('utf-8'), usr.salt)
        usr.email = email
        usr.registered_on = datetime.utcnow()
        usr.done_training = False  # each user has to complete all the training steps
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
        fname = users_folder + id.lower() + '.yaml'
        logger.info("Loading user %s" % id)
        # check user exists in our 'database'
        if os.path.exists(fname):
            # load user from file
            usr = User.from_dict(yaml.load(open(fname)))
            if not hasattr(usr, 'done_training'):
                usr.done_training = False
            return usr
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

    def dump(self):
        fname = users_folder + self.username.lower() + '.yaml'
        yaml.dump(self.__dict__, open(fname, 'w'))

    def pw_correct(self, pw_guess):
        hashed_guess = bcrypt.hashpw(pw_guess.encode('utf-8'), self.salt)
        correct = self.hashed_password == hashed_guess
        return correct
