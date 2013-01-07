#!/usr/bin/env python

from setuptools import setup

setup(name='pyrepresent',
      version='0.1',
      description='Client library for represent.opennorth.ca',
      author='Nicolas Cadou',
      author_email='ncadou@cadou.ca',
      url='https://github.com/ncadou/pyrepresent',
      keywords='canada politics democracy',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Other/Nonlisted Topic',  # Politics
          ],
      packages=['represent'],
      install_requires=['requests'],
     )
