import bcrypt
import yaml
import os
from datetime import datetime

users_folder = '../data/users/'

class User():

    def __init__(self):
        pass

    @classmethod
    def new_user(cls, username, password, email):
        # check if user exists
        usernamepath = users_folder + username.lower() + '.yaml'
        if os.path.exists(usernamepath):
            print "Username exists"
            return None

        usr = cls()
        usr.username = username
        usr.id = username
        # hash password immediately
        usr.salt = bcrypt.gensalt()
        usr.hashed_password = bcrypt.hashpw(password.encode('utf-8'), usr.salt)
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
        fname = users_folder + id.lower() + '.yaml'
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

    def dump(self):
        fname = users_folder + self.username.lower() + '.yaml'
        yaml.dump(self.__dict__, open(fname, 'w'))

    def pw_correct(self, pw_guess):
        hashed_guess = bcrypt.hashpw(pw_guess.encode('utf-8'), self.salt)
        correct = self.hashed_password == hashed_guess
        print "Correct: ", correct
        return correct
