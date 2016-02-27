# unit tests for SWAPY's tools.
# Copyright (C) 2016 Matiychuk D.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA


import unittest
import tools


class ToolsTestCase(unittest.TestCase):

    def test_show_error_message(self):
        try:
            0 / 0
        except ZeroDivisionError:
            pass

        self.assertRaises(ZeroDivisionError, tools.show_error_message)

    def test_object_to_text(self):
        str_text = str('asdfghjkl')
        text = tools.object_to_text(str_text)
        self.assertEquals(str_text, text)
        self.assertTrue(isinstance(text, str))

        u_text = unicode('asdfghjkl')
        text = tools.object_to_text(u_text)
        self.assertEquals(u_text, text)
        self.assertTrue(isinstance(text, unicode))

        list_text = ['as', 'dfgh', 'jkl']
        text = tools.object_to_text(list_text)
        self.assertEquals(str(list_text), text)
        self.assertTrue(isinstance(text, str))

        class InvalidItem(object):
            def __repr__(self):
                return u'bats\u00E0'
        invalid_object = [InvalidItem() for i in range(3)]
        self.assertRaises(UnicodeEncodeError, lambda: str(invalid_object))
        self.assertEquals("[u'bats\\xe0', u'bats\\xe0', u'bats\\xe0']",
                          tools.object_to_text(invalid_object))
