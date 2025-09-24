# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# import os
# import sys
# sys.path.insert(0, os.path.abspath('../src'))
# autodoc_mock_imports = ["test","tmc"]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mysterions'
copyright = '2025, Christopher O\'Brien'
author = "Christopher O'Brien"
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = ['sphinx.ext.autodoc']

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
# add_module_names = False
# html_show_sourcelink = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# def skip(app, what, name, obj, would_skip, options):
#     if name == "__init__":
#         return False
#     return would_skip

# def setup(app):
#     app.connect("autodoc-skip-member", skip)

# something
