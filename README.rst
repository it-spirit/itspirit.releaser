spirit.releaser
===============

``spirit.releaser`` provides several plugins for `zest.releaser`_.
The plugins are registered globally and can be activated if needed.


Available Plugins
=================


Exporting Diazo Themes as ZIP files
-----------------------------------

Plone allows us to upload diazo themes as zip files.
This can be used when we don't have the permission to install our theme on the server as a python package (e.g. within a shared hosting environment).
``spirit.releaser`` provides a hook which is run after the release has been done.
Use the following options in your ``setup.cfg`` to enable the ZIP file export::

    [spirit.releaser]
    diazo_export.enabled = true
    diazo_export.path = src/my/package/theme
    diazo_export.adjust_title = true
    diazo_export.adjust_theme_version = true
    diazo_export.theme_name = mypackage
    diazo_export.exclude =
        node_modules
        _less

diazo_export.adjust_title
    Append the version number of the package to the title in the zipped ``manifest.cfg`` file.

diazo_export.adjust_theme_version
    Add or update the ``theme_version`` parameter with the current version number of the package.

diazo_export.enabled
    Activate or deactivate the export.
    It can be used in the default and multi-theme settings.

diazo_export.exclude
    Exclude the listed folders/files from the diazo export.

diazo_export.multi
    Define multiple subsections for diazo themes.
    Multi-theme sections must start with `spirit.releaser:`, followed by the identifier for that theme.

diazo_export.path
    Path relative from the package root to the folder containing the diazo resource files.
    It can be used in the default and multi-theme settings.

diazo_export.theme_name
    Add a custom name for the theme folder and exported zip file.
    Use this is you have a different name (id) for your theme, e.g. 'mypackage' instead of 'my.package'.
    It can be used in the default and multi-theme settings.

To export more than one diazo theme from a package you can use the `diazo_export.multi` option::

    [spirit.releaser]
    diazo_export.multi =
        theme
        custom
    diazo_export.enabled = true
    diazo_export.adjust_title = true
    diazo_export.adjust_theme_version = true

    [spirit.releaser:theme]
    diazo_export.path = src/my/package/theme
    diazo_export.theme_name = mypackage

    [spirit.releaser:custom]
    diazo_export.path = src/my/package/theme-custom
    diazo_export.theme_name = mypackage-custom


Installation
============

Use in a buildout
-----------------

::

    [buildout]
    parts += releaser

    [releaser]
    recipe = zc.recipe.egg:scripts
    dependent-scripts = true
    eggs =
        spirit.releaser
        my.package

If you want to use the latest development version from GitHub, add ``spirit.releaser`` to your ``mr.developer`` source section::

    [buildout]
    extensions += mr.developer

    [sources]
    spirit.releaser = git git@github.com:it-spirit/spirit.releaser.git


This creates the ``zest.releaser`` executables in your bin-directory.
Create a release as you're used to::

    $ ./bin/fullrelease


Installation in a virtualenv
----------------------------

You can also install ``spirit.releaser`` in a virtualenv.::

    $ pip install spirit.releaser

You can also install the latest version of ``spirit.releaser`` directly from GitHub::

    $ pip install -e git+git@github.com:it-spirit/spirit.releaser.git#egg=spirit.releaser

Now you can use it like this (when releasing your package)::

    $ fullrelease


.. _`zest.releaser`: http://zestreleaser.readthedocs.org/en/latest/
