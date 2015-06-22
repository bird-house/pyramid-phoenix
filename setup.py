import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid>=1.5.7',
    'pyramid-chameleon',
    'pyramid-mako',
    'pymongo',
    'pyramid_layout',
    'pyramid_deform',
    'pyramid_beaker',
    'pyramid_mailer',
    'pyramid_deform',
    #'pyramid_persona',
    'pyramid_ldap',
    'deform>=2.0a2',
    'js.deform',
    'js.bootstrap',
    'PasteDeploy',
    'authomatic',
    'python-openid',
    'webhelpers2',
    'webhelpers2_grid',
    'mako',
    'pyyaml',
    'owslib',
    'lxml',
    'python-dateutil',
    'pytz',
    'esgf-pyclient',
    'python-swiftclient',
    'pyramid_celery',
    'celery',
    #'threddsclient',
    ]

setup(name='Phoenix',
      version="0.4.1",
      description='Phoenix',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Birdhouse',
      url='https://github.com/bird-house/pyramid-phoenix.git',
      keywords='web wsgi buildout pylons pyramids phoenix birdhouse malleefowl wps pywps esgf',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='phoenix',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = phoenix:main
      """,
      )
