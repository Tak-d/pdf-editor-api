from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.auth import verify_api_key
from app.config import settings
from app.pdf_editor import merge_pdfs, rotate_pdf, split_pdf

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@app.head("/")
def root():
    return {"name": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/v1/merge")
@limiter.limit("30/minute")
async def merge(
    request: Request,
    files: list[UploadFile] = File(...),
    _: str = Depends(verify_api_key),
):
    pdf_list = [await f.read() for f in files]
    result = merge_pdfs(pdf_list)
    return Response(
        content=result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )


@app.post("/v1/split")
@limiter.limit("30/minute")
async def split(
    request: Request,
    file: UploadFile = File(...),
    pages: str = Form(...),
    _: str = Depends(verify_api_key),
):
    pdf_bytes = await file.read()
    result = split_pdf(pdf_bytes, pages)
    return Response(
        content=result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=split.pdf"},
    )


@app.post("/v1/rotate")
@limiter.limit("30/minute")
async def rotate(
    request: Request,
    file: UploadFile = File(...),
    angle: int = Form(...),
    pages: str = Form("all"),
    _: str = Depends(verify_api_key),
):
    pdf_bytes = await file.read()
    result = rotate_pdf(pdf_bytes, angle, pages)
    return Response(
        content=result,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rotated.pdf"},
    )