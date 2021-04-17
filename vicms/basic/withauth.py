'''
basic cms, custom user db with routes requiring login
used with flask-login
this can be used with viauth
supports multiple content per arch
'''
import vicms.basic as basic
from flask import render_template, request, redirect, abort, flash, url_for
from vicms import Arch, cmroutes, route_rewrap
#from flask_login import current_user, login_required

class SQLContent(basic.SQLContent):

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
                setattr(self, route, route_rewrap(policy, getattr(self, route)))

        if default_ap:
            # for k in ('select', 'select_one', 'insert', 'update', 'delete')
            for route in cmroutes:
                if route not in access_policy:
                    setattr(self, route, route_rewrap(default_ap, getattr(self, route)))
