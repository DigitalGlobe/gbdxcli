from setuptools import setup

setup(
    name='gbdxcli',
    version='0.0.2',
    py_modules=['gbdxcli'],
    install_requires=[
        'Click',
        'gbdxtools'
    ],
    entry_points='''
        [console_scripts]
        gbdx=gbdxcli:cli
    '''
)
