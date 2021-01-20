'''
vial.py:
this file contains the implementation description/version that should be changed
upon every build
'''
from flask import Blueprint, flash
from collections import namedtuple

name = 'vicms'
version = '0.1.4'
description = 'vial-cms (vicms), a flask mini content management module using sqlalchemy'

AppArch = namedtuple('AppArch', ['bp'])

def make_blueprint(prefix=None):
    prefix = prefix if prefix else '/%s'%name
    bp = Blueprint(name, __name__, url_prefix=prefix)

    @bp.route('/about', methods=['GET'])
    def about():
        return '%s %s: %s, written by toranova\n' % (name, version, description)

    return bp
