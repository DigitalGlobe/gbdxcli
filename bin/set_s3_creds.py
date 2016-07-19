#!/usr/bin/env python

import six

import ConfigParser

import argparse
import os
import sys
import traceback

from gbdx_auth import gbdx_auth

__version__ = '0.1'


def set_awscli_creds(s3_access_key, s3_secret_key, s3_session_token, profile_name, config_file):
    vardict = dict(aws_access_key_id=s3_access_key,
                   aws_secret_access_key=s3_secret_key,
                   aws_session_token=s3_session_token)

    _set_config(vardict, profile_name, config_file)


def set_s3cmd_creds(s3_access_key, s3_secret_key, s3_session_token, config_file):
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


def get_temp_s3creds(gbdx_conn=None):
    url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
    if gbdx_conn is None:
        gbdx_conn = gbdx_auth.get_session()
    results = gbdx_conn.get(url, verify=False)

    if not results.ok or not results.json()['S3_access_key']:
        raise Exception("Failed to find {0}.  Error {1}".format(url, results.reason))

    s3creds = results.json()

    return s3creds


def set_temp_creds(gbdx_conn, awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export):

    s3creds = get_temp_s3creds(gbdx_conn)
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


def _print_gbdx_token_info(gbdx_conn):

    six.print_()
    six.print_("#------------------------- GBDX Token Info ---------------------------")
    for k, v in gbdx_conn.token.items():
        six.print_('{}={}'.format(k, v))
    six.print_("#---------------------------------------------------------------------")
    six.print_()


def main():

    parser = argparse.ArgumentParser(description="Set temporary S3 credentials into "
                                                 "configuration files and/or environment variables.",
                                     version=__version__)

    parser.add_argument("-a", "--awscli", dest="awscli", action="store_true",
                        required=False, default=False,
                        help="If True, then set temp s3 credentials in the awscli config file")

    parser.add_argument("-p", "--awscli_profile", dest="awscli_profile", metavar="<profile_name>",
                        type=str, required=False, default='temp',
                        help="Set the variables in the configuration in the specified profile")

    parser.add_argument("-s", "--s3cmd", dest="s3cmd", action="store_true",
                        required=False, default=False,
                        help="If True, then set temp s3 credentials in the s3cmd config file")

    parser.add_argument("--s3cmd_config", dest="s3cmd_config", default="~/.s3cfg", metavar="<config_file>",
                        type=str, required=False, help="Name of the config file for s3cmd")

    parser.add_argument("-e", "--environ", dest="environ", action="store_true",
                        required=False, default=False,
                        help="If True, then write temp s3 credentials to stdout")

    parser.add_argument("--environ_export", dest="environ_export", action="store_true",
                        required=False, help="If true, then prefix each environment variable with 'export'")

    parser.add_argument("-d", "--display-token", dest="print_token", action="store_true", required=False, default=False,
                        help="If set, then print the GBDX token information.")

    args = parser.parse_args()

    if not any((args.awscli, args.s3cmd, args.environ)):

        six.print_()
        six.print_("Must specify at least one of --awscli, --s3cmd or --environ.")
        six.print_()
        parser.print_help()
        sys.exit(1)

    try:
        gbdx_conn = gbdx_auth.get_session()

        if args.print_token:
            _print_gbdx_token_info(gbdx_conn)

        set_temp_creds(gbdx_conn,
                       awscli=args.awscli, awscli_profile=args.awscli_profile,
                       s3cmd=args.s3cmd, s3cmd_config=args.s3cmd_config,
                       environ=args.environ, environ_export=args.environ_export)
    except Exception:
        traceback.print_exc()
        parser.error("An occurred.")
        sys.exit(1)


if __name__ == '__main__':
    main()