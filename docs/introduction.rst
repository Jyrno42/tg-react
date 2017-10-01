Introduction
============

Helpers for react based applications running on django.

Installation
------------

Install tg-react with pip::

    pip install tg-react

Add to INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'tg_react',
    )

Then use it in your project::

    import tg_react

Features
--------

* Generic webpack constant generation
* URL flattening
* NodeJS compatible JavaScriptCatalog_
* Generic accounts API(s):

  - Signup
  - Login
  - Logout
  - Set active language (incl. customized LocaleMiddleware)
  - Forgot password

For more information about each feature see the next chapter.

.. _JavaScriptCatalog: https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#django.views.i18n.JavaScriptCatalog
