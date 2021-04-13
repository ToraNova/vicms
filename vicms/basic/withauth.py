'''
basic cms, custom user db with routes requiring login
used with flask-login
this can be used with viauth
supports multiple content per arch
'''
from flask import render_template, request, redirect, abort, flash, url_for
from vicms import Arch, cmroutes
from vicms.basic import Content
#from flask_login import current_user, login_required

# late-binding vs. early binding
# https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
def accesspol_route(policy, route, oldfunc):
    @policy
    def f(*args):
        return oldfunc(*args)
    return f

class Content(Content):

    def __init__(self, content_class,
            access_policy = {},
            default_ap = None,
            templates = {},
            reroutes = {},
            reroutes_kwarg = {},
            rex_callback = {},
            routes_disabled = []
        ):
        super().__init__(content_class, templates, reroutes, reroutes_kwarg, rex_callback, routes_disabled)

        for route, policy in access_policy.items():
            if policy:
                setattr(self, route, accesspol_route(policy, route, getattr(self, route)) )
                #self.__fctab[route] = accesspol_route(policy, route, self.__fctab[route])

        if default_ap:
            # for k in ('select', 'select_one', 'insert', 'update', 'delete')
            for route in cmroutes:
                if route not in access_policy:
                    setattr(self, route, accesspol_route(default_ap, route, getattr(self, route)))
                    #self.__fctab[route] = accesspol_route(default_ap, route, self.__fctab[route])

# nothing new added to arch, just a place holder to nicer importing
class Arch(Arch):
    pass
