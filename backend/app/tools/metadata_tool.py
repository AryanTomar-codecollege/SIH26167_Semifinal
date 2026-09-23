from app.services.geospatial import extract_metadata


def run(filepath: str) -> dict:
    return extract_metadata(filepath)
