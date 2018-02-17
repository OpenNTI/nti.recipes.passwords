#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that

import os
import unittest

import fudge

import zc.buildout.buildout
import zc.buildout.testing

from nti.recipes.passwords import DecryptSection


class NoDefaultBuildout(zc.buildout.testing.Buildout):
    # The testing buildout doesn't provide a way to
    # ignore local defaults, which makes it system dependent, which
    # is clearly wrong
    def __init__(self):
        zc.buildout.buildout.Buildout.__init__(
            self,
            '',
            [('buildout', 'directory', os.getcwd())],
            user_defaults=False)


class TestDecryptSection(unittest.TestCase):

    def test_no_file(self):
        # No verification, just sees if it runs
        buildout = NoDefaultBuildout()
        DecryptSection(buildout, 'passwords', {'base_passwd': ''})
        # buildout.print_options()

    @fudge.patch('getpass.getpass', 'nti.recipes.passwords._read', 'os.path.isfile')
    def test_decrypt_data(self, mock_getpass, mock_read, mock_isfile):

        ciphertext = (b'Salted__\xbe\x82\x11\xc4\x01\xe6\x94\xfc\x93\xb5\x8aF\xeb\x8chEy"'
                      b'\xd0\xb4\x04\xf3g\xb3.UX\x18\x17\x95\xe7 x7\x16\xa4{\x805~z\xe5\xad\xdc\xc4\xdc'
                      b'\xd43\x8e\xfd\xda\x108\xbfv\xf8yW\x1f\xd2\xd73j\x0f\xce\x0f(4\x95\xe3{&~{\xdf'
                      b'\x8ekm\xbb\x01\x17\xf28\x97\xd4\xfaSL\x99\xb5I\xfb\xc4\t\xb8\xeeH\x97\x02\\\xc8\xd6dw')

        mock_getpass.is_callable().returns('temp001')
        mock_read.is_callable().returns(ciphertext)
        mock_isfile.is_callable().returns(True)

        buildout = NoDefaultBuildout()
        options = {
            'file': 'foo.cast5'
        }

        DecryptSection(buildout, 'passwords', options)

        assert_that(options, has_entry('_input_mod_time', '0'))
        assert_that(options, has_entry('sql_passwd', 'rdstemp001'))
