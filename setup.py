import os
from setuptools import setup, find_packages

version = __import__('phoenix').__version__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

reqs = [line.strip() for line in open('requirements.txt')]

setup(name='Phoenix',
      version=version,
      description='Phoenix',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Development Status :: 4 - Beta",
      ],
      author='Birdhouse Developers',
      author_email='',
      url='https://github.com/bird-house/pyramid-phoenix.git',
      license='Apache License 2.0',
      keywords='web buildout pyramids phoenix birdhouse wps pywps esgf',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='phoenix',
      install_requires=reqs,
      entry_points="""\
      [paste.app_factory]
      main = phoenix:main
      """,
      )
