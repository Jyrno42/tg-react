import itertools
import json
import os

import re
import six

from django.apps import apps
from django.conf import settings
from django.utils import translation
from django.utils.translation.trans_real import DjangoTranslation

from tg_react.catalogue_legacy import get_catalogue_legacy


class DjangoLocaleData(object):
    languages = settings.LANGUAGES

    domain = 'djangojs'
    packages = None

    def __init__(self, domain=None, packages=None):
        """Create new locale data generator. By default use all installed packages."""
        if domain and isinstance(domain, six.string_types):
            self.domain = domain

        self.packages = packages.split('+') if packages else self.packages
        self.paths = self.get_paths(self.packages) if self.packages else None

    def get_catalog(self, locale):
        """Create Django translation catalogue for `locale`."""
        with translation.override(locale):
            try:
                translation_engine = DjangoTranslation(locale, domain=self.domain, localedirs=self.paths)

                trans_cat = translation_engine._catalog
                trans_fallback_cat = translation_engine._fallback._catalog if translation_engine._fallback else {}
            except:
                trans_cat = get_catalogue_legacy(self.domain, locale, self.packages)
                trans_fallback_cat = get_catalogue_legacy(self.domain, settings.LANGUAGE_CODE, self.packages)

            return trans_cat, trans_fallback_cat

    @classmethod
    def get_paths(cls, packages):
        """Create list of matching packages for translation engine."""
        allowable_packages = dict((app_config.name, app_config) for app_config in apps.get_app_configs())
        app_configs = [allowable_packages[p] for p in packages if p in allowable_packages]
        # paths of requested packages
        return [os.path.join(app.path, 'locale') for app in app_configs]

    @classmethod
    def get_catalogue_header_value(cls, catalog, key):
        """Get `.po` header value."""
        header_value = None
        if '' in catalog:
            for line in catalog[''].split('\n'):
                if line.startswith('%s:' % key):
                    header_value = line.split(':', 1)[1].strip()

        return header_value

    def _num_plurals(self, catalogue):
        """
        Return the number of plurals for this catalog language, or 2 if no
        plural string is available.
        """
        match = re.search(r'nplurals=\s*(\d+)', self.get_plural(catalogue) or '')
        if match:
            return int(match.groups()[0])
        return 2

    @classmethod
    def get_plural(cls, catalog):
        """Special handling for plural forms."""
        plural = cls.get_catalogue_header_value(catalog, 'Plural-Forms')

        if plural is not None:
            # This should be a compiled function of a typical plural-form:
            # Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 :
            #               n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
            plural = [el.strip() for el in plural.split(';') if el.strip().startswith('plural=')][0].split('=', 1)[1]
        return plural

    def make_header(self, locale, catalog):
        """Populate header with correct data from top-most locale file."""
        return {
            "po-revision-date": self.get_catalogue_header_value(catalog, 'PO-Revision-Date'),
            "mime-version": self.get_catalogue_header_value(catalog, 'MIME-Version'),
            "last-translator": 'Automatic <hi@thorgate.eu>',
            "x-generator": "Python",
            "language": self.get_catalogue_header_value(catalog, 'Language') or locale,
            "lang": locale,
            "content-transfer-encoding": self.get_catalogue_header_value(catalog, 'Content-Transfer-Encoding'),
            "project-id-version": self.get_catalogue_header_value(catalog, 'Project-Id-Version'),
            "pot-creation-date": self.get_catalogue_header_value(catalog, 'POT-Creation-Date'),
            "domain": self.domain,
            "report-msgid-bugs-to": self.get_catalogue_header_value(catalog, 'Report-Msgid-Bugs-To'),
            "content-type": self.get_catalogue_header_value(catalog, 'Content-Type'),
            "plural-forms": self.get_plural(catalog),
            "language-team": self.get_catalogue_header_value(catalog, 'Language-Team')
        }

    def collect_translations(self):
        """Collect all `domain` translations and return `Tuple[languages, locale_data]`"""
        languages = {}
        locale_data = {}

        for language_code, label in settings.LANGUAGES:
            languages[language_code] = '%s' % label

            # Create django translation engine for `language_code`
            trans_cat, trans_fallback_cat = self.get_catalog(language_code)

            # Add the meta object
            locale_data[language_code] = {}
            locale_data[language_code][""] = self.make_header(language_code, trans_cat)
            num_plurals = self._num_plurals(trans_cat)

            # Next code is largely taken from Django@master (01.10.2017) from `django.views.i18n JavaScriptCatalogue`
            pdict = {}
            seen_keys = set()

            for key, value in itertools.chain(six.iteritems(trans_cat), six.iteritems(trans_fallback_cat)):
                if key == '' or key in seen_keys:
                    continue

                if isinstance(key, six.string_types):
                    locale_data[language_code][key] = value

                elif isinstance(key, tuple):
                    msgid, cnt = key
                    pdict.setdefault(msgid, {})[cnt] = value

                else:
                    raise TypeError(key)
                seen_keys.add(key)

            for k, v in pdict.items():
                locale_data[language_code][k] = [v.get(i, '') for i in range(num_plurals)]

        for key, value in locale_data.items():
            locale_data[key] = json.dumps(value)

        return languages, locale_data


def constants(context):
    locale_data_generator = DjangoLocaleData()
    all_languages, locale_data = locale_data_generator.collect_translations()

    return {
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'LANGUAGE_COOKIE_NAME': settings.LANGUAGE_COOKIE_NAME,
        'LANGUAGES': all_languages,
        'LOCALE_DATA': locale_data,
    }
