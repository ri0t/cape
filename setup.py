from setuptools import setup
import os.path

from RAIN.System.Version import ver

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["RAIN/*"]

setup(name = "rain",
    version = ver,
    description = "Autonomous Naval Robotic Vehicle OS",
    license = "GPL v3",
    author = "Hackerfleet Contributors",
    author_email = "riot@hackerfleet.org",
    url = "https://hackerfleet.org/rain",
    packages = ['RAIN'],
    package_data = {'RAIN': ['RAIN']},
    scripts = ['rain.py'],
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Logging',
        'Topic :: System :: Power (UPS)',
        'Topic :: System :: Networking'
    ],

    #package_data = {'package' : files },
    #scripts = [""], # None yet
    long_description = read('README'),
    # Dependencies
    #
    # Note: Those are proven to work, older versions might work, 
    # but have never been tested.
    #
    dependency_links = [
        'http://kamaelia.googlecode.com/files/Axon-1.7.0.tar.gz',
        'http://kamaelia.googlecode.com/files/Kamaelia-1.0.12.0.tar.gz'
    ],
    install_requires=['jsonpickle>=0.4.0',
                      'hgapi>=1.1.0',
                      'PIL>=1.1.7',
                      'Axon>=1.7.0',
                      'Kamaelia>=1.0.12.0',
                      'pynmea>=0.3.0',
                      'configobj>=4.7.2'],
    extras_require={'mapnik2': 'mapnik2>=2.0.0',
                    'pymongo': 'pymongo>=2.2'}
)
