import fitz
import re

# ==========================================
# 🧠 BƯỚC 1: HÀM MÒ BẢNG CHÚ THÍCH BẰNG TIA LASER NGANG
# ==========================================
def hoc_bang_ky_hieu(duong_dan_pdf, trang_so):
    try:
        doc = fitz.open(duong_dan_pdf)
        page = doc.load_page(trang_so)
        
        words = page.get_text("words")
        drawings = page.get_drawings()
        
        mau_ma_hieu = r'^((?=.*[a-zA-Z])(?=.*[\d\-_])[a-zA-Z0-9\-_]{2,20})$'
        danh_sach_chu = []
        
        for w in words:
            text = w[4].strip(".,;:{}[ ]\n\r")
            match = re.match(mau_ma_hieu, text)
            if match:
                danh_sach_chu.append({
                    "ma": match.group(1).upper(), 
                    "box": fitz.Rect(w[0], w[1], w[2], w[3])
                })
        
        if not danh_sach_chu:
            return {"thanh_cong": False, "error": "Đéo tìm thấy cái mã nào trên trang này!"}

        chu_ky_thu_duoc = {}
        
        for chu in danh_sach_chu:
            ma = chu["ma"]
            b_chu = chu["box"]
            
            # Tia laser rộng 150 points sang 2 bên
            tia_laser = fitz.Rect(b_chu.x0 - 150, b_chu.y0 - 5, b_chu.x1 + 150, b_chu.y1 + 5)
            
            cac_net_ve_bat_duoc = []
            for d in drawings:
                rect_net = d["rect"]
                if rect_net.intersects(tia_laser) and not rect_net.intersects(b_chu):
                    if 2 < rect_net.width < 80 and 2 < rect_net.height < 80:
                        cac_net_ve_bat_duoc.append(rect_net)
            
            if cac_net_ve_bat_duoc:
                bbox_tong = cac_net_ve_bat_duoc[0]
                for r in cac_net_ve_bat_duoc[1:]:
                    bbox_tong = bbox_tong | r 
                
                chu_ky_thu_duoc[ma] = {
                    "w": round(bbox_tong.width, 1),
                    "h": round(bbox_tong.height, 1)
                }
                
        return {"thanh_cong": True, "data": chu_ky_thu_duoc}
        
    except Exception as e:
        return {"thanh_cong": False, "error": str(e)}


# ==========================================
# 🚀 BƯỚC 2: CODE ĐẾM TEXT SIÊU TỐC (MẮT THẦN NHÌN XUYÊN LỀ)
# ==========================================
def dem_ky_hieu_text(duong_dan_pdf, trang_so, vung_chon=None):
    try:
        import fitz
        import re
        doc = fitz.open(duong_dan_pdf)
        page = doc.load_page(trang_so)
        
        # 🚀 BÍ THUẬT MỞ MẮT THẦN: Ép máy quét toàn bộ khổ giấy vật lý (MediaBox), 
        # Bất chấp thợ CAD để lề (CropBox) ra sao, chữ lém ra ngoài bắt sạch 100%!
        page.set_cropbox(page.mediabox)
        words = page.get_text("words")
        
        # Xử lý Vùng Chọn (Nếu sếp có khoanh vùng)
        khung_chon = None
        if isinstance(vung_chon, list) and len(vung_chon) == 4:
            dx, dy = page.rect.x0, page.rect.y0
            khung_chon = fitz.Rect(
                vung_chon[0] + dx - 15, 
                vung_chon[1] + dy - 15, 
                vung_chon[2] + dx + 15, 
                vung_chon[3] + dy + 15
            )
        
        mau_tim_kiem = r'^((?=.*[a-zA-Z])[a-zA-Z0-9\-_]{2,20}(?:\((?![xX]\d)[a-zA-Z0-9\-_]+\))?)(?:\([xX](\d+)\))?$'
        ket_qua = {}
        
        for w in words:
            x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
            rect_chu = fitz.Rect(x0, y0, x1, y1)
            
            if khung_chon:
                if not khung_chon.intersects(rect_chu):
                    continue
            
            text = w[4].strip(".,;:{}[ ]").replace(" ", "")
            match = re.match(mau_tim_kiem, text)
            if match:
                ma_goc = match.group(1).upper() 
                he_so_nhan = int(match.group(2)) if match.group(2) else 1
                
                if ma_goc not in ket_qua:
                    ket_qua[ma_goc] = {"so_luong": 0, "toa_do": []}
                
                ket_qua[ma_goc]["so_luong"] += he_so_nhan
                ket_qua[ma_goc]["toa_do"].append([x0, y0, x1, y1])
                
        return ket_qua
    except Exception as e:
        # Báo lỗi rõ ràng cho Front-end biết
        return {"error": f"Lỗi Backend: {str(e)}"}
