#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from datetime import datetime
import os
import sys
import pyvib

sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------

project = u'pyvib'
author = u'Paw'
copyright = u'2017–{0}, '.format(datetime.utcnow().year) + author

# The short X.Y version.
version = '.'.join(pyvib.__version__.split('.', 2)[:2])
# The full version, including alpha/beta/rc tags.
release = pyvib.__version__


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon',
              'sphinx.ext.mathjax', 'sphinx.ext.coverage',
              'sphinx.ext.linkcode', 'sphinx.ext.doctest']
# napoleon: alternative to numpydoc -- looks a bit worse.
# linkcode: link to github, see linkcode_resolve() below]
napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

# See https://github.com/rtfd/readthedocs.org/issues/283
mathjax_path = ('https://cdn.mathjax.org/mathjax/latest/MathJax.js?'
                'config=TeX-AMS-MML_HTMLorMML')


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'  # 'alabaster'
#html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {}
# html_theme_options = {
#     "extra_nav_links": {
#         "🚀 Github": "https://github.com/pawsen/pyvib",
#         "💾 Download Releases": "https://pypi.python.org/pypi/pyvib",
#     },
#     'github_user': 'pawsen',
#     'github_repo': 'pyvib',
#     'github_button': False,
#     'github_banner': True,
# }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'pyvibdoc'

# https://stackoverflow.com/a/42513684/1121523
# https://gist.github.com/bskinn/0e164963428d4b51017cebdb6cda5209
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.5', None),
    'sphinx': ('http://www.sphinx-doc.org/en/stable/', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    'scipy': ('http://docs.scipy.org/doc/scipy/reference/', None),
    'matplotlib': ('http://matplotlib.sourceforge.net/', None)
}

# -----------------------------------------------------------------------------
# Source code links
# -----------------------------------------------------------------------------
# https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L286
import inspect
from os.path import relpath, dirname

for name in ['sphinx.ext.linkcode']: #, 'numpydoc.linkcode']:
    try:
        __import__(name)
        extensions.append(name)
        break
    except ImportError:
        pass
else:
    print("NOTE: linkcode extension not found -- no links to source generated")

def linkcode_resolve(domain, info):
    """
    Determine the URL corresponding to Python object
    """
    if domain != 'py':
        return None

    modname = info['module']
    fullname = info['fullname']

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split('.'):
        try:
            obj = getattr(obj, part)
        except Exception:
            return None

    # strip decorators, which would resolve to the source of the decorator
    # possibly an upstream bug in getsourcefile, bpo-1764286
    try:
        unwrap = inspect.unwrap
    except AttributeError:
        pass
    else:
        obj = unwrap(obj)

    try:
        fn = inspect.getsourcefile(obj)
    except Exception:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except Exception:
        lineno = None

    if lineno:
        linespec = "#L%d-L%d" % (lineno, lineno + len(source) - 1)
    else:
        linespec = ""

    fn = relpath(fn, start=dirname(pyvib.__file__))

    return "https://github.com/pawsen/pyvib/blob/master/pyvib/%s%s" % (fn, linespec)

#     if 'dev' in numpy.__version__:
#         return "https://github.com/pawsen/vib/blob/master/vib/%s%s" % (
#            fn, linespec)
#     else:
#         return "https://github.com/numpy/numpy/blob/v%s/numpy/%s%s" % (
# numpy.__version__, fn, linespec)
