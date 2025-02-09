# from setuptools import setup, command
from setuptools import setup
from setuptools.command.install_scripts import install_scripts
import os
import shutil

def strip_comments(l):
    return l.split('#', 1)[0].strip()

def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(os.path.join(os.getcwd(), *f)).readlines()]))

class py_install(install_scripts):
# class py_install(command.install_scripts.install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                shutil.move(script, script[:-3])

setup(
    name='Hora',
    author='Richard Charlesworth',
    version='0.1.0',
    license="MIT",
    url='https://github.com/rdchar/Hora',
    description='Hypernetwork Theory library.',
    long_description_content_type='text/x-rst',
    long_description="""Hypernetwork Theory library.""",
    install_requires=reqs('requirements.txt'),
    packages=['hypernetworks', 'hypernetworks/core', 'hypernetworks/utils', 'hypernetworks/QL'],
    cmdclass={"install_scripts": py_install},
    package_data={'': ['fullHT.lark', 'HoraQL.lark']},
    include_package_data=True,
    zip_safe=False
)
