from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from app.database import get_session
from app.models import Document
from app.dependencies import get_current_user
from app.services.document import extract_text_from_pdf, extract_text_from_txt

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files allowed")

    file_bytes = await file.read()

    if file.filename.endswith(".pdf"):
        content = extract_text_from_pdf(file_bytes)
    else:
        content = extract_text_from_txt(file_bytes)

    if not content.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        content=content
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "characters": len(content)
    }

@router.get("/")
def get_documents(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    documents = session.exec(
        select(Document).where(Document.user_id == current_user.id)
    ).all()
    return documents