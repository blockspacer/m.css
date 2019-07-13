#
#   This file is part of m.css.
#
#   Copyright © 2017, 2018, 2019 Vladimír Vondruš <mosra@centrum.cz>
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#

import os
import unittest

from typing import List

from . import BaseInspectTestCase
from python import EntryType, default_id_formatter

def custom_url_formatter(type: EntryType, path: List[str]) -> str:
    if type == EntryType.CLASS:
        filename = 'c.' + '.'.join(path) + '.html'
    elif type == EntryType.MODULE:
        filename = 'm.' + '.'.join(path) + '.html'
    elif type == EntryType.PAGE:
        filename = 'p.' + '.'.join(path) + '.html'
    elif type == EntryType.SPECIAL:
        filename = 's.' + '.'.join(path) + '.html'
    else: assert False

    return filename, filename + "#this-is-an-url"

def custom_id_formatter(type: EntryType, path: List[str]) -> str:
    if type == EntryType.FUNCTION:
        return 'f-' + '-'.join(path)
    if type == EntryType.OVERLOADED_FUNCTION:
        # Reuse the original hasher so we can test its behavior
        return 'o-' + default_id_formatter(type, path)
    if type == EntryType.PROPERTY:
        return 'p-' + '-'.join(path)
    if type == EntryType.ENUM:
        return 'e-' + '-'.join(path)
    if type == EntryType.ENUM_VALUE:
        return 'v-' + '-'.join(path)
    if type == EntryType.DATA:
        return 'd-' + '-'.join(path)

    assert False

class Test(BaseInspectTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(__file__, '', *args, **kwargs)

    def test(self):
        self.run_python({
            'INPUT_PAGES': ['page.rst'],
            'URL_FORMATTER': custom_url_formatter,
            'ID_FORMATTER': custom_id_formatter,
            'LINKS_NAVBAR1': [
                ('Pages', 'pages', []),
                ('Modules', 'modules', []),
                ('Classes', 'classes', [])],
            'LINKS_NAVBAR2': [('A page', 'page', []),
                              ('A module', 'link_formatting', []),
                              ('The class', ['link_formatting', 'Class'], [])],
            'PYBIND11_COMPATIBILITY': True
        })
        self.assertEqual(*self.actual_expected_contents('m.link_formatting.html'))
        self.assertEqual(*self.actual_expected_contents('m.link_formatting.sub.html'))
        self.assertEqual(*self.actual_expected_contents('c.link_formatting.Class.html'))
        self.assertEqual(*self.actual_expected_contents('c.link_formatting.Class.Sub.html'))

        # There's nothing inside p.page.html that wouldn't be already covered
        # by others
        self.assertTrue(os.path.exists(os.path.join(self.path, 'output/p.page.html')))

        self.assertEqual(*self.actual_expected_contents('s.classes.html'))
        self.assertEqual(*self.actual_expected_contents('s.modules.html'))
        self.assertEqual(*self.actual_expected_contents('s.pages.html'))

        # There's nothing inside s.index.html that wouldn't be already covered
        # by others
        self.assertTrue(os.path.exists(os.path.join(self.path, 'output/s.index.html')))

        # Verify pybind11 overloaded function hashing as well
        self.assertEqual(*self.actual_expected_contents('m.link_formatting.pybind.html'))
        self.assertEqual(*self.actual_expected_contents('c.link_formatting.pybind.Foo.html'))