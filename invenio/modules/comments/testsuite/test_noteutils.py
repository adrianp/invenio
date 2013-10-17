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

__revision__ = "$Id$"

from invenio.base.wrappers import lazy_import
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

EXTRACT_NOTES_FROM_COMMENT = \
    lazy_import('invenio.modules.comments.noteutils:extract_notes_from_comment')
MARKER_EXPAND_NAME = \
    lazy_import('invenio.modules.comments.noteutils:marker_expand_name')
MODEL_NOTE = \
    lazy_import('invenio.modules.comments.noteutils:model_note')
GET_ORIGINAL_COMMENT = \
    lazy_import('invenio.modules.comments.noteutils:get_original_comment')
GET_NOTE_TITLE = \
    lazy_import('invenio.modules.comments.noteutils:get_note_title')
PREPARE_NOTES = \
    lazy_import('invenio.modules.comments.noteutils:prepare_notes')


class TestExtractNotes(InvenioTestCase):
    """Tests for comment note extraction"""

    def test_extract_notes_from_comment(self):
        """Tests note extraction from single comments"""
        fun = EXTRACT_NOTES_FROM_COMMENT

        # marker collection tests; no corners or invalids here, just
        # [MARKER.LOCATION(S): BODY]
        self.assert_(fun('P.1: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('P.1,2,3: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '1,2,3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('P.1-3: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '1-3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('P.1-3,4: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '1-3,4',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('F.1: lorem ipsum dolor') ==
                     [{'marker': 'F',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('F.1a: lorem ipsum dolor') ==
                     [{'marker': 'F',
                       'location': '1a',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('F.1-3: lorem ipsum dolor') ==
                     [{'marker': 'F',
                       'location': '1-3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('F.1,2a,3: lorem ipsum dolor') ==
                     [{'marker': 'F',
                       'location': '1,2a,3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('G: lorem ipsum dolor') ==
                     [{'marker': 'G',
                       'location': None,
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('L.1: lorem ipsum dolor') ==
                     [{'marker': 'L',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('L.1-3: lorem ipsum dolor') ==
                     [{'marker': 'L',
                       'location': '1-3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('E.1: lorem ipsum dolor') ==
                     [{'marker': 'E',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('E.1,2,3: lorem ipsum dolor') ==
                     [{'marker': 'E',
                       'location': '1,2,3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('T.1: lorem ipsum dolor') ==
                     [{'marker': 'T',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('T.1,2,3: lorem ipsum dolor') ==
                     [{'marker': 'T',
                       'location': '1,2,3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('S.1: lorem ipsum dolor') ==
                     [{'marker': 'S',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('S.1.1: lorem ipsum dolor') ==
                     [{'marker': 'S',
                       'location': '1.1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('S.1a: lorem ipsum dolor') ==
                     [{'marker': 'S',
                       'location': '1a',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('S.1,2a,3: lorem ipsum dolor') ==
                     [{'marker': 'S',
                       'location': '1,2a,3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('PP.1: lorem ipsum dolor') ==
                     [{'marker': 'PP',
                       'location': '1',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('PP.1,2: lorem ipsum dolor') ==
                     [{'marker': 'PP',
                       'location': '1,2',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('PP.1-3: lorem ipsum dolor') ==
                     [{'marker': 'PP',
                       'location': '1-3',
                       'body': 'lorem ipsum dolor'}])
        self.assert_(fun('P.1: F.2: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '1',
                       'body': {'marker': 'F',
                                'location': '2',
                                'body': 'lorem ipsum dolor'}}])
        self.assert_(fun('P.10: R.[Ellis98]: lorem ipsum dolor') ==
                     [{'marker': 'P',
                       'location': '10',
                       'body': {'marker': 'R',
                                'location': '[Ellis98]',
                                'body': 'lorem ipsum dolor'}}])

        # corner cases
        self.assert_(fun('P.1: A comment on page 1\n\nsome bla bla\nF.12: A comment on figure 12') ==
                     [{'marker': 'P',
                       'location': '1',
                       'body': 'A comment on page 1'},
                      {'marker': 'F',
                       'location': '12',
                       'body': 'A comment on figure 12'}])
        self.assert_(fun('This comment has no notes') == [])
        self.assert_(
            fun('P.1:A comment on page 1\nF.12: A comment on figure 12') ==
            [{'marker': 'P',
              'location': '1',
              'body': 'A comment on page 1'},
             {'marker': 'F',
              'location': '12',
              'body': 'A comment on figure 12'}])
        self.assert_(fun('bla bla\nF.123a: A comment on a subfigure') ==
                     [{'marker': 'F',
                       'location': '123a',
                       'body': 'A comment on a subfigure'}])
        self.assert_(fun('') == [])

        # invalid notes tests
        self.assert_(fun('P.1 An invalid page marker (no column)\n\nF.123a: A comment on a subfigure') ==
                     [{'marker': 'F',
                       'location': '123a',
                       'body': 'A comment on a subfigure'}])

    def test_marker_expand_name(self):
        """Tests marker shortname expansion"""
        fun = MARKER_EXPAND_NAME
        self.assert_(fun() is None)
        self.assert_(fun('P') == 'Page')
        self.assert_(fun('F') == 'Figure')
        self.assert_(fun('G') == 'General aspect')
        self.assert_(fun('L') == 'Line')
        self.assert_(fun('R') == 'Reference')
        self.assert_(fun('E') == 'Equation')
        self.assert_(fun('T') == 'Table')
        self.assert_(fun('S') == 'Section')
        self.assert_(fun('THIS_IS_NOT_A_MARKER') is None)

    def test_model_note(self):
        """Tests note conversion from JSON to CmtNOTE"""
        note = MODEL_NOTE({'marker': 'P', 'location': '1', 'body': 'lorem'})
        self.assert_(note.marker_type == 'P')
        self.assert_(note.marker_location == '1')
        self.assert_(note.body == 'lorem')
        self.assert_(note.child_note is None)

        note = MODEL_NOTE({'marker': 'G', 'location': None, 'body': 'lorem'})
        self.assert_(note.marker_type == 'G')
        self.assert_(note.marker_location is None)
        self.assert_(note.body == 'lorem')

        note = MODEL_NOTE({'marker': 'P',
                           'location': '1',
                           'body': {'marker': 'F',
                                    'location': '2a',
                                    'body': 'lorem'}})

        self.assert_(note.child_note is not None)
        self.assert_(note.child_note.marker_type == 'F')
        self.assert_(note.child_note.marker_location == '2a')
        self.assert_(note.child_note.body == 'lorem')
        self.assert_(note.child_note.parent_note is not None)
        self.assert_(note.child_note.parent_note.marker_type == 'P')
        self.assert_(note.child_note.parent_note.marker_location == '1')
        self.assert_(note.child_note.parent_note.body is None)

        note = MODEL_NOTE({'location': '1', 'body': 'lorem'})
        self.assert_(note is None)

    def test_get_original_comment(self):
        """Tests if the original comment of the notes is correctly retrieved"""
        fun = GET_ORIGINAL_COMMENT
        note = MODEL_NOTE({'marker': 'P',
                           'location': '1',
                           'body': {'marker': 'F',
                                    'location': '2a',
                                    'body': 'lorem'}})
        self.assert_(fun(note) is None)
        self.assert_(fun(note.child_note) is None)
        note.cmtRECORDCOMMENT = 1
        self.assert_(fun(note) == 1)
        self.assert_(fun(note.child_note) == 1)

    def test_get_note_title(self):
        """Test note title expansion"""
        fun = GET_NOTE_TITLE
        self.assert_(fun('P.1') == 'Page 1')
        self.assert_(fun('F.2a') == 'Figure 2a')
        self.assert_(fun('G') == 'General aspect')
        self.assert_(fun('X') is None)
        self.assert_(fun('E') == 'Equation')

    def test_prepare_notes(self):
        """Test note tree preparation"""
        tree = PREPARE_NOTES([
            MODEL_NOTE({'marker': 'P', 'location': '1', 'body': 'lorem'}),
            MODEL_NOTE({'marker': 'P',
                        'location': '1',
                        'body': {'marker': 'F',
                                 'location': '2a',
                                 'body': 'ipsum'}}),
            MODEL_NOTE({'marker': 'G', 'location': None, 'body': 'dolor'}),
            MODEL_NOTE({'marker': 'G', 'location': None, 'body': 'elit'}),
            MODEL_NOTE({'marker': 'G',
                        'location': None,
                        'body': {'marker': 'T',
                                 'location': '4',
                                 'body': 'adipisicing'}}),
            MODEL_NOTE({'marker': 'E',
                        'location': '4',
                        'body':
                        'sit amet'}),
            MODEL_NOTE({'marker': 'E',
                        'location': '4',
                        'body': 'consectetur'})])

        self.assert_(tree['P.1']['root'][0].body == 'lorem')
        self.assert_(len(tree['E.4']['root']) == 2)
        self.assert_(tree['E.4']['root'][0].body == 'sit amet')
        self.assert_(tree['E.4']['root'][1].body == 'consectetur')
        self.assert_(tree['G']['toggle'] == 'G')
        self.assert_(tree['P.1']['F.2a']['toggle'] == 'P.1-F.2a')
        self.assert_(tree['P.1']['F.2a']['root'][0].body == 'ipsum')
        self.assert_(len(tree['G']['root']) == 2)
        self.assert_(tree['G']['T.4']['toggle'] == 'G-T.4')

TEST_SUITE = make_test_suite(TestExtractNotes)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
