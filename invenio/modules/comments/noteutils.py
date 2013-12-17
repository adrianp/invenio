# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

""" Utils for extracting notes from comments and manipulating them."""

import re

from flask.ext.login import current_user

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db


# a note location can have one of the following structures (sans markers):
# P.1, P.1,3,7 (multiple locations), P.1-3 (interval locations),
# F.1a (sub-locations), T.1.1-2.3 (interval with sub-locations)
LOCATION = r'[\w\.]+(?:[\,\-][\w\.]+)*'


# the note markers; references have a special type of location, e.g. "[Ellis98]"
MARKERS = {
    'P': {'longname': _('Page'), 'regex': r'[P]\.' + LOCATION},
    'F': {'longname': _('Figure'), 'regex': r'[F]\.' + LOCATION},
    'G': {'longname': _('General aspect'), 'regex': r'[G]'},
    'L': {'longname': _('Line'), 'regex': r'[L]\.' + LOCATION},
    'E': {'longname': _('Equation'), 'regex': r'[E]\.' + LOCATION},
    'T': {'longname': _('Table'), 'regex': r'[T]\.' + LOCATION},
    'S': {'longname': _('Section'), 'regex': r'[S]\.' + LOCATION},
    'PP': {'longname': _('Paragraph'), 'regex': r'[P]{2}\.' + LOCATION},
    'R': {'longname': _('Reference'),
          'regex': r'[R]\.' +
                   r'[\[][\w]+[\]](?:[\,\-][\[][\w]+[\]])*'}
}


# description of the notes' markup, to be used in GUI
# FIXME: move to Jinja2 template
HOWTO = _("To leave a note use the following syntax:<br>\
P.1: a note on page one<br>\
P.1-3: a note on pages one to three<br>\
P.1-3,5: a note on pages one to three and five<br>\
F.2a: a note on subfigure 2a<br>\
P.1: T.2: L.3: a note on the third line of table two, which appears on the first page<br>\
G: a note on the general aspect of the paper<br>\
R.[Ellis98]: a note on a reference<br><br>\
The available markers are:")

for KEY, VALUE in MARKERS.items():
    HOWTO += '<br>' + KEY + ' - ' + VALUE['longname']


# concatenate all regexes in MARKERS
MARKER_REGEX = [r'(']
for m in MARKERS.keys():
    MARKER_REGEX += MARKERS[m]['regex'] + '|'
MARKER_REGEX[len(MARKER_REGEX) - 1] = r')+'  # remove the final OR
MARKER_REGEX = "".join(MARKER_REGEX)


# notes should be delimited by a newline; we do not want to extract this
# part, so we use a non-capturing group `?:`
PREFIX = r'(?:^|\n)+'


# a note prefix should be followed by a column and optional whitespace
SUFFIX = r'[\:][\s]*'


# the actual text; can be anything
TEXT = r'(.+)'


def extract_notes_from_comment(comment):
    """Extracts notes from a comment.

    Notes are one-line blocks of text preceded by MARKERS and locations (page
    numbers, figure names etc.).

    Args:
        comment: the comment to parse
    Returns:
        the list of parsed notes in the following JSON form:
            {
             'marker': String,
             'location': String,
             'body': JSON|String
            }
        if the 'body' is a JSON it means that the note has a child
    """
    notes = re.findall(PREFIX + MARKER_REGEX + SUFFIX + TEXT, comment)
    result = []
    for note in notes:
        # recursively search for sub-notes; for example "P.1: F.2: a note on
        # page one, figure two" is a valid note
        sub_note = extract_notes_from_comment(note[1])
        if len(sub_note) > 0:
            body = sub_note[0]
        else:
            # no child notes
            body = note[1]
        # split MARKER from LOCATION; location might be empty if this is a
        # general note ('G' marker)
        where = note[0].split('.', 1)
        result.append({'marker': where[0],
                       'location': where[1] if len(where) == 2 else None,
                       'body': body})
    return result


def model_note(json):
    """Converts a note from JSON to a CmtNOTE object.

    Args:
        json: the json to parse
    Return:
        a CmtNOTE
    """
    from .models import CmtNOTE
    try:
        result = CmtNOTE()
        result.marker_type = json['marker']
        result.marker_location = json['location']

        if type(json['body']) == dict:
            # we need to model child notes also
            result.child_note = model_note(json['body'])
        else:
            # no child note
            result.body = json['body']
        return result
    except KeyError:
        # invalid input JSON
        return None


def get_original_comment(note):
    """Fetches the original comment of the note; in case of hierarchic notes, it
    goes up to the parent.

    Args:
        note: the note
    Returns:
        the comment in which the note appeared
    """
    while note.parent_note:
        note = note.parent_note
    return note.cmtRECORDCOMMENT


def marker_expand_name(short=None):
    """Fetches the long names for markers.

    Args:
        short: short name to be converted
    Returns:
        the long name of the marker
    """
    try:
        return MARKERS[short]['longname']
    except KeyError:
        # inexistent marker
        return None


def get_note_title(location):
    """Convert a note/ marker combination to a human readable string.

    Args:
        location: the note/ marker combination
    Returns:
        the human-readable location
    """
    location = location.split('.')
    # certain marker types might not require a location, hence else ''
    marker = marker_expand_name(location[0])
    if marker:
        return marker + (' ' + location[1] if len(location) > 1 else '')
    else:
        return None


def prepare_notes(notes, tree=None, path=None):
    """Prepares the notes for display by nesting them.

    Args:
        notes: the notes to prepare
    Returns:
        the prepared notes
    """
    if not tree:
        tree = {}
    for note in notes:
        key = note.marker_type
        if note.marker_location:
            # certain marker types, such as General, do not have a location
            key += '.' + note.marker_location

        # path used for toggling collapsed/ expanded (HTML element IDs)
        current_path = ""
        if path:
            current_path += path + "-" + key
        else:
            current_path = key

        if not key in tree:
            tree[key] = {}
            tree[key]['toggle'] = current_path

        if note.child_note:
            # update the current key with another one containing the child notes
            tree[key] = prepare_notes([note.child_note],
                                      tree[key],
                                      current_path)
        else:
            if 'root' not in tree[key]:
                tree[key]['root'] = []
            tree[key]['root'].append(note)
    return tree


def note_collapse(id_bibrec, path):
    """Collapses note category for user."""
    from .models import CmtNOTECOLLAPSED
    collapsed = CmtNOTECOLLAPSED(id_bibrec=id_bibrec,
                                 path=path,
                                 id_user=current_user.get_id())
    try:
        db.session.add(collapsed)
        db.session.commit()
    except:
        db.session.rollback()


def note_expand(id_bibrec, path):
    """Expands note category for user."""
    from .models import CmtNOTECOLLAPSED
    CmtNOTECOLLAPSED.query.filter(db.and_(
        CmtNOTECOLLAPSED.id_bibrec == id_bibrec,
        CmtNOTECOLLAPSED.path == path,
        CmtNOTECOLLAPSED.id_user == current_user.get_id())).\
        delete(synchronize_session=False)


def note_is_collapsed(id_bibrec, path):
    """Checks if a note category is collapsed."""
    from .models import CmtNOTECOLLAPSED
    return CmtNOTECOLLAPSED.query.filter(db.and_(
        CmtNOTECOLLAPSED.id_bibrec == id_bibrec,
        CmtNOTECOLLAPSED.path == path,
        CmtNOTECOLLAPSED.id_user == current_user.get_id())).count() > 0
