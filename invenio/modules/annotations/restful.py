# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from flask import request
from flask.ext.restful import abort, Resource

from invenio.modules.annotations.api import get_annotations, get_jsonld_multiple
from invenio.modules.deposit.restful import require_header


class AnnotationsListResource(Resource):

    def get(self):
        annos = get_annotations(request.args.to_dict())
        return get_jsonld_multiple(annos, context={})

    @require_header('Content-Type', 'application/json')
    def post(self):
        rqj = request.json
        annos = get_annotations(rqj["query"])
        if "ldexport" in rqj:
            return get_jsonld_multiple(annos,
                                       context=rqj.get("context", "oaf"),
                                       new_context=rqj.get("new_context", {}),
                                       format=rqj.get("ldexport", "full"))
        return annos

    def put(self):
        abort(405)

    def delete(self):
        abort(405)

    def head(self):
        abort(405)

    def options(self):
        abort(405)

    def patch(self):
        abort(405)


def setup_app(app, api):
    api.add_resource(AnnotationsListResource, '/api/annotations/export/',)
