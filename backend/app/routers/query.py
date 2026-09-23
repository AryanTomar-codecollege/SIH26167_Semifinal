from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException


router = APIRouter()


@router.post("/query")
async def query(
    files: List[UploadFile] = File(...),
    query: str = Form(...),
):
    """
    Main SatQuery AI query endpoint.

    Accepts:
        - 1 to 3 GeoTIFF files
        - A text query

    Example:
        files = [image1.tif]
        query = "What is visible in this satellite image?"
    """

    # ---------------------------------------------------------
    # 1. Validate query
    # ---------------------------------------------------------

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    # ---------------------------------------------------------
    # 2. Validate number of files
    # ---------------------------------------------------------

    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one GeoTIFF file is required."
        )

    if len(files) > 3:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 3 files can be uploaded."
        )

    # ---------------------------------------------------------
    # 3. Validate uploaded files
    # ---------------------------------------------------------

    allowed_extensions = {".tif", ".tiff"}

    file_information = []

    for uploaded_file in files:

        filename = uploaded_file.filename or ""

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="One of the uploaded files has no filename."
            )

        extension = ""

        if "." in filename:
            extension = "." + filename.rsplit(".", 1)[1].lower()

        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid file '{filename}'. "
                    "Only .tif and .tiff files are supported."
                )
            )

        file_information.append(
            {
                "filename": filename,
                "content_type": uploaded_file.content_type,
            }
        )

    # ---------------------------------------------------------
    # 4. Current test response
    #
    # This confirms that FastAPI correctly receives:
    #     - real uploaded files
    #     - the user's query
    #
    # EarthDial + OmniRoute integration will be connected
    # after the upload schema is verified.
    # ---------------------------------------------------------

    return {
        "success": True,
        "answer": "Files received successfully.",
        "geojson": None,
        "confidence": None,
        "execution_trace": [
            "Files received by FastAPI",
            "File validation completed",
        ],
        "metadata": {
            "file_count": len(files),
            "files": file_information,
            "query": query,
        },
    }