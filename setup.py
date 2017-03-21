import os
from subprocess import Popen, PIPE
from setuptools import setup, find_packages
import sys


HERE = os.path.abspath(os.path.dirname(__file__))

REQUIRES = [
    'alembic==0.9.*',
    'six==1.*',
    'SQLAlchemy==1.0.*',
]

EXTRAS = {
    'postgresql': [
        'psycopg2==2.7.*'
    ],
    'test': [
        'pytest==3.*',
        'pytest-cov==2.*'
    ],
}


if sys.version_info < (2, 7):
    REQUIRES.extend(['argparse', 'ordereddict'])
    EXTRAS['test'].extend(['unittest2'])


def get_version():
    version_file = os.path.join(HERE, 'VERSION')

    # read fallback file
    try:
        with open(version_file, 'r+') as fp:
            version_txt = fp.read().strip()
    except:
        version_txt = None

    # read git version (if available)
    try:
        version_git = (
            Popen(['git', 'describe'], stdout=PIPE, stderr=PIPE, cwd=HERE)
            .communicate()[0]
            .strip()
            .decode(sys.getdefaultencoding()))
    except:
        version_git = None

    version = version_git or version_txt or '0.0.0'

    # update fallback file if necessary
    if version != version_txt:
        with open(version_file, 'w') as fp:
            fp.write(version)

    return version


setup(
    name='occams_datastore',
    version=get_version(),
    description='Provides storage solution for sparse data.',
    classifiers=[
        'Development Status :: 4 - Beta'
        'Intended Audience :: Developers'
        'Operating System :: OS Independent'
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],
    keywords='BIT OCCAMS datastore database eav sqlalchemy clinical',
    author='The YoungLabs',
    author_email='younglabs@ucsd.edu',
    url='https://github.com/younglabs/occams_datatore',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    tests_require=EXTRAS['test'],
    test_suite='nose.collector',
    entry_points="""\
    [console_scripts]
    """
)
