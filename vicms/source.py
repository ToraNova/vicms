from flask import Blueprint, flash
from vicms import vial
from collections import namedtuple

AppArch = namedtuple('AppArch', ['bp'])

def make_blueprint(content_name, prefix=None):
    prefix = prefix if prefix else vial.name
    bp = Blueprint(content_name, __name__, url_prefix='/%s/%s'%(prefix,content_name))

    @bp.route('/about', methods=['GET'])
    def about():
        return '%s %s: %s\n' % (vial.name, vial.version, vial.description)

    return bp

def eflash(exception):
    flash("an exception (%s) has occurred: %s" % (type(exception).__name__, str(exception)), 'err')

def emflash(msg):
    flash(msg, 'err')

def sflash(msg):
    flash(msg, 'ok')

def wflash(msg):
    flash(msg, 'warn')
