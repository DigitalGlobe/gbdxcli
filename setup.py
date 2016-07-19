from setuptools import setup

setup(
    name='gbdxcli',
    version='0.0.2',
    install_requires=[
        'Click',
        'gbdxtools',
        'gbdx-auth'
    ],
    entry_points='''
        [console_scripts]
        gbdx=gbdxcli.gbdxcli:cli
    ''',
    scripts=['bin/set_s3_creds',
             ]

)
