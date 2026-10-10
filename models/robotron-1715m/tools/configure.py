#!/usr/bin/env python3
"""Generate the shared key geometry/UV table; no photograph pixels are edited."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
left='PXL_20261009_132916421.MP.jpg'
right='PXL_20261009_132919894.jpg'
keys=[]
def key(label,u,row,width=1,style=0,photo=left,cx=None,cy=None,height=1):
    x=-247+u*20.0;y=35-row*20.0
    item=dict(id=f'key-{len(keys):03}',row=row,u=u,label=label,x=x,y=y,width=width,height=height,style=style)
    if cx is not None:
        # Photos are portrait, with the keyboard turned clockwise. Keep the
        # pixels untouched and rotate the UV coordinates instead.
        dx=43*height;dy=43*width
        item['photo']=photo
        item['uv']=[[ (cx+dx)/1373,(cy-dy)/1824 ],[(cx+dx)/1373,(cy+dy)/1824],[(cx-dx)/1373,(cy+dy)/1824],[(cx-dx)/1373,(cy-dy)/1824]]
    keys.append(item)
key('ALT',.75,0,1.5,1,cx=870,cy=250)
for i,label in enumerate(['1','2','3','4','5','6','7','8','9','0','ß','^']):
    key(label,2+i,0,cx=872,cy=[376,488,600,718,830,946,1058,1170,1282,1398,1510,1620][i])
key('R',14,0,photo=right,cx=850,cy=420)
key('SI SO',15.5,0,style=1,photo=right,cx=850,cy=590)
key('CTRL',.75,1,1.5,cx=755,cy=276)
for i,label in enumerate('QWERTYUIOP'):
    key(label,2.25+i,1,cx=760,cy=[430,546,660,772,884,998,1112,1222,1334,1450][i])
key('@',12.25,1,cx=748,cy=1562)
key('{',13.25,1,photo=right,cx=735,cy=330)
key('Tab',14.25,1,photo=right,cx=735,cy=443)
key('INS',15.5,1,style=1,photo=right,cx=735,cy=590)
key('DEL',16.5,1,style=1,photo=right,cx=735,cy=700)
key('Caps Lock',1,2,cx=641,cy=333)
for i,label in enumerate('ASDFGHJKL'):
    key(label,2.25+i,2,cx=646,cy=[446,564,676,794,910,1024,1136,1252,1366][i])
key('+',11.25,2,cx=646,cy=1482)
key('*',12.25,2,cx=646,cy=1596)
key('}',13.25,2,photo=right,cx=619,cy=330)
key('Shift',.75,3,1.5,cx=526,cy=253)
for i,label in enumerate(['|','Z','X','C','V','B','N','M',',','.','/']):
    key(label,2+i,3,cx=536,cy=[388,502,622,738,854,964,1078,1192,1308,1424,1538][i])
key('Shift',13.5,3,1.5,photo=right,cx=505,cy=333)
key('Space',7.5,4,8,cx=413,cy=1010)
key('ET',12.8,4,1.5,photo=right,cx=386,cy=216)
for row in (2,3,4):
    for col in range(3):
        key([['⇤','↑','⇥'],['←','↱','→'],['↵','↓','F15']][row-2][col],14.5+col,row,style=1,photo=right,cx=[0,0,620,504,386][row],cy=470+col*117)
for row,labels in enumerate([['PF1','PF2','PF3'],['7','8','9'],['4','5','6'],['1','2','3'],['0','00',',']]):
    for col,label in enumerate(labels):
        key(label,18+col,row,style=int(row==0),photo=right,cx=[845,733,616,503,382][row],cy=895+col*114)
for row,label in enumerate(['PF4','CE']):
    key(label,21.5, row,style=1 if row==0 else 2 if row==1 else 0,photo=right,cx=[844,733,618][row],cy=1302)
key('-',21.5,2.25,height=1.5,photo=right,cx=565,cy=1302)
key('↔',21.5,3.75,height=1.5,photo=right,cx=395,cy=1302)
for row in range(5):
    for col in range(2):
        key('PF'+str(5+row+5*col),23+col,row,style=1,photo=right,cx=[839,731,616,501,382][row],cy=1528+col*116)
pf=[0xd1,0xd2,0xd3,0xd4,0xcf,0xa0,0xa1,0xa2,0xa3,0x83,0xc1,0xc0,0xc2,0xcd,0x8e]
for k in keys:
    label=k['label']; k['input']={}
    if label in ['Shift','CTRL','Caps Lock']:
        k['input']={'modifier':{'Shift':'shift','CTRL':'ctrl','Caps Lock':'caps'}[label]}
    elif label.startswith('PF') or label=='F15':
        k['input']={'code':pf[int(label.replace('PF','').replace('F',''))-1]}
    elif k['u']>=18:
        code={'00':0xbb,',':0xac,'-':0xbd,'CE':0xce,'↔':0xd0}.get(label)
        if len(label)==1 and label.isdigit():code=0xb0+int(label)
        if code is not None:k['input']={'code':code}
    elif label in ['ET','Tab','INS','DEL','←','↑','→','↓','Space']:
        k['input']={'code':{'ET':13,'Tab':0x80,'INS':0x82,'DEL':0x7f,'←':0x88,'↑':0x8b,'→':0x86,'↓':0x8a,'Space':32}[label]}
    elif len(label)==1 and label.isascii() and label!='R' or (label=='R' and k['row']==1):
        base={'{':'[','}':']','+':';','*':':','|':chr(92)}.get(label,label.lower())
        shifted={'1':'!','2':'"','3':'#','5':'%','6':'&','7':"'",'8':'(','9':')','0':'_',',':'<','.':'>','/':'?','{':'{','}':'}','+':'+','*':'*','|':'|'}.get(label)
        if label.isalpha():shifted=label
        k['input']={'code':ord(base)}
        if shifted:k['input']['shiftCode']=ord(shifted)
        else:k['input']['shiftUnsupported']=True
        k['input']['letter']=label.isalpha()
    if not k['input']:k['input']={'unsupported':'This key’s specimen-specific encoding is not verified yet.'}
# Visible legends transcribed from the photos, independent of input support.
# Blank Shift/Space and the unlettered Caps key stay blank as on the specimen.
paired={'1':['!','1'],'2':['"','2'],'3':['#','3'],'4':['¤','4'],
        '5':['%','5'],'6':['&','6'],'7':["'",'7'],'8':['(','8'],
        '9':[')','9'],'0':['_','0'],'ß':['?','ß'],'^':['_','^'],
        '{':['{','['],'}':['}',']'],'+':['+',';'],'*':['*',':'],
        '|':['|',chr(92)],',':['<',','],'.':['>','.'],'/':['?','/']}
for k in keys:
    label=k['label']
    k['legend']=[] if label in ['Space','Shift','Caps Lock'] else [label]
    if k['u']<18 and label in paired:k['legend']=paired[label]
    if label=='Tab':k['legend']=['→']
    if label=='SI SO':k['legend']=['SI','SO']
    if label=='R' and k['row']==0:k['legend']=['Ⓡ']
(root/'keyboard-layout.json').write_text(json.dumps(keys,indent=2)+'\n')
lines=['// Generated by tools/configure.py; positions share browser photo UV data.','// [x, y, width in pitches, height in pitches, material group]','keys = [']
lines += ['  '+json.dumps([k['x'],k['y'],k['width'],k['height'],k['style']])+(',' if i<len(keys)-1 else '')+' // '+k['label'] for i,k in enumerate(keys)]
(root/'keyboard-layout.scad').write_text('\n'.join(lines+ ['];'])+'\n')
print(len(keys),'reference-based keys')

profile=json.loads((root/'monitor-profile.json').read_text())
g=profile['glass']
values={'monitor_seam_fraction':profile['seamFraction'],'crt_size':g['size'],'crt_position':g['position'],'crt_power':g['outlinePower'],'crt_depth':g['depth'],'crt_radii':g['radii'],'crt_back':g['backThickness']}
(root/'monitor-profile.scad').write_text('// Generated from monitor-profile.json; shared with the browser.\n'+'\n'.join(k+' = '+json.dumps(v)+';' for k,v in values.items())+'\n')

# Raised package outlines share source-photo landmarks with the browser decals.
boards=json.loads((root/'pcb-references.json').read_text())
packages=[]
for b in boards:
    x0,y0,x1,y1=b['crop'];w,h=b['size'];ox,oy,oz=b['origin']
    for x,y,pw,ph in b['packages']:
        u=(x-x0)/(x1-x0);v=(y-y0)/(y1-y0)
        du=pw/(x1-x0);dv=ph/(y1-y0)
        if b['rotated']:box=[ox+(1-v-dv)*w,oy+(1-u-du)*h,oz,dv*w,du*h,b['packageHeight']]
        else:box=[ox+u*w,oy+(1-v-dv)*h,oz,du*w,dv*h,b['packageHeight']]
        packages.append(box)
(root/'pcb-packages.scad').write_text('// Generated from pcb-references.json; approximate photographed package outlines.\npcb_packages='+json.dumps(packages)+';\n')
