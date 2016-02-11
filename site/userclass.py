import bcrypt
import yaml
import os
from datetime import datetime

class User():

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
