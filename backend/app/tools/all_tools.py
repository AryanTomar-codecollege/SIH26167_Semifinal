import re
from app.services.earthdial import earthdial
from app.services.geospatial import inspect, bbox_feature, ndvi

def metadata(files, q=None): return {'tool':'metadata','results':[inspect(c,n) for n,c,_ in files]}
def vqa(files,q):
    if len(files)!=1: raise ValueError('VQA expects exactly one image.')
    r=earthdial.infer(files[0],q,'[caption]'); return {'tool':'vqa','answer':r.get('answer',''),'earthdial':r}
def caption(files,q):
    if len(files)!=1: raise ValueError('Caption expects exactly one image.')
    r=earthdial.infer(files[0],q or 'Describe the important remote-sensing features visible in this image.','[caption]'); return {'tool':'caption','answer':r.get('answer',''),'earthdial':r}
def grounding(files,q):
    if len(files)!=1: raise ValueError('Grounding expects exactly one image.')
    r=earthdial.infer(files[0],q,'[grounding]'); ans=r.get('answer',''); feats=[]
    matches=re.findall(r'<box>\s*([^<]+?)\s*</box>',ans,re.I|re.S)
    if not matches: matches=re.findall(r'\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]',ans)
    for raw in matches:
        nums=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',raw if isinstance(raw,str) else ','.join(raw))]
        if len(nums)>=4:
            b=nums[-4:]; mx=max(b); sp='normalized_1' if mx<=1 else ('normalized_1000' if mx<=1000 else 'pixel')
            try: feats.append(bbox_feature(files[0][1],b,sp))
            except Exception: pass
    return {'tool':'grounding','answer':ans,'boxes_found':len(feats),'geojson':{'type':'FeatureCollection','features':feats},'earthdial':r}
def compare(files,q):
    if len(files)<2: raise ValueError('Compare needs at least two images.')
    rs=[earthdial.infer(f,'Describe important land-cover, water, vegetation and built features for comparison.','[caption]') for f in files]
    return {'tool':'compare','image_results':rs}
def change(files,q):
    if len(files)<2: raise ValueError('Change detection needs at least two images.')
    try: return dict(earthdial.infer_multi(files,q or 'Identify important changes between these images.','[changedet]'),tool='change_detection',mode='joint_earthdial')
    except Exception as e:
        if str(e)!='MULTI_ENDPOINT_NOT_AVAILABLE': raise
        rs=[earthdial.infer(f,'Describe features useful for comparing this image with another date.','[caption]') for f in files]
        return {'tool':'change_detection','mode':'independent_images_fallback','individual_results':rs}
def ndvi_tool(files,q):
    if len(files)!=1: raise ValueError('NDVI expects exactly one image.')
    x=ndvi(files[0][1]); return {'tool':'ndvi','answer':f"Mean NDVI {x['mean']:.4f}; median {x['median']:.4f}; fraction >0.3 {x['vegetation_fraction_ndvi_gt_0_3']:.2%}.",'ndvi':x}
def flood(files,q):
    if len(files)!=1: raise ValueError('Flood analysis expects one image.')
    r=earthdial.infer(files[0],q or 'Identify areas that appear flooded or covered by water and describe their approximate locations.','[grounding]'); return {'tool':'flood_analysis','answer':r.get('answer',''),'earthdial':r}
TOOLS={'metadata':metadata,'vqa':vqa,'caption':caption,'grounding':grounding,'compare':compare,'change_detection':change,'ndvi':ndvi_tool,'flood_analysis':flood}
