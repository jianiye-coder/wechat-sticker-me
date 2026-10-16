#!/usr/bin/env python3
"""List starter templates or create an editable creative brief; no image/network actions."""
import argparse
import json
from pathlib import Path

CATALOG=Path(__file__).resolve().parents[1]/'templates/catalog.json'

def instantiate(template_id, style=None, title=None):
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    templates={t['id']:t for t in catalog['templates']}
    if template_id not in templates:raise ValueError(f'未知模板: {template_id}')
    t=templates[template_id];style_id=style or t['style']
    if style_id not in catalog['styles']:raise ValueError(f'未知画风: {style_id}')
    visual=catalog['styles'][style_id]
    return {'template_id':t['id'],'template_name':t['name'],'style':{'id':style_id,**visual},'tone':t['tone'],'palette_example':t.get('palette_example',{}),'visual_direction':t.get('visual_direction',''),'title':title or t['title_example'],'description':t['description_example'],'title_availability':'未查询，不能保证可用','identity_constraints':{},'reference_images':[],'trial':t['trial'],'stickers':[{'number':i,'meaning':s['meaning'],'action':s['action'],'status':'planned'} for i,s in enumerate(t['stickers'],1)],'cover_direction':t['cover_direction'] if style_id==t['style'] else f'采用{visual["name"]}画风；以同一角色的单个完整表情作为无文字独立封面，保持风格一致。','banner_direction':t['banner_direction'],'spec_status':'待平台复核','workflow_status':'创意草案；未生成，未上传','notes':['16项为可编辑的选题起点，不代表官方数量要求。','这是创意草案，不是prepare_assets.py build的源图清单；生成后填写实际source路径。']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('template',nargs='?');p.add_argument('--style');p.add_argument('--title');p.add_argument('--out');args=p.parse_args()
    if not args.template:
        c=json.loads(CATALOG.read_text(encoding='utf-8'))
        print(json.dumps({'templates':[{'id':t['id'],'name':t['name'],'style':t['style'],'tone':t['tone']} for t in c['templates']],'styles':c['styles']},ensure_ascii=False,indent=2));return
    brief=instantiate(args.template,args.style,args.title)
    content=json.dumps(brief,ensure_ascii=False,indent=2)
    if args.out:
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as f:f.write(content+'\n')
        print(path)
    else:print(content)

if __name__=='__main__':main()
