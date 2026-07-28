import requests

def goi_backend_hoc_ky_hieu(duong_dan_file, trang_hien_tai):
    payload = {"file_path": duong_dan_file, "page_index": trang_hien_tai}
    try:
        response = requests.post("http://localhost:8000/api/pdf/hoc-bang-ky-hieu", json=payload)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Lỗi Server: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Sập nguồn: Đéo gọi được Backend!"

# 🚀 NÂNG CẤP ĐƯỜNG ỐNG: Phải có đủ biến vung_chon=None ở dòng dưới
def goi_backend_boc_tach(duong_dan_file, trang_hien_tai, mode, chu_ky_da_hoc=None, vung_chon=None):
    payload = {
        "file_path": duong_dan_file,
        "page_index": trang_hien_tai,
        "mode": mode,
        "chu_ky": chu_ky_da_hoc if chu_ky_da_hoc else {},
        "vung_chon": vung_chon if vung_chon else [] # Bơm vào hàng hóa
    }
    try:
        response = requests.post("http://localhost:8000/api/pdf/dem-vat-the", json=payload)
        if response.status_code == 200:
            return True, response.json() 
        return False, f"Lỗi Server: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Sập nguồn: Đéo gọi được Backend!"