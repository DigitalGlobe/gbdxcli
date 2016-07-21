#!/usr/bin/env python

import ConfigParser
import os

import six
from gbdx_auth import gbdx_auth


def set_awscli_creds(s3_access_key, s3_secret_key, s3_session_token, profile_name, config_file):
    vardict = dict(aws_access_key_id=s3_access_key,
                   aws_secret_access_key=s3_secret_key,
                   aws_session_token=s3_session_token)

    _set_config(vardict, profile_name, config_file)


def set_s3cmd_creds(s3_access_key, s3_secret_key, s3_session_token, config_file, duration=36000):
    vardict = dict(access_key=s3_access_key,
                   secret_key=s3_secret_key,
                   access_token=s3_session_token)

    _set_config(vardict, 'default', config_file)


def print_environ_creds(s3_access_key, s3_secret_key, s3_session_token, export):
    vardict = dict(AWS_ACCESS_KEY_ID=s3_access_key,
                   AWS_SECRET_ACCESS_KEY=s3_secret_key,
                   AWS_SESSION_TOKEN=s3_session_token)
    _print_aws_environ(vardict, export)


def _set_config(vardict, profile_name, config_file):
    fname = os.path.expanduser(config_file)
    cfp = ConfigParser.SafeConfigParser()
    cfp.read(fname)
    for k, v in vardict.items():
        try:
            cfp.set(profile_name, k, v)
        except ConfigParser.NoSectionError:
            cfp.add_section(profile_name)
            cfp.set(profile_name, k, v)

    with open(fname, 'w+') as fh:
        cfp.write(fh)


def get_temp_s3creds(gbdx_conn=None, duration=36000):
    url = 'https://geobigdata.io/s3creds/v1/prefix?duration={}'.format(duration)
    if gbdx_conn is None:
        gbdx_conn = gbdx_auth.get_session()
    results = gbdx_conn.get(url, verify=False)

    if not results.ok or not results.json()['S3_access_key']:
        raise Exception("Failed to find {0}.  Error {1}".format(url, results.reason))

    s3creds = results.json()

    return s3creds


def set_temp_creds(gbdx_conn, awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export, duration):

    s3creds = get_temp_s3creds(gbdx_conn, duration)
    s3_access_key = s3creds['S3_access_key']
    s3_secret_key = s3creds['S3_secret_key']
    s3_session_token = s3creds['S3_session_token']

    if s3cmd:
        set_s3cmd_creds(s3_access_key, s3_secret_key, s3_session_token, config_file=s3cmd_config)

    if awscli:
        set_awscli_creds(s3_access_key, s3_secret_key, s3_session_token,
                         config_file='~/.aws/credentials',
                         profile_name=awscli_profile)

    if environ:
        print_environ_creds(s3_access_key, s3_secret_key, s3_session_token, export=environ_export)


def _print_aws_environ(vardict, export=False):
    export_str = 'export ' if export else ''

    six.print_()
    six.print_("#------------------ AWS bash environment variables -------------------")
    for k, v in vardict.items():
        six.print_('{}{}={}'.format(export_str, k, v))
    six.print_("#---------------------------------------------------------------------")
    six.print_()


def print_gbdx_token_info(gbdx_conn):

    six.print_()
    six.print_("#------------------------- GBDX Token Info ---------------------------")
    for k, v in gbdx_conn.token.items():
        six.print_('{}={}'.format(k, v))
    six.print_("#---------------------------------------------------------------------")
    six.print_()

