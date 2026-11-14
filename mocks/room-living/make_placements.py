# Regenerates placements.json for the lounge from the Collection (v2, 6 Nov 2026 feedback: his Edge-tab listings).
import json,urllib.request,os
al=json.load(open('all2.json',encoding='utf8'))
al.append({"id":"e716af29-6b6a-49bb-a10e-949435ead6fe","name":"Enfurnish Sheesham Wood Coffee Table with Shelf, Walnut Finish","model_url":"x","buy_link":"https://www.amazon.in/dp/B0CGNPGT6K?tag=urbannest03b-21","description":"Solid sheesham wood coffee table with a lower shelf for books and remotes, in a rich walnut polish."})
def G(p): return next(i for i in al if i['id'].startswith(p))
def dl(p,name):
    g=G(p); f='products/'+name+'.glb'
    if not os.path.exists(f): urllib.request.urlretrieve(g['model_url'].replace(' ','%20'),f)
    return name+'.glb'
def first(s):
    s=' '.join(s.split())
    for sep in ('. ','! '):
        if sep in s: s=s.split(sep)[0]+'.'
    return s[:220]
def prod(pid,fn,name,tag,specs,extra,**kw):
    g=G(pid); d={"id":g['id'],"name":name,"file":dl(pid,fn),"tag":"THE COLLECTION · "+tag,"desc":first(g['description']),"specs":specs,"link":g['buy_link'],"listing":g['name']}
    d.update(kw); d.update(extra or {}); return d
P=[]
P.append(prod('a18cf5ad','liv-chandelier','Victorian Crystal Chandelier','LIGHTING',[["Material","Metal, glass and crystal"],["Dimensions","80 × 80 × 70 cm"],["Light","12 candle bulbs, E14"]],{"hang":True,"noShadow":True},height=0.82,pos=[0.15,2.99,-0.1]))
P.append(prod('0c9ab81d','liv-gond-set','Gond Art Set of Six','WALL ART',[["Frames","Six framed Gond prints"],["Size","43 × 33 cm each"],["Maker","kotart"]],{"alignBack":-2.064,"noShadow":True},height=0.74,pos=[-1.2,1.5,0]))
P.append(prod('872070ef','liv-seven-horses','Seven Running Horses','SCULPTURES',[["Material","Resin"],["Length","19 inch"],["Style","Vastu, Feng Shui"]],None,length=0.48,pos=[-1.75,0.82,-1.86],rotY=0.2))
P.append(prod('fc8422e3','liv-hampi-chariot','Hampi Stone Chariot','SCULPTURES',[["Material","Stone"],["Dimensions","23 × 16 × 18 cm"],["Maker","SILAII"]],None,height=0.18,pos=[2.38,0.502,0.85]))
P.append(prod('9adffab2','liv-ball-vase','Crackled Metal Ball Vase','VASES',[["Material","Metal, crackled finish"],["Dimensions","17 × 17 × 17 cm"],["Brand","BEHOMA"]],None,height=0.34,pos=[-0.6,0.82,-1.86]))
P.append(prod('f6355faf','liv-dogwood-vase','Brass Dogwood Steel Vase','VASES',[["Material","Stainless steel, brass dogwood"],["Dimensions","17 × 15 × 20.5 cm"],["Brand","BEHOMA"]],None,height=0.38,pos=[0.15,0.357,-0.30]))
P.append(prod('cde2a73b','liv-cylinder-lamp','Cotton Fabric Floor Lamp','LUMINAIRES',[["Shade","Cotton fabric"],["Style","Slim column"],["Placement","Floor"]],{"light":{"w":22}},height=1.0,pos=[-2.35,0,-1.85]))
P.append(prod('966832fa','liv-globe-wall-lamp','5-Globe Wall Lamp','LUMINAIRES',[["Style","Bubble globes"],["Mount","Wall"],["Maker","The Crafted Gesture"]],{"glow":1.1,"light":{"w":14,"at":[1.9,1.95,1.75]}},height=0.5,pos=[1.9,1.75,0],rotY=3.14159,alignBack=-2.07,noShadow=True))
P.append(prod('5e586bdd','liv-side-table-wood','Wooden Side Table','FURNITURE',[["Shape","Square"],["Size","30.5 × 30.5 × 43.2 cm"],["Tiers","Two"]],{"view":{"pos":[1.2,1.3,-0.4],"target":[1.25,0.3,-1.88]}},height=0.55,pos=[1.25,0,-1.88]))
P.append(prod('b2b696ae','liv-craftel-clock','Double-Sided Station Clock','TIMEPIECES',[["Style","Station clock on bracket"],["Size","20 cm dial"],["Maker","Craftel"]],{"noShadow":True},height=0.55,pos=[2.55,1.8,1.15],rotY=3.14159,alignRight=2.59))
P.append(prod('9677aca6','liv-paper-plane-canvas','Modern Abstract Canvas','WALL ART',[["Size","122 × 81 cm"],["Maker","Paper Plane Design"],["Style","Modern abstract"]],{"noShadow":True},height=1.45,pos=[1.75,1.05,2.085],rotY=3.14159))
P.append(prod('e9b931ae','liv-artsense-flower-canvas','Woman with Flower Canvas','WALL ART',[["Size","20 × 30 inch"],["Style","Abstract, framed"],["Maker","Artsense"]],{"noShadow":True},height=0.76,pos=[-2.575,1.65,1.2],rotY=1.5708,alignLeft=-2.59))
P.append(prod('5046156b','liv-floral-lamp','Floral Floor Lamp','LUMINAIRES',[["Shade","Floral fabric"],["Frame","Black metal"],["Maker","Homesake"]],{"light":{"w":22}},height=1.5,pos=[-2.3,0,1.8]))
P.append(prod('d833fde8','liv-lexton-lamp','Adjustable Study Lamp','LUMINAIRES',[["Material","Metal, swing arm"],["Size","31 × 12 × 31 cm"],["Maker","Lexton"]],{"light":{"w":18,"at":[2.33,1.76,0.85]}},height=0.31,pos=[2.33,0.553,-1.76],rotY=-1.2,view={"pos":[1.5,2.2,-0.3],"target":[2.33,0.6,-1.76]}))
P.append(prod('79601e90','liv-silver-bansuri','Silver Krishna Bansuri','SCULPTURES',[["Material","999 pure silver"],["Size","23.5 × 9.3 × 15.7 cm"],["Brand","TOUCH925"]],None,length=0.235,pos=[0.15,0.357,0.20],rotY=1.5708,view={"pos":[-0.55,0.95,0.85],"target":[0.15,0.46,0.2]}))
P.append(prod('e716af29','liv-sheesham-table','Sheesham Coffee Table with Shelf','FURNITURE',[["Material","Solid sheesham wood"],["Size","86 × 46 × 46 cm"],["Finish","Walnut polish"]],None,length=0.92,pos=[0.15,0,-0.1],rotY=1.5708))
out=json.load(open('placements.json',encoding='utf8')); out['products']=P
# the furniture, split out of the baked room as movable pieces (split_furniture.py): no dot, 'lm' = it carries its own baked light
out['staging']=[dict(name=i['name'],file=i['file'],height=i['height'],pos=i['pos'],lm=True) for i in json.load(open('split_info.json',encoding='utf8'))] if os.path.exists('split_info.json') else []
# his layout saved from admin Rooms (saved_layout.json, fetched from Storage) wins over the defaults above
if os.path.exists('saved_layout.json'):
    sv=json.load(open('saved_layout.json',encoding='utf8')); keep=['pos','rotY','height','length','alignBack','alignLeft','alignRight','view','hang']
    for kind in ('products','staging'):
        for d in out[kind]:
            o=next((x for x in sv[kind] if x.get('file')==d['file'] and x.get('pos')==x.get('pos') and x.get('name')==d['name']),None) or next((x for x in sv[kind] if x.get('file')==d['file']),None)
            if o:
                for k in keep:
                    if k in o: d[k]=o[k]
                    elif k in d and k in ('rotY','view') and k not in o: d.pop(k)
json.dump(out,open('placements.json','w',encoding='utf8'),indent=1,ensure_ascii=False)
print(len(P),'products')
