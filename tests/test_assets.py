import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from PIL import Image, ImageDraw

spec=importlib.util.spec_from_file_location('assets',Path(__file__).resolve().parents[1]/'scripts/prepare_assets.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class AssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        im=Image.new('RGBA',(300,300));ImageDraw.Draw(im).ellipse((30,30,270,270),fill='#bb7744');im.save(self.root/'sticker.png')
        Image.new('RGB',(750,400),'#e6bd98').save(self.root/'banner.jpg')
    def tearDown(self):self.temp.cleanup()
    def build(self):
        config={'title':'<test>','description':'"special & text"','cover':'sticker.png','banner':'banner.jpg','stickers':[{'source':'sticker.png','meaning':'抱抱'},{'source':'sticker.png','meaning':'疑惑'}]}
        p=self.root/'project.json';p.write_text(json.dumps(config),encoding='utf-8')
        out=self.root/'result';a.build(SimpleNamespace(manifest=str(p),out=str(out)));return out
    def test_package_and_preview(self):
        out=self.build();report=a.check(out)
        self.assertFalse(report['errors']);self.assertTrue(any('重复' in w for w in report['warnings']))
        html=(out/'review.html').read_text(encoding='utf-8')
        self.assertIn('&lt;test&gt;',html);self.assertIn('main-gif/01.gif',html)
        self.assertTrue(out.with_suffix('.zip').is_file())
        with Image.open(out/'support/icon.png') as icon:self.assertEqual(icon.size,(50,50))
    def test_opaque_rejected(self):
        out=self.build();Image.new('RGB',(240,240),'white').save(out/'main-png/01.png')
        self.assertTrue(any('透明' in e for e in a.check(out)['errors']))
    def test_split_boundary_and_blank(self):
        im=Image.new('RGBA',(200,100));ImageDraw.Draw(im).rectangle((60,20,100,80),fill='red');im.save(self.root/'grid.png')
        out=self.root/'split';a.split(SimpleNamespace(sheet=str(self.root/'grid.png'),rows=1,cols=2,out=str(out)))
        report=json.loads((out/'split-report.json').read_text(encoding='utf-8'))
        self.assertTrue(report[0]['risks']);self.assertTrue(report[1]['risks'])
        self.assertTrue((out/'split-preview-dark.jpg').is_file())
    def test_split_blank(self):
        Image.new('RGBA',(100,100)).save(self.root/'blank.png')
        out=self.root/'blank';a.split(SimpleNamespace(sheet=str(self.root/'blank.png'),rows=1,cols=1,out=str(out)))
        report=json.loads((out/'split-report.json').read_text(encoding='utf-8'))
        self.assertIn('空图或主体过于透明',report[0]['risks'])
    def test_refuse_existing_directory(self):
        with self.assertRaises(FileExistsError):a.fresh(self.root)
    def test_banner_aspect(self):
        Image.new('RGB',(100,100),'red').save(self.root/'banner.jpg')
        with self.assertRaisesRegex(ValueError,'750:400'):self.build()

if __name__=='__main__':unittest.main()
