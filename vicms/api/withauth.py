'''
vicms-api: lightweight flexible REST-API routes for vicms.
supports multiple content per arch and authentication
'''

import json
import vicms.api as api
from vicms import Arch, cmroutes, route_rewrap
from flask import request, redirect, abort
from sqlalchemy.exc import IntegrityError

'''
api.withauth.Content Arch
'''
class SQLContent(api.SQLContent):

    def __init__(self,
            content_class,
            access_policy = {},
            default_ap = None,
            routes_disabled = [],
        ):
        '''initialize the content structure. a content structure is used by an arch to easily create API routes as well as the access policy and default access policy
        '''
        super().__init__(content_class, routes_disabled)

        for route, policy in access_policy.items():
            if policy:
                setattr(self, route, route_rewrap(policy, getattr(self, route)))

        if default_ap:
            # for k in ('select', 'select_one', 'insert', 'update', 'delete')
            for route in cmroutes:
                if route not in access_policy:
                    setattr(self, route, route_rewrap(default_ap, getattr(self, route)))
