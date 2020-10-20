from os import path
from setuptools import setup


VERSION = '0.2.0'


def read(file_name):
    with open(path.join(path.dirname(__file__), file_name), encoding='utf-8') as file:
        return file.read()


setup(
    name='install-jdk',
    version=VERSION,
    author='Jason Snow',
    author_email='jsn.snw@gmail.com',
    url="https://github.com/jyksnw/install-jdk",
    keywords="AdoptOpenJDK Java jdk jre",
    description='Installs AdoptOpenJDK Java',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    python_requires='>=3.6',
    packages=['jdk'],
)
