from setuptools import setup
import os


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), *f)).readlines()]))


setup(
    name='hn',
    version='0.0.1',
    license="MIT",
    url='https://github.com/rdchar/HypernetworkTheory',
    description='Hypernetwork Theory library and bin.',
    install_requires=reqs('requirements.txt'),
    packages=['hypernetworks'],
    zip_safe=False
    # ...
)
