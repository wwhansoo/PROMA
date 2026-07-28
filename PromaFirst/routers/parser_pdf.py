from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict # 🚀 GỌI THÊM BỘ BÙA CHỐNG LỖI CÚ PHÁP
from core.pdf_counter import dem_ky_hieu_text, hoc_bang_ky_hieu

router = APIRouter()

class YeuCauBocTach(BaseModel):
    file_path: str
    page_index: int
    mode: str
    chu_ky: Optional[Dict] = {}
    vung_chon: Optional[List] = [] # 🚀 Sửa thành rỗng mặc định để chống sập!

class YeuCauHocBang(BaseModel):
    file_path: str
    page_index: int

@router.post("/hoc-bang-ky-hieu")
def api_hoc_bang_ky_hieu(yeu_cau: YeuCauHocBang):
    ket_qua = hoc_bang_ky_hieu(yeu_cau.file_path, yeu_cau.page_index)
    if ket_qua.get("thanh_cong"): return ket_qua
    return {"thanh_cong": False, "error": ket_qua.get("error")}

@router.post("/dem-vat-the")
def api_dem_vat_the(yeu_cau: YeuCauBocTach):
    ket_qua = dem_ky_hieu_text(yeu_cau.file_path, yeu_cau.page_index, yeu_cau.vung_chon)
    return {
        "status": "success",
        "thong_diep": f"Đã quét xong trang {yeu_cau.page_index}",
        "data": ket_qua
    }