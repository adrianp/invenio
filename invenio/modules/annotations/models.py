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

from invenio.ext.sqlalchemy import db

from invenio.modules.records.models import Record as Bibrec
from invenio.modules.accounts.models import User
from invenio.modules.comments.models import CmtRECORDCOMMENT
from invenio.base.globals import cfg
from sqlalchemy import event


class Annotation(db.Model):
    """Represents an annotation object inside a SQL database"""

    __tablename__ = 'annotation'

    id = db.Column(db.UUID,
                   primary_key=True)
    json = db.Column(db.JSON,
                     nullable=True)


class CmtNOTECOLLAPSED(db.Model):
    """Represents a CmtNOTECOLLAPSED record."""

    __tablename__ = 'cmtNOTECOLLAPSED'

    id = \
        db.Column(db.Integer(15, unsigned=True),
                  primary_key=True,
                  autoincrement=True,
                  nullable=False,
                  unique=True)

    id_bibrec = \
        db.Column(db.MediumInteger(8, unsigned=True),
                  db.ForeignKey(Bibrec.id),
                  primary_key=False,
                  nullable=False,
                  unique=False)

    # e.g., P1-F2 is the path for a note on Page 1, Figure 2
    path = \
        db.Column(db.Text,
                  primary_key=False,
                  nullable=False,
                  unique=False)

    id_user = \
        db.Column(db.Integer(15, unsigned=True),
                  db.ForeignKey(User.id),
                  primary_key=False,
                  nullable=False,
                  unique=False)


__all__ = ['CmtNOTECOLLAPSED']


@event.listens_for(CmtRECORDCOMMENT, 'after_insert')
def extract_notes(mapper, connection, target):
    if cfg['CFG_ANNOTATIONS_NOTES_ENABLED'] and target.star_score == 0:
        from .noteutils import extract_notes_from_comment
        revs = extract_notes_from_comment(target)
        if len(revs) > 0:
            from invenio.modules.annotations.api import add_annotation
            for rev in revs:
                add_annotation(model='annotation_note', **rev)
