import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('templates',Path(__file__).resolve().parents[1]/'scripts/choose_template.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)

class TemplateTests(unittest.TestCase):
    def test_all_presets(self):
        import json
        catalog=json.loads(t.CATALOG.read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['templates']),9)
        for preset in catalog['templates']:
            brief=t.instantiate(preset['id'])
            self.assertEqual(len(brief['stickers']),16)
            self.assertEqual(len({s['meaning'] for s in brief['stickers']}),16)
            self.assertTrue(all(s['action'] for s in brief['stickers']))
            self.assertEqual(brief['reference_images'],[])
            self.assertEqual(brief['spec_status'],'待平台复核')
    def test_mix_style_and_content(self):
        original=t.instantiate('office-life')
        mixed=t.instantiate('office-life','clay','我的下班时刻')
        self.assertEqual(mixed['stickers'],original['stickers'])
        self.assertEqual(mixed['style']['id'],'clay')
        self.assertEqual(mixed['title'],'我的下班时刻')
        self.assertIn('黏土',mixed['cover_direction'])
    def test_unknown_option(self):
        with self.assertRaises(ValueError):t.instantiate('unknown')
        with self.assertRaises(ValueError):t.instantiate('office-life','unknown')

if __name__=='__main__':unittest.main()
