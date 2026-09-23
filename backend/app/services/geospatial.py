from rasterio.io import MemoryFile
from rasterio.transform import xy
from pyproj import Transformer
import numpy as np

def inspect(content, filename):
    with MemoryFile(content) as m:
        with m.open() as s:
            b=s.bounds
            return {'filename':filename,'width':s.width,'height':s.height,'bands':s.count,'crs':str(s.crs) if s.crs else None,'bounds':{'left':b.left,'bottom':b.bottom,'right':b.right,'top':b.top},'band_descriptions':list(s.descriptions or []),'dtypes':list(s.dtypes or [])}

def bbox_feature(content,bbox,space='pixel'):
    with MemoryFile(content) as m:
        with m.open() as s:
            w,h=s.width,s.height; x1,y1,x2,y2=map(float,bbox)
            if space=='normalized_1': x1,x2=x1*w,x2*w; y1,y2=y1*h,y2*h
            elif space=='normalized_1000': x1,x2=x1/1000*w,x2/1000*w; y1,y2=y1/1000*h,y2/1000*h
            x1,x2=max(0,min(w,x1)),max(0,min(w,x2)); y1,y2=max(0,min(h,y1)),max(0,min(h,y2))
            pts=[xy(s.transform,y1,x1,offset='center'),xy(s.transform,y1,x2,offset='center'),xy(s.transform,y2,x2,offset='center'),xy(s.transform,y2,x1,offset='center')]
            if s.crs:
                tr=Transformer.from_crs(s.crs,'EPSG:4326',always_xy=True); pts=[tr.transform(x,y) for x,y in pts]; crs='EPSG:4326'
            else: crs=None
            coords=[[float(x),float(y)] for x,y in pts]; coords.append(coords[0])
            return {'type':'Feature','geometry':{'type':'Polygon','coordinates':[coords]},'properties':{'pixel_bbox':[x1,y1,x2,y2],'source_crs':str(s.crs) if s.crs else None,'geojson_crs':crs}}

def ndvi(content):
    with MemoryFile(content) as m:
        with m.open() as s:
            if s.count<8: raise ValueError('NDVI needs at least 8 bands for standard Sentinel-2 ordering.')
            red=s.read(4).astype(np.float32); nir=s.read(8).astype(np.float32); den=nir+red
            a=np.divide(nir-red,den,out=np.zeros_like(den),where=np.abs(den)>1e-12); a=a[np.isfinite(a)]
            return {'method':'(B08-B04)/(B08+B04)','band_assumption':'standard Sentinel-2 order','min':float(a.min()),'max':float(a.max()),'mean':float(a.mean()),'median':float(np.median(a)),'vegetation_fraction_ndvi_gt_0_3':float(np.mean(a>0.3))}
