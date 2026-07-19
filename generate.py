#!/usr/bin/env python3
from pathlib import Path
import zipfile, xml.etree.ElementTree as ET, re, json, shutil, sys

ROOT = Path(__file__).resolve().parent
WORKBOOK = ROOT / "Clipboard_v4_Master_Base.xlsx"
BUILD = ROOT / "clipboard_generated"
NS = {"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def col_num(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n=0
    for ch in letters: n=n*26+ord(ch)-64
    return n

def read_workbook(path):
    with zipfile.ZipFile(path) as z:
        sst=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            root=ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('m:si',NS):
                sst.append(''.join(t.text or '' for t in si.iter('{%s}t'%NS['m'])))
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rmap={r.attrib['Id']:r.attrib['Target'] for r in rels}
        sheets={}
        for sh in wb.find('m:sheets',NS):
            name=sh.attrib['name']; rid=sh.attrib['{%s}id'%NS['r']]
            target=rmap[rid].lstrip('/')
            if not target.startswith('xl/'): target='xl/'+target
            xml=ET.fromstring(z.read(target))
            rows=[]
            for row in xml.findall('.//m:sheetData/m:row',NS):
                vals={}
                for c in row.findall('m:c',NS):
                    ref=c.attrib['r']; typ=c.attrib.get('t'); v=c.find('m:v',NS)
                    val=''
                    if v is not None:
                        raw=v.text or ''
                        val=sst[int(raw)] if typ=='s' and raw else raw
                    elif typ=='inlineStr':
                        val=''.join(t.text or '' for t in c.iter('{%s}t'%NS['m']))
                    vals[col_num(ref)] = val
                if vals:
                    mx=max(vals); rows.append([vals.get(i,'') for i in range(1,mx+1)])
            sheets[name]=rows
        return sheets

def records(rows):
    if not rows: return []
    headers=[str(x).strip() for x in rows[0]]
    out=[]
    for r in rows[1:]:
        if not any(str(x).strip() for x in r): continue
        d={}
        for i,h in enumerate(headers):
            if not h: continue
            v=r[i] if i<len(r) else ''
            if h=='Display Order' and str(v).strip():
                try: v=int(float(v))
                except: pass
            elif h=='Default Value' and str(v).strip():
                sv=str(v).strip()
                if re.fullmatch(r'-?\d+(?:\.0+)?',sv): v=int(float(sv))
            if v!='': d[h]=v
        out.append(d)
    return out

def build_config(s):
    app=records(s.get('APP DESIGN',[]))
    followups=records(s.get('FOLLOW-UP TEMPLATES',[]))
    lists={}
    rows=s.get('Lists',[])
    if rows:
        heads=rows[0]
        for i,h in enumerate(heads):
            h=str(h).strip()
            if h: lists[h]=[r[i] for r in rows[1:] if i<len(r) and str(r[i]).strip()]
    settings={}
    for r in s.get('Settings',[])[1:]:
        if len(r)>=2 and str(r[0]).strip(): settings[str(r[0]).strip()]=r[1]
    settings['Version']='4.2.1'
    settings['Workbook Role']='Live master configuration for Clipboard v4'
    nav=[]
    for r in s.get('Navigation',[])[1:]:
        if len(r)>=2 and str(r[1]).strip(): nav.append((float(r[0]) if str(r[0]).strip() else 999,r[1]))
    nav=[x[1] for x in sorted(nav)]
    return {'app':app,'followups':followups,'lists':lists,'settings':settings,'navigation':nav}

def validate(cfg):
    issues=[]
    ids=[x.get('Field ID') for x in cfg['app'] if x.get('Field ID')]
    if len(ids)!=len(set(ids)): issues.append('Duplicate APP DESIGN Field IDs')
    fids=[x.get('Field ID') for x in cfg['followups'] if x.get('Field ID')]
    if len(fids)!=len(set(fids)): issues.append('Duplicate follow-up Field IDs')
    for f in cfg['app']+cfg['followups']:
        opt=f.get('Options')
        if opt and opt not in cfg['lists']: issues.append(f"Missing list {opt} for {f.get('Field ID','?')}")
    return sorted(set(issues))

def main():
    if not WORKBOOK.exists():
        print(f'ERROR: Workbook not found: {WORKBOOK}')
        return 1
    sheets=read_workbook(WORKBOOK)
    cfg=build_config(sheets)
    issues=validate(cfg)
    BUILD.mkdir(exist_ok=True)
    (BUILD/'config.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf-8')
    for name in ('index.html','app-v4-2-1.js','manifest.json'):
        shutil.copy2(ROOT/'app_template'/name, BUILD/name)
    report=[
        'Clipboard v4 workbook validation',
        f"Workbook: {WORKBOOK.name}",
        f"APP DESIGN fields: {len(cfg['app'])}",
        f"Follow-up questions: {len(cfg['followups'])}",
        f"Lists: {len(cfg['lists'])}",
        f"Navigation tabs: {len(cfg['navigation'])}",
        f"Issues: {len(issues)}",
    ] + [f'- {x}' for x in issues]
    (ROOT/'VALIDATION.txt').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print('\n'.join(report))
    print(f'Generated: {BUILD}')
    return 1 if issues else 0

if __name__=='__main__': raise SystemExit(main())
