#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import base64
import os
import shutil
import subprocess
import sys
import tempfile

'''
Procursus 2

INFO: Repacks deb as rootless with iphoneos-arm64 arch, moves legacy tweak dir to
       new directory, and resigns. Does not do any further modification.

original gist: https://gist.github.com/Teutates/ee52995cee1e6a6ee5a5c61466471b1f

'''

if not os.path.exists(os.path.join(os.getcwd(), 'CreatedDebs')): # check deb files Directory.
    os.makedirs(os.path.join(os.getcwd(), 'CreatedDebs'), exist_ok=True)  # Create deb files Directory.

tempDir_new = tempfile.mkdtemp() # Created /tmp/
tempDir_old = tempfile.mkdtemp() # Cretaed /tmp/
ldid = 'ldid -Hsha256'

class repack(object):
    def __init__(self):
        # self.check_dpkg_deb()  # checking installed dpkg-deb
        # self.check_fakeroot()  # checking installed fakeroot
        # self.check_file()  # checking installed file
        # self.check_ldid()  # checking installed ldid
        if os.path.exists(os.path.join(tempDir_old, 'var', 'jb')): # delete previous work directory and exit.
            print('deb already rootless. Skipping and exiting cleanly.')
            try:
                shutil.rmtree(tempDir_new)
                shutil.rmtree(tempDir_old)
            except:
                pass
            sys.exit(0)
        self.start_repack()
        self.clean()

    def check_dpkg_deb(self): # checking dpkg-deb
        if subprocess.Popen('type dpkg-deb', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].decode(errors='ignore') == '':
            print('Please install dpkg-deb.')

    def check_file(self): # checking file
        if subprocess.Popen('type file', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].decode(errors='ignore') == '':
            print('Please install file.')

    def check_fakeroot(self): # checking fakeroot
        if subprocess.Popen('type fakeroot', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].decode(errors='ignore') == '':
            print('Please install dpkg-deb.')

    def check_ldid(self): # checking ldid
        if not 'procursus' in subprocess.Popen('ldid', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].decode(errors='ignore'):
            print('Please install Procursus ldid.')

    def start_repack(self): # repacking start.
        subprocess.run('dpkg-deb -R {} {}'.format(sys.argv[1], tempDir_old), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.makedirs(os.path.join(tempDir_new, 'var', 'jb'), exist_ok=True) # create [TMPDIR]/var/jb

        shutil.copytree(os.path.join(tempDir_old, 'DEBIAN'), os.path.join(tempDir_new, 'DEBIAN')) # copying work directory from [TMPDIR].

        with open(os.path.join(tempDir_old, 'DEBIAN', 'control'), 'r', encoding='utf-8') as sed: # replace iphoneos-arm to iphoneos-arm64
            s = sed.read().replace('iphoneos-arm', 'iphoneos-arm64')
            if 'iphoneos-arm6464' in s:
                s = s.replace('iphoneos-arm6464', 'iphoneos-arm64')
            with open(os.path.join(tempDir_new, 'DEBIAN', 'control'), 'w', encoding='utf-8') as sedf:
                sedf.write(s) # write control file.
        try:
            shutil.rmtree(os.path.join(tempDir_old, 'DEBIAN')) # delete [TMPDIR]/DEBIAN
        except:
            pass

        for f in os.listdir(tempDir_old):
            try:
                shutil.move(os.path.join(tempDir_old, f), os.path.join(tempDir_new, 'var', 'jb', f)) # move all TMPDIR in files to working directory.
            except:
                pass
        if os.path.exists(os.path.join(tempDir_new, 'var', 'jb', 'Library', 'MobileSubstrate', 'DynamicLibraries')): # check "[work directory]/var/jb/Library/MobileSubstrate/DynamicLibraries" directory.
            os.makedirs(os.path.join(tempDir_new, 'var', 'jb', 'usr', 'lib'), exist_ok=True) # create directory to [Work Dir]/var/jb/usr/lib
            shutil.move(os.path.join(tempDir_new, 'var', 'jb', 'Library', 'MobileSubstrate', 'DynamicLibraries'), os.path.join(tempDir_new, 'var', 'jb', 'usr', 'lib', 'TweakInject')) # move "[work directory]/var/jb/Library/MobileSubstrate/DynamicLibraries" to "[work directory]/var/jb/usr/lib/TweakInject".

        for root, dirs, files in os.walk(tempDir_new): # scan work directory in all files.
            for file in files:
                if os.path.isfile(file):
                    if 'x-mach-binary; charset=binary' in subprocess.Popen('file -ib "{}"'.format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode(errors='ignore'):
                        INSTALL_NAME = subprocess.Popen(base64.b64decode('b3Rvb2wgLUQgInt9IiB8IGdyZXAgLXYgLWUgIjokIiAtZSAiXkFyY2hpdmUgOiIgfCBoZWFkIC1uMQ==').decode(errors='ignore').format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode(errors='ignore')
                        with open(os.path.join(tempDir_old, '._lib_cache'), 'w', encoding='utf-8') as f:
                            f.write(subprocess.Popen(base64.b64decode('b3Rvb2wgLUwgInt9IiB8IHRhaWwgLW4gKzIgfCBncmVwIC91c3IvbGliLydbXi9dJ1wqLmR5bGliIHwgY3V0IC1kJyAnIC1mMSB8IHRyIC1kICJbOmJsYW5rOl0i').decode(errors='ignore').format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode(errors='ignore'))
                        if 1 <= len(INSTALL_NAME):
                            subprocess.run(base64.b64decode('aW5zdGFsbF9uYW1lX3Rvb2wgLWlkIEBycGF0aC8iJChiYXNlbmFtZSAie30iKSIgInt9Ig==').decode(errors='ignore').format(INSTALL_NAME, os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if 'CydiaSubstrate' in subprocess.Popen('otool -L "{}"'.format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode(errors='ignore'):
                            subprocess.run(base64.b64decode('aW5zdGFsbF9uYW1lX3Rvb2wgLWNoYW5nZSAvTGlicmFyeS9GcmFtZXdvcmtzL0N5ZGlhU3Vic3RyYXRlLmZyYW1ld29yay9DeWRpYVN1YnN0cmF0ZSBAcnBhdGgvbGlic3Vic3RyYXRlLmR5bGliICJ7fSI=').decode(errors='ignore').format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if os.path.isfile(os.path.join(tempDir_old, '._lib_cache')) and not os.path.islink(os.path.join(tempDir_old, '._lib_cache')):
                            for line in open(os.path.join(tempDir_old, '._lib_cache'), 'r', encoding='utf-8').readlines():
                                subprocess.run(f'install_name_tool -change "{line}" @rpath/"$(basename "{line}")" "{line}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run('install_name_tool -add_rpath "/usr/lib" "{}"'.format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run('install_name_tool -add_rpath "/var/jb/usr/lib" "{}"'.format(os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subprocess.run('{} -s {}'.format(ldid, os.path.join(root, file)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(base64.b64decode('ZHBrZy1kZWIgLWIgInt9IiAiQ3JlYXRlZERlYnMvJChncmVwIFBhY2thZ2U6ICJ7fSIvREVCSUFOL2NvbnRyb2wgfCBjdXQgLWYyIC1kICcgJykiXyIkKGdyZXAgVmVyc2lvbjogInt9Ii9ERUJJQU4vY29udHJvbCB8IGN1dCAtZjIgLWQgJyAnKSJfIiQoZ3JlcCBBcmNoaXRlY3R1cmU6ICJ7fSIvREVCSUFOL2NvbnRyb2wgfCBjdXQgLWYyIC1kICcgJykiLmRlYg==').decode(errors='ignore').format(tempDir_new, tempDir_new, tempDir_new, tempDir_new), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # building deb file to "./CreatedDebs"

    def clean(self): # delete work directory and temp directory.
        print('Cleaning up')
        try:
            shutil.rmtree(os.path.join(tempDir_new))
            shutil.rmtree(os.path.join(tempDir_old))
        except:
            pass

if __name__ == '__main__':
    repack()
