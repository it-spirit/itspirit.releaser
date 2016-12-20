# -*- coding: utf-8 -*-
"""Plugins for zest.releaser for Diazo themes."""

# python imports
from ConfigParser import ConfigParser
from zest.releaser import utils
import logging
import os
import pkg_resources
import shutil
import tempfile
import zest.releaser.choose
import zipfile


logger = logging.getLogger(__name__)

SETUP_CONFIG_FILE = 'setup.cfg'
SECTION = 'spirit.releaser'
OPTION_ENABLED = 'diazo_export.enabled'
OPTION_DIAZO_PATH = 'diazo_export.path'
OPTION_TITLE_UPDATE = 'diazo_export.adjust_title'


def release_diazo(data):
    """Release a diazo theme from a folder."""
    if not os.path.exists(SETUP_CONFIG_FILE):
        return

    config = ConfigParser()
    config.read(SETUP_CONFIG_FILE)

    if not config.has_option(SECTION, OPTION_ENABLED):
        return

    try:
        enabled = config.getboolean(SECTION, OPTION_ENABLED)
    except ValueError:
        pass

    if not enabled:
        return

    if not config.has_option(SECTION, OPTION_DIAZO_PATH):
        return

    path = config.get(SECTION, OPTION_DIAZO_PATH)
    if path is None:
        return

    if not os.path.exists(path):
        logger.warning(
            'Diazo path does not exist. We can not create a zip file.'
        )
        return

    if not utils.ask('Create a zip file of the Diazo Theme?', default=True):
        return

    package_name = data.get('name')
    tmp_folder = tempfile.mkdtemp()
    diazo_folder = os.path.join(tmp_folder, package_name)
    shutil.copytree(path, diazo_folder)

    manifest_file = os.path.join(diazo_folder, 'manifest.cfg')
    has_manifest = os.path.exists(manifest_file)
    if has_manifest and config.has_option(SECTION, OPTION_TITLE_UPDATE):
        try:
            config.getboolean(SECTION, OPTION_TITLE_UPDATE)
        except ValueError:
            pass
        else:
            if utils.ask(
                'Add version number to the theme title in exported zip file?',
                default=True,
            ):
                manifest = ConfigParser()
                manifest.read(manifest_file)
                version = pkg_resources.get_distribution(package_name).version
                title = manifest.get('theme', 'title')
                manifest.set('theme', 'title', ' '.join([title, version]))
                with open(manifest_file, 'wb') as configfile:
                    manifest.write(configfile)
    create_zipfile(tmp_folder, data.get('workingdir'), package_name)
    shutil.rmtree(tmp_folder)


def create_zipfile(src, dist, package_name):
    """Creates a ZIP file """
    # Work on the source root dir.
    os.chdir(src)

    # Prepare the zip file name
    filename = package_name + '.zip'

    # We need the full path.
    filename = os.path.join(dist, filename)
    logger.info('Creating zip file at: {0}'.format(filename))

    zf = zipfile.ZipFile(filename, 'w')
    for dirpath, dirnames, filenames in os.walk('./'):
        for name in filenames:
            path = os.path.normpath(os.path.join(dirpath, name))
            if os.path.isfile(path):
                zf.write(path, path)
    # Close file to write to disk.
    zf.close()


def main():
    vcs = zest.releaser.choose.version_control()
    data = {
        'name': vcs.name,
        'workingdir': os.getcwd(),
    }
    release_diazo(data)
