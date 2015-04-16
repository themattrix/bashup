from setuptools import setup

setup(
    name='bashup',
    version='1.1.0',
    packages=(
        'bashup',
        'bashup.compile',
        'bashup.compile.elements',
        'bashup.parse'),
    url='https://github.com/themattrix/bashup',
    license='MIT',
    author='Matthew Tardiff',
    author_email='mattrix@gmail.com',
    install_requires=(
        'docopt',
        'Jinja2',
        'pyparsing',
        'temporary',),
    tests_require=(
        'mock',),
    entry_points={
        'console_scripts': (
            'bashup = bashup.__main__:main',)},
    description=(
        'A (toy) language that compiles to bash.'),
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'))
