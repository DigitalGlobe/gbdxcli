'''
Authors: Donnie Marino
Contact: dmarino@digitalglobe.com

Command Line interface for the GBDX tools suite.
This is intended to mimic the aws cli in that users
won't need to program to access the full functionality
of the GBDX API.

This is a Click application
Click is the 'Command Line Interface Creation Kit'
Learn more at http://click.pocoo.org/5/

Main gbdx command group is cli
Subcommands are click groups

Commands belong to one click group, allows for cli syntax like this:
gbdx workflow list_tasks
gbdx workflow describe_task -n MutualInformationCoregister
gbdx catalog strip_footprint -c 10200100359B2C00
'''

import click
import simplejson as json
import six
from gbdx_auth import gbdx_auth

from gbdxtools import Interface
import _s3creds

gbdx = Interface()


# report pretty json
def show(js):
    six.print_(json.dumps(js, sort_keys=True, indent=4, separators=(',', ': ')))


# Main command group
@click.group()
def cli():
    """GBDX Command Line Interface
    example:
        gbdx workflow list_tasks
    """
    pass


#
# Workflow command group
#
@cli.group()
def workflow():
    """GBDX Workflow Interface"""
    pass


@workflow.command()
def list_tasks():
    """List workflow tasks available to the user"""
    show( gbdx.workflow.list_tasks() )
    

@workflow.command()
@click.option('--name','-n',
    help="Name of task to describe")
def describe_task(name):
    """Show the task description json for the task named"""
    show( gbdx.workflow.describe_task(name) )


@workflow.command()
@click.option('--id','-i',
    help="ID of the workflow to status")
def status(id):
    """Display the status information for the workflow ID given"""
    show( gbdx.workflow.status(id) )


#
# Catalog command group
#
@cli.group()
def catalog():
    """GBDX Catalog Interface"""
    pass


@catalog.command()
@click.option("--catalog_id", "-c",
    help="Catalog ID of the strip to display")
def strip_footprint(catalog_id):
    """Show the WKT footprint of the strip named"""
    show(gbdx.catalog.get_strip_footprint_wkt(catalog_id))


#
# Ordering command group
#
@cli.group()
def ordering():
    """GBDX Ordering Interface"""
    pass


@ordering.command()
@click.option("--catalog_id", "-c",
    multiple=True,
    help="Catalog ID of the strip to order. May pass multiple times")
def order(catalog_id):
    """Order the catalog ID(s) passed in"""
    if len(catalog_id) == 0:
        six._print("No catalog IDs passed in.")
        return
    if len(catalog_id) == 1:
        # pull the one item and just order that
        show( gbdx.ordering.order(catalog_id[0]) )
    else:
        # this is a list with multiple entries
        show( gbdx.ordering.order(catalog_id) )


@ordering.command()
@click.option("--order_id","-o",
    help="Order ID to status")
def status(order_id):
    show( gbdx.ordering.status(id) )


#
# IDAHO command group
#
@cli.group()
def idaho():
    """GBDX Idaho Interface"""
    pass


@idaho.command()
@click.option("--catalog_id","-c",
    help="Catalog ID to fetch IDAHO images for")
def get_images_by_catid(catalog_id):
    """Retrieve all IDAHO Images associated with a catalog ID"""
    show(gbdx.idaho.get_images_by_catid(catalog_id))


#
# S3 command group
#
@cli.group()
def s3():
    """GBDX S3 Interface"""
    pass


@s3.command()
def info():
    """Display the s3 information for this GBDX User"""
    show(gbdx.s3.info)


#
# S3temp command group for temporary credentials
#
@cli.group()
def s3temp():
    """Set temporary S3 credentials for access to GBDX S3 customer-data bucket."""
    pass


@s3temp.command()
@click.option("--awscli/--no-awscli", "-a", help="Set temporary s3 credentials in the awscli config file (~/.aws/credentials) (default: false).", default=False)
@click.option("--awscli_profile", "-o", help="Write the credentials into this profile in the aswcli config file (default: temp).", default="temp")
@click.option("--s3cmd/--no-s3cmd", "-s", help="Set temporary s3 credentials in the s3cmd config file. (default: false)", default=False)
@click.option("--s3cmd_config", help="Name of the s3cmd config file (default: ~/.s3cfg).", default="~/.s3cfg")
@click.option("--environ/--no-environ", "-e", help="Write temporary s3 credentials to stdout. (default: false)", default=False)
@click.option("--environ_export/--no-environ_export", help="Prefix each environment variable with 'export' (default: false).", default=False)
@click.option("--print_token/--no-print_token", "-p", help="Write to the screen the GBDX token information. (default: false)", default=False)
@click.option("--duration", "-d", help="Duration of the S3 credentials in seconds. (default: 36000)", type=click.IntRange(900,36000), default=36000)
def set(awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export, print_token, duration):
    """Writes temporary GBDX S3 credentials to one or more of the following targets:

    awscli -- The Amazon Web Services Command Line Interface (https://aws.amazon.com/cli/) credentials file
    s3cmd -- The Command Line S3 Client (http://s3tools.org/s3cmd) configuration file
    environ -- Bash environment variables (only prints to the screen)

    By design, the GBDX credentials have a duration of at most 36000 seconds

    Warning: No backups of the original files are made!

    """

    if not any((awscli, s3cmd, environ)):
        raise click.ClickException("Must specify at least one of --awscli, --s3cmd or --environ.")

    gbdx_conn = gbdx_auth.get_session()

    if print_token:
        _s3creds.print_gbdx_token_info(gbdx_conn)

    _s3creds.set_temp_creds(gbdx_conn, awscli, awscli_profile, s3cmd, s3cmd_config, environ, environ_export, duration)


@s3temp.command()
def clear():
    """Clear temporary data from configuration files."""
    raise click.ClickException("Not Implemented")


if __name__ == '__main__':
    cli()
