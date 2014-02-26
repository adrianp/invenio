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

from flask import g
from werkzeug.local import LocalProxy

from invenio.base.globals import cfg
from invenio.modules.jsonalchemy.wrappers import SmartJsonLD
from invenio.modules.jsonalchemy.jsonext.engines.mongodb_pymongo import \
    MongoDBStorage
from invenio.modules.jsonalchemy.jsonext.readers.json_reader import reader

from .models import Annotation as SQLAnnotation


def get_storage_engine():
    if not hasattr(g, "annotations_storage_engine"):
        g.annotations_storage_engine = \
            MongoDBStorage(SQLAnnotation.__name__,
                           host=cfg["CFG_ANNOTATIONS_MONGODB_HOST"],
                           port=cfg["CFG_ANNOTATIONS_MONGODB_PORT"],
                           database=cfg["CFG_ANNOTATIONS_MONGODB_DATABASE"])
    return g.annotations_storage_engine


class Annotation(SmartJsonLD):
    storage_engine = LocalProxy(get_storage_engine)

    @classmethod
    def create(cls, data, model='annotation', verbose=False):
        parsed = reader(data, model=model, namespace="annotationsext")
        dic = cls(parsed.translate())
        uuid = cls.storage_engine.save_one(dic.dumps())
        if verbose:
            del dic["__meta_metadata__"]
            print dic
        return uuid

    @classmethod
    def search(cls, query):
        return cls.storage_engine.search(query)

    def translate(self, context_name, ctx):
        dump = self.dumps()
        model = dump["__meta_metadata__"]['__additional_info__']['model'][0]
        res = {}
        if context_name == "oaf":
            from invenio.modules.accounts.models import User

            res["@id"] = cfg["CFG_SITE_URL"] + \
                "/api/annotations/export/?_id=" + \
                dump["_id"]
            res["@type"] = "oa:Annotation"

            u = User.query.filter(User.id == dump["who"]).one()
            res["annotatedBy"] = {
                "@id": cfg["CFG_SITE_URL"] +
                "/api/accounts/account/?id=" +
                str(u.id),
                "@type": "foaf:Person",
                "name": u.nickname,
                "mbox": {"@id": "mailto:" + u.email}}

            if model == "annotation":
                res["hasTarget"] = {
                    "@type": ["cnt:ContentAsXML", "dctypes:Text"],
                    "@id": cfg["CFG_SITE_URL"] + dump["where"],
                    "cnt:characterEncoding": "utf-8",
                    "format": "text/html"}
            elif model == "annotation_note":
                res["hasTarget"] = {
                    "@id": "oa:hasTarget",
                    "@type": "oa:SpecificResource",
                    "hasSource": cfg["CFG_SITE_URL"] + "/record/" +
                    str(dump["where"]["record"]),
                    "hasSelector":  {
                        "@id": "oa:hasSelector",
                        "@type": "oa:FragmentSelector",
                        "value": dump["where"]["marker"],
                        "dcterms:conformsTo": cfg["CFG_SITE_URL"] + "/api/annotations/notes_specification"}}

            res["motivatedBy"] = "oa:commenting"

            res["hasBody"] = {
                "@id": "oa:hasBody",
                "@type": ["cnt:ContentAsText", "dctypes:Text"],
                "chars": dump["what"],
                "cnt:characterEncoding": "utf-8",
                "format": "text/plain"}

            res["annotatedAt"] = dump["when"]
            return res
        raise NotImplementedError


def get_jsonld_multiple(annos, context="oaf", new_context={}, format="full"):
    return [Annotation(a).get_jsonld(context=context, new_context=new_context,
                                     format=format) for a in annos]


def add_annotation(model='annotation', **kwargs):
    Annotation.create(kwargs, model)


def get_annotations(which):
    return list(Annotation.search(which))
