# -*- coding: utf-8 -*-
"""Plugins for zest.releaser for Diazo themes."""

from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
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
OPTION_DIAZO_PATH = 'diazo_export.path'
OPTION_ENABLED = 'diazo_export.enabled'
OPTION_PARAM_THEME_VERSION = 'diazo_export.adjust_theme_version'
OPTION_THEME_NAME = 'diazo_export.theme_name'
OPTION_TITLE_UPDATE = 'diazo_export.adjust_title'
OPTION_FILES_EXCLUDED = 'diazo_export.exclude'


def _check_config(data):
    if not os.path.exists(SETUP_CONFIG_FILE):
        return None

    config = ConfigParser()
    config.read(SETUP_CONFIG_FILE)

    if not config.has_option(SECTION, OPTION_ENABLED):
        return None

    try:
        enabled = config.getboolean(SECTION, OPTION_ENABLED)
    except ValueError:
        pass

    if not enabled:
        return None

    return config


def _get_diazo_path(config, section):
    try:
        enabled = config.getboolean(section, OPTION_ENABLED)
    except (NoOptionError, ValueError):
        enabled = config.getboolean(SECTION, OPTION_ENABLED)

    if not enabled:
        return None

    if not config.has_option(section, OPTION_DIAZO_PATH):
        return None

    path = config.get(section, OPTION_DIAZO_PATH)
    if path is None:
        return path

    if not os.path.exists(path):
        logger.warning(
            'Configured diazo path "{0}" does not exist.'.format(path)
        )
        return None

    return path


def update_version(data):
    """Update the version number."""
    config = _check_config(data)
    if not config:
        return

    if config.has_option(SECTION, 'diazo_export.multi'):
        multiple = True
        parts = config.get(SECTION, 'diazo_export.multi').split()
    else:
        parts = ['__default__']
        multiple = False

    for part in parts:
        if multiple:
            section = '{0}:{1}'.format(SECTION, part)
        else:
            section = SECTION

        if not config.has_section(section):
            continue
        path = _get_diazo_path(config, section)
        if not path:
            continue

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

    config = _check_config(data)
    if not config:
        return

    if not utils.ask('Create a zip file of the Diazo Theme?', default=True):
        return

    package_name = data.get('name')

    if config.has_option(SECTION, 'diazo_export.multi'):
        multiple = True
        parts = config.get(SECTION, 'diazo_export.multi').split()
    else:
        parts = ['__default__']
        multiple = False

    for part in parts:
        if multiple:
            section = '{0}:{1}'.format(SECTION, part)
        else:
            section = SECTION

        if not config.has_section(section):
            continue
        path = _get_diazo_path(config, section)
        if not path:
            continue

        tmp_folder = tempfile.mkdtemp()
        if config.has_option(section, OPTION_THEME_NAME):
            zip_name = config.get(section, OPTION_THEME_NAME)
        else:
            zip_name = package_name

        diazo_folder = os.path.join(tmp_folder, zip_name)
        excluded = []
        if config.has_option(SECTION, OPTION_FILES_EXCLUDED):
            excluded = config.get(SECTION, OPTION_FILES_EXCLUDED).split()
        shutil.copytree(
            path,
            diazo_folder,
            ignore=shutil.ignore_patterns(*excluded),
        )
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
