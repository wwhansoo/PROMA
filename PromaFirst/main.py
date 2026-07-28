from fastapi import FastAPI
from routers import parser_pdf

app = FastAPI(title="PROMA Backend Engine")

# Cắm cái ống nước "pdf" vào tổng đài
app.include_router(parser_pdf.router, prefix="/api/pdf", tags=["Bóc Tách PDF"])