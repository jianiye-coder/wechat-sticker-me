#!/usr/bin/env python3
"""Deterministic WeChat sticker candidates; Pillow required. No network or upload."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile
from PIL import Image, ImageDraw

SIZES = {'main':(240,240),'thumb':(120,120),'cover':(240,240),'icon':(50,50),'banner':(750,400)}
LIMITS = {'main':100_000,'thumb':50_000,'cover':80_000,'icon':30_000,'banner':80_000}

def load(path):
    with Image.open(path) as im:
        return im.convert('RGBA')

def fit(im, size, pad=0):
    im=im.copy(); im.thumbnail((size[0]-2*pad,size[1]-2*pad),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size)
    canvas.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
    return canvas

def png(im,path,limit):
    im.save(path,optimize=True)
    if path.stat().st_size>limit:
        im.quantize(colors=256,method=Image.Quantize.FASTOCTREE).save(path,optimize=True)
    if path.stat().st_size>limit:
        raise ValueError(f'文件仍超限，需另行优化: {path}')

def gif(im,path):
    rgb=Image.new('RGB',im.size,'white'); rgb.paste(im,mask=im.getchannel('A'))
    pal=rgb.quantize(colors=255,method=Image.Quantize.MEDIANCUT)
    alpha=list(im.getchannel('A').getdata())
    pal.putdata([v if a>=128 else 255 for v,a in zip(pal.getdata(),alpha)])
    pal.putpalette(pal.getpalette()[:765]+[255,255,255])
    pal.save(path,transparency=255,optimize=False)

def fresh(path):
    path=Path(path).resolve();path.mkdir(parents=True,exist_ok=False);return path

def split(args):
    if args.rows<=0 or args.cols<=0: raise ValueError('行列必须大于0')
    out=fresh(args.out); im=load(args.sheet);w,h=im.size
    for r in range(args.rows):
        for c in range(args.cols):
            box=(round(c*w/args.cols),round(r*h/args.rows),round((c+1)*w/args.cols),round((r+1)*h/args.rows))
            im.crop(box).save(out/f'{r*args.cols+c+1:02d}.png')
    (out/'检查提示.txt').write_text('网格拆分未做内容识别：请逐张检查串格、截断、空白和文字；不要直接当作已验证投稿素材。\n',encoding='utf-8')
    print(out)

def check(root):
    root=Path(root).resolve(); manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    errors=[];warnings=[];rows=[]
    for rec in manifest['files']:
        path=root/rec['path'];kind=rec['kind']
        if not path.is_file():errors.append(f'缺少文件: {path.name}');continue
        with Image.open(path) as raw:
            im=raw.convert('RGBA');size=raw.size;fmt=raw.format;frames=getattr(raw,'n_frames',1)
        n=path.stat().st_size
        if size!=SIZES[kind]:errors.append(f'{path.name}: 尺寸{size}')
        if n>LIMITS[kind]:errors.append(f'{path.name}: 超过保守体积目标')
        if fmt not in ({'JPEG'} if kind=='banner' else {'PNG','GIF'}):errors.append(f'{path.name}: 格式不符')
        if frames!=1:errors.append(f'{path.name}: 本工具只打包静态表情')
        a=im.getchannel('A');lo,hi=a.getextrema()
        if kind!='banner':
            if lo==255:errors.append(f'{path.name}: 缺少真实透明背景')
            if hi==0:errors.append(f'{path.name}: 完全空白')
            box=a.point(lambda x:255 if x>=128 else 0).getbbox()
            if box and kind=='main' and min(box[0],box[1],size[0]-box[2],size[1]-box[3])<4:
                warnings.append(f'{path.name}: 安全边距不足4像素')
        rows.append({'file':rec['path'],'size':list(size),'bytes':n,'format':fmt})
    report={'engineering_checks_passed':not errors,'platform_approval':False,'spec_status':manifest.get('spec_status','待平台复核'),'errors':errors,'warnings':warnings,'files':rows}
    (root/'检查报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

def build(args):
    source=Path(args.manifest).resolve(); data=json.loads(source.read_text(encoding='utf-8'))
    stickers=data['stickers']
    if not stickers:raise ValueError('表情清单不能为空')
    for key in ['title','description','cover','banner']:
        if not data.get(key):raise ValueError(f'缺少{key}')
    meanings=[s['meaning'].strip() for s in stickers]
    if any(not s for s in meanings):raise ValueError('含义词不能为空')
    if len(set(meanings))!=len(meanings):raise ValueError('含义词重复，请确认逐图映射')
    def path(s):
        p=Path(s);return p if p.is_absolute() else source.parent/p
    # Validate inputs before creating the output folder.
    for p in [s['source'] for s in stickers]+[data['cover'],data['banner']]+([data['icon']] if data.get('icon') else []):
        if not path(p).is_file():raise FileNotFoundError(p)
    out=fresh(args.out)
    for name in ['main-png','main-gif','thumbnails','support','masters']:(out/name).mkdir()
    manifest={'title':data['title'],'description':data['description'],'spec_status':data.get('spec_status','待平台复核'),'stickers':[],'files':[]}
    def record(p,kind):manifest['files'].append({'path':str(p.relative_to(out)),'kind':kind})
    thumbs=[]
    for i,s in enumerate(stickers,1):
        original=load(path(s['source'])); alpha=original.getchannel('A')
        if alpha.getextrema()[0]==255 or not alpha.getbbox():raise ValueError(f'{i}: 需提供独立非空透明图')
        shutil.copy2(path(s['source']),out/'masters'/f'{i:02d}{path(s["source"]).suffix}')
        image=fit(original.crop(alpha.getbbox()),SIZES['main'],10)
        for folder,ext in [('main-png','png'),('main-gif','gif')]:
            p=out/folder/f'{i:02d}.{ext}'
            png(image,p,LIMITS['main']) if ext=='png' else gif(image,p)
            record(p,'main')
        p=out/'thumbnails'/f'{i:02d}.png';png(fit(image,SIZES['thumb']),p,LIMITS['thumb']);record(p,'thumb')
        manifest['stickers'].append({'number':i,'meaning':meanings[i-1],'png':f'main-png/{i:02d}.png','gif':f'main-gif/{i:02d}.gif'})
        thumbs.append(image)
    for key in ['cover','icon']:
        original=load(path(data.get(key,data['cover'])));a=original.getchannel('A')
        if a.getextrema()[0]==255 or not a.getbbox():raise ValueError(f'{key}: 源图需真实透明背景')
        p=out/'support'/f'{key}.png';png(fit(original,SIZES[key]),p,LIMITS[key]);record(p,key)
    banner=load(path(data['banner']))
    if banner.getchannel('A').getextrema()[0]<255:raise ValueError('横幅需用户已确认的不透明背景，不自动填白')
    if banner.width*400!=banner.height*750:raise ValueError('横幅源图需750:400比例，避免拉伸或裁切内容')
    banner=banner.convert('RGB').resize(SIZES['banner'],Image.Resampling.LANCZOS);p=out/'support'/'banner.jpg'
    for quality in [92,85,75,65,55,45]:
        banner.save(p,quality=quality,optimize=True)
        if p.stat().st_size<=LIMITS['banner']:break
    record(p,'banner')
    # Both backgrounds expose transparent halos and dark edges.
    for bg,label in [('#faf6f1','light'),('#30343b','dark')]:
        preview=Image.new('RGB',(960,((len(thumbs)+3)//4)*240),bg)
        for i,t in enumerate(thumbs):preview.paste(t,((i%4)*240,(i//4)*240),t)
        preview.save(out/f'preview-{label}.jpg',quality=90)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    words='\n'.join(f'{i:02d} {s}' for i,s in enumerate(meanings,1))
    (out/'上传文案.txt').write_text(f'专辑名称：{data["title"]}\n简介：{data["description"]}\n\n含义词：\n{words}\n\nPNG/GIF是同一套静态表情的格式备选，选一种上传。\n当前规格状态：{manifest["spec_status"]}\n版权署名/授权/AI申报请本人按实际情况填写；未代填或投稿。\n机器检查不代表视觉检查、官方规格核实或审核通过。\n',encoding='utf-8')
    report=check(out)
    if report['errors']:raise ValueError('检查未通过：'+ '; '.join(report['errors']))
    dest=out.with_name(out.name+'.zip')
    if dest.exists():raise FileExistsError(dest)
    with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
        for p in out.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(out.parent))
    print(json.dumps({'package':str(out),'zip':str(dest),'warnings':report['warnings'],'spec_status':manifest['spec_status']},ensure_ascii=False))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('split',help='Split a regular grid without editing content');p.add_argument('--sheet',required=True);p.add_argument('--rows',required=True,type=int);p.add_argument('--cols',required=True,type=int);p.add_argument('--out',required=True);p.set_defaults(func=split)
    p=sub.add_parser('build',help='Build static upload candidates from reviewed sources');p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);p.set_defaults(func=build)
    p=sub.add_parser('check',help='Check an existing generated package');p.add_argument('--package',required=True)
    args=parser.parse_args()
    if args.command=='check':
        report=check(args.package);print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(1 if report['errors'] else 0)
    args.func(args)

if __name__=='__main__':main()
