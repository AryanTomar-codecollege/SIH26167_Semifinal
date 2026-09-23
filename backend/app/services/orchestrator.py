import json
from app.services.omniroute import omniroute
from app.services.geospatial import inspect
from app.tools.all_tools import TOOLS

ROUTER='''You are the SatQuery AI router. Choose exactly one tool and return ONLY JSON: {"tool":"...","reason":"..."}. Tools: metadata, vqa, caption, grounding, compare, change_detection, ndvi, flood_analysis. Rules: 2+ images + change/before/after/difference -> change_detection; 2+ + compare -> compare; where/locate/find/highlight -> grounding; NDVI/vegetation index -> ndvi; flood/flooded -> flood_analysis; CRS/bounds/bands/dimensions -> metadata; describe/caption -> caption; otherwise vqa.'''

def fallback(q,n):
    x=q.lower()
    if n>=2 and any(k in x for k in ['change','changed','before','after','difference']): return 'change_detection'
    if n>=2 and 'compar' in x: return 'compare'
    if 'ndvi' in x or 'vegetation index' in x: return 'ndvi'
    if 'flood' in x: return 'flood_analysis'
    if any(k in x for k in ['where','locate','find','highlight','ground']): return 'grounding'
    if any(k in x for k in ['crs','bounds','bands','width','height','metadata']): return 'metadata'
    if 'describ' in x or 'caption' in x: return 'caption'
    return 'vqa'

def synthesize(q,tool,evidence):
    compact=dict(evidence)
    for k in ['earthdial']:
        if isinstance(compact.get(k),dict): compact[k]={x:compact[k].get(x) for x in ['answer','metadata','inference_time_seconds']}
    return omniroute.chat([{'role':'system','content':'Answer the original remote-sensing question using only the tool evidence. Do not invent coordinates or measurements. If grounding returned GeoJSON, describe it briefly. If a fallback was used, mention it.'},{'role':'user','content':json.dumps({'query':q,'tool':tool,'evidence':compact},ensure_ascii=False)}],temperature=.1,max_tokens=1000)

def execute(q,files):
    metas=[inspect(c,n) for n,c,_ in files]
    decision=''
    try:
        raw=omniroute.chat([{'role':'system','content':ROUTER},{'role':'user','content':json.dumps({'query':q,'file_count':len(files),'files':metas})}],max_tokens=200)
        parsed=omniroute.parse_json(raw); tool=parsed.get('tool') if parsed else None; decision=(parsed or {}).get('reason','OmniRoute selection')
    except Exception:
        tool=None; decision='Deterministic fallback router'
    if tool not in TOOLS: tool=fallback(q,len(files))
    result=TOOLS[tool](files,q)
    try: answer=synthesize(q,tool,result)
    except Exception: answer=result.get('answer','Tool execution completed.')
    return {'success':True,'answer':answer,'tool':tool,'execution_trace':[{'step':'route','tool':tool,'reason':decision},{'step':'execute','tool':tool,'file_count':len(files)},{'step':'synthesize','provider':'OmniRoute'}],'geojson':result.get('geojson',{'type':'FeatureCollection','features':[]}), 'metadata':metas,'raw':result}
