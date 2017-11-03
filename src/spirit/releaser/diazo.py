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
OPTION_PARAM_THEME_VERSION = 'diazo_export.adjust_theme_version'
OPTION_THEME_NAME = 'diazo_export.theme_name'


def _check_config(data):
    if not os.path.exists(SETUP_CONFIG_FILE):
        return False

    config = ConfigParser()
    config.read(SETUP_CONFIG_FILE)

    if not config.has_option(SECTION, OPTION_ENABLED):
        return False, None

    try:
        enabled = config.getboolean(SECTION, OPTION_ENABLED)
    except ValueError:
        pass

    if not enabled:
        return False, None

    if not config.has_option(SECTION, OPTION_DIAZO_PATH):
        return False, None

    path = config.get(SECTION, OPTION_DIAZO_PATH)
    if path is None:
        return False, path

    if not os.path.exists(path):
        logger.warning(
            'Configured diazo path "{0}" does not exist.'.format(path)
        )
        return False, path

    return config, path


def update_version(data):
    """Update the version number."""
    config, path = _check_config(data)
    if not config:
        return

    workingdir = data.get('workingdir')
    diazo_folder = os.path.join(workingdir, path)
    manifest_file = os.path.join(diazo_folder, 'manifest.cfg')
    has_manifest = os.path.exists(manifest_file)
    if not has_manifest:
        return

    version = data.get('dev_version', data.get('new_version'))
    if config.has_option(SECTION, OPTION_PARAM_THEME_VERSION):
        _update_param_theme_version(config, manifest_file, version)


def release_diazo(data):
    """Release a diazo theme from a folder."""
    if not os.path.exists(SETUP_CONFIG_FILE):
        return

    config, path = _check_config(data)
    if not config:
        return

    if not utils.ask('Create a zip file of the Diazo Theme?', default=True):
        return

    package_name = data.get('name')
    tmp_folder = tempfile.mkdtemp()

    if config.has_option(SECTION, OPTION_THEME_NAME):
        zip_name = config.get(SECTION, OPTION_THEME_NAME)
    else:
        zip_name = package_name

    diazo_folder = os.path.join(tmp_folder, zip_name)
    shutil.copytree(path, diazo_folder)
    update_manifest(data, config, diazo_folder, package_name)

    create_zipfile(tmp_folder, data.get('workingdir'), zip_name)
    shutil.rmtree(tmp_folder)


def update_manifest(data, config, diazo_folder, package_name):
    """Update the manifest file."""
    manifest_file = os.path.join(diazo_folder, 'manifest.cfg')
    has_manifest = os.path.exists(manifest_file)
    if has_manifest:
        if config.has_option(SECTION, OPTION_TITLE_UPDATE):
            _update_title(data, config, manifest_file, package_name)


def _update_title(data, config, manifest_file, package_name):
    """Update the title of the theme."""
    try:
        do_update = config.getboolean(SECTION, OPTION_TITLE_UPDATE)
    except ValueError:
        return

    if not do_update:
        return

    manifest = ConfigParser()
    manifest.read(manifest_file)
    version = data.get('version')
    if version is None:
        version = pkg_resources.get_distribution(package_name).version
    title = manifest.get('theme', 'title')
    manifest.set('theme', 'title', ' '.join([title, version]))
    with open(manifest_file, 'wb') as configfile:
        manifest.write(configfile)


def _update_param_theme_version(config, manifest_file, version):
    """Update the 'theme_version' param."""
    try:
        do_update = config.getboolean(SECTION, OPTION_PARAM_THEME_VERSION)
    except ValueError:
        return

    if not do_update:
        return

    manifest = ConfigParser()
    manifest.read(manifest_file)
    if not manifest.has_section('theme:parameters'):
        manifest.add_section('theme:parameters')
    manifest.set(
        'theme:parameters',
        'theme_version',
        'string:{0}'.format(version),
    )
    with open(manifest_file, 'wb') as configfile:
        manifest.write(configfile)


def create_zipfile(src, dist, zip_name):
    """Create a ZIP file."""
    # Work on the source root dir.
    os.chdir(src)

    # Prepare the zip file name
    filename = zip_name + '.zip'

    # We need the full path.
    parent = os.path.abspath(os.path.join(dist, os.pardir))
    filename = os.path.join(parent, filename)
    logger.info('Creating zip file at: {0}'.format(filename))

    zf = zipfile.ZipFile(filename, 'w')
    for dirpath, dirnames, filenames in os.walk('./'):
        for name in filenames:
            path = os.path.normpath(os.path.join(dirpath, name))
            if os.path.isfile(path):
                zf.write(path, path)
    # Close file to write to disk.
    zf.close()
    os.chdir(dist)


def main():
    """Run Diazo releaser."""
    vcs = zest.releaser.choose.version_control()
    data = {
        'name': vcs.name,
        'workingdir': os.getcwd(),
    }
    release_diazo(data)
