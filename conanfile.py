#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException


class FfiConan(ConanFile):
    """
    Builds libffi, only tested on linux and cross-compiling to arm.  By default
    this builds the static and shared ffi libs.
    """

    name        = 'ffi'
    version     = '3.2.1'
    license     = 'https://github.com/libffi/libffi/blob/master/LICENSE'
    url         = 'https://raw.githubusercontent.com/kheaactua/conan-ffi/v3.2.1/conanfile.py'
    description = 'Compilers for high level languages generate code that follow certain conventions.'
    settings    = 'os', 'compiler', 'build_type', 'arch'
    requires    = 'helpers/[>= 0.3.0]@ntc/stable',

    def build_requirements(self):
        pack_names = None
        if tools.os_info.linux_distro == 'ubuntu':
            pack_names = ['texinfo', 'autoconf', 'libtool']

            if self.settings.arch == 'x86':
                full_pack_names = []
                for pack_name in pack_names:
                    full_pack_names += [pack_name + ':i386']
                pack_names = full_pack_names

        if pack_names:
            try:
                installer = tools.SystemPackageTool()
                installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not install build requirements')

    def source(self):
        g = tools.Git(folder=self.name)
        g.clone('https://github.com/libffi/libffi', branch='v%s'%self.version)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        with tools.chdir(self.name):
            self.run('./autogen.sh', win_bash=tools.os_info.is_windows)
            autotools.configure(args=['--prefix=%s'%self.package_folder])
            autotools.make()
            autotools.make(args=['install'])

    def package_info(self):
        self.cpp_info.libs = ['ffi']
        self.env_info.MANPATH.append(os.path.join(self.package_folder, 'share', 'man'))

        # Populate the pkg-config environment variables
        with tools.pythonpath(self):
            from platform_helpers import adjustPath, appendPkgConfigPath

            self.env_info.PKG_CONFIG_LIBFFI_PREFIX = adjustPath(self.package_folder)
            appendPkgConfigPath(adjustPath(os.path.join(self.package_folder, 'lib', 'pkgconfig')), self.env_info)


# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
