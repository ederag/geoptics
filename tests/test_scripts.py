# -*- coding: utf-8 -*-

# Copyright (C) 2018 ederag <edera@gmx.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GeOptics; see the file LICENSE.txt.  If not, see
# <http://www.gnu.org/licenses/>.


import pytest


# global file marker
# The custom "script" marker is defined in the pytest section of setup.cfg
pytestmark = pytest.mark.script


def test_main(script_runner):
    ret = script_runner.run('geoptics', "--version")
    assert ret.success
    #assert ret.stdout == 'bar\n'
    assert ret.stderr == ''
