from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.health import router as health_router
from app.routers.query import router as query_router
app=FastAPI(title='SatQuery AI Backend',version='2.0.0')
origins=['*'] if settings.cors_origins=='*' else [x.strip() for x in settings.cors_origins.split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(health_router)
app.include_router(query_router, prefix="/api")
app.include_router(query_router)

@app.get('/')
def root(): return {'status':'SatQuery AI backend is running','service':'EarthDial + OmniRoute'}
