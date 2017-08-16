#!/usr/bin/env python

from setuptools import setup, find_packages
import statsroyale

with open("README.rst", "r") as f:
    long_description = f.read()

setup(name='statsroyale',
      version=statsroyale.__version__,
      description='Python library to fetch information from StatsRoyale.com',
      long_description=long_description,
      author='Atulya Bisht',
      author_email='atulya2109@gmail.com',
      packages = find_packages(),
      #entry_points={
      #      'console_scripts': [
      #            'statsroyale = statsroyale.statsroyale:command_line',
      #      ]
      #},
      url='https://www.github.com/atulya2019/Stats-Royale-Python',
      keywords=['stats', 'royale', 'clash-royale', 'api', 'library', 'unofficial', 'supercell', 'game'],
      license='MIT',
      download_url='https://github.com/atulya2019/Stats-Royale-Python/v' + statsroyale.__version__ + '.tar.gz',
      classifiers=[],
      install_requires=[
            'BeautifulSoup4',
      ]
)
