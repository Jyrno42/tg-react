import json
import unittest

from tg_react.language import DjangoLocaleData


class LanguagesTestCase(unittest.TestCase):
    def test_valid_headers(self):
        locale_data_generator = DjangoLocaleData()
        languages, languages_data = locale_data_generator.collect_translations()

        self.assertEqual(list(sorted(languages.keys())), ['en', 'et'])
        self.assertEqual(list(sorted(languages_data.keys())), ['en', 'et'])

        locale_data_en = json.loads(languages_data.get('en'))
        locale_data_et = json.loads(languages_data.get('et'))

        header_data_en = locale_data_en.get('')
        header_data_et = locale_data_et.get('')

        # Remove diff unfriendly values
        header_data_en.pop('po-revision-date')
        header_data_et.pop('pot-creation-date')
        header_data_et.pop('po-revision-date')
        header_data_en.pop('pot-creation-date')

        self.assertDictEqual(header_data_en, {
            'mime-version': '1.0',
            'last-translator': 'Automatic <hi@thorgate.eu>',
            'x-generator': 'Python',
            'language': 'en',
            'lang': 'en',
            'content-transfer-encoding': '8bit',
            'project-id-version': 'Example v0.0.1',
            'domain': 'djangojs',
            'report-msgid-bugs-to': '',
            'content-type': 'text/plain; charset=UTF-8',
            'plural-forms': None,
            'language-team': 'Automatic <hi@thorgate.eu>'
        })

        self.assertDictEqual(header_data_et, {
            'mime-version': '1.0',
            'last-translator': 'Automatic <hi@thorgate.eu>',
            'x-generator': 'Python',
            'language': 'et',
            'lang': 'et',
            'content-transfer-encoding': '8bit',
            'project-id-version': 'Example v0.0.1',
            'domain': 'djangojs',
            'report-msgid-bugs-to': '',
            'content-type': 'text/plain; charset=UTF-8',
            'plural-forms': '(n != 1)',
            'language-team': 'Automatic <hi@thorgate.eu>'
        })

    def test_valid_translation_string_present(self):
        locale_data_generator = DjangoLocaleData()
        languages, languages_data = locale_data_generator.collect_translations()

        self.assertEqual(list(sorted(languages.keys())), ['en', 'et'])
        self.assertEqual(list(sorted(languages_data.keys())), ['en', 'et'])

        locale_data_en = json.loads(languages_data.get('en'))
        locale_data_et = json.loads(languages_data.get('et'))

        self.assertEqual(locale_data_en.get('Dummy test string'), 'EN: Dummy test string')
        self.assertEqual(locale_data_et.get('Dummy test string'), 'ET: Dummy test string')

    def test_with_package_define(self):
        locale_data_generator = DjangoLocaleData(packages='django.contrib.admin')
        languages, languages_data = locale_data_generator.collect_translations()

        self.assertEqual(list(sorted(languages.keys())), ['en', 'et'])

        locale_data = json.loads(languages_data.get('en'))

        self.assertEqual(locale_data.get('Dummy test string'), 'EN: Dummy test string')
