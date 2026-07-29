import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter.filedialog as fd
from tkinter.colorchooser import askcolor 
import fitz  # PyMuPDF
import os
import sys  
import time
import threading

# ==========================================
# 🚀 BÙA MỞ ĐƯỜNG
# ==========================================
THU_MUC_HIEN_TAI = os.path.dirname(os.path.abspath(__file__)) 
THU_MUC_GOC = os.path.dirname(os.path.dirname(THU_MUC_HIEN_TAI)) 

if THU_MUC_GOC not in sys.path:
    sys.path.append(THU_MUC_GOC)

# ==========================================
# CẤU HÌNH PALETTE MÀU TỐI GIẢN
# ==========================================
ctk.set_appearance_mode("dark")
BG_DARK = "#120C08"       # Nền tối sâu hơn
PANEL_BG = "#1E150F"      # Panel xám đen
ACCENT_MAIN = "#B07D4C"   
ACCENT_HOVER = "#C49A6C"  
TEXT_MAIN = "#F5F5DC"     
TEXT_MUTED = "#8A7969"    
GRID_COLOR = "#33261D"    

TAB_ACTIVE = PANEL_BG     
TAB_INACTIVE = "#100B07"  
TAB_HOVER = "#241810"     
CLOSE_BTN_HOVER = "#B3543E" 

class PromaEnterpriseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PROMA // Takeoff Workspace (VIE)")
        self.geometry("1400x850")
        self.configure(fg_color=BG_DARK)

        self.tabs = {}
        self.active_tab_name = None
        self.last_mouse_update = 0
        self.zoom_timer = None

        self.danh_sach_mau = [
            "#E63946", "#F4A261", "#2A9D8F", "#E9C46A", "#9B5DE5", 
            "#00F5D4", "#F15BB5", "#00BBF9", "#FEE440", "#F94144",
            "#F3722C", "#F8961E", "#43AA8B", "#577590", "#277DA1",
            "#9D4EDD", "#FF99C8", "#38B000", "#7209B7", "#FF006E"
        ]
        self.mau_index = 0

        self.show_splash_screen()

    # ==========================================
    # KHU VỰC 1: SPLASH SCREEN
    # ==========================================
    def show_splash_screen(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.splash_frame.pack(fill="both", expand=True)

        thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
        thu_muc_client = os.path.dirname(thu_muc_hien_tai)
        logo_filename = os.path.join(thu_muc_client, "assets", "Proma Logo 1.png")

        try:
            img_goc = Image.open(logo_filename)
            w_goc, h_goc = img_goc.size
            anh_logo = ctk.CTkImage(light_image=img_goc, dark_image=img_goc, size=(int(w_goc*(200/h_goc)), 200))
            ctk.CTkLabel(self.splash_frame, text="", image=anh_logo).pack(pady=(220, 10))
        except FileNotFoundError:
            ctk.CTkLabel(self.splash_frame, text="[ LOGO PROMA ]", font=("Arial", 45, "bold"), text_color=ACCENT_MAIN).pack(pady=(220, 10))

        ctk.CTkLabel(self.splash_frame, text="Proma.", font=("EB Garamond ExtraBold", 75, "bold"), text_color=TEXT_MAIN).pack(pady=(10, 5))
        ctk.CTkLabel(self.splash_frame, text="Ready to break ground!", font=("EB Garamond", 30), text_color=TEXT_MUTED).pack(pady=(0, 40))

        ctk.CTkButton(
            self.splash_frame, text="TẢI BẢN VẼ (LOAD PDF)", height=55, width=280, 
            corner_radius=8, font=("Arial", 16, "bold"),
            fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, text_color=BG_DARK,
            command=self.open_first_pdf
        ).pack()

    def open_first_pdf(self):
        filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
        if not filepath: return
        self.splash_frame.pack_forget()
        self.build_workspace()
        self.add_new_tab(filepath)

    def open_additional_pdf(self):
        filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
        if filepath: self.add_new_tab(filepath)

    # ==========================================
    # KHU VỰC 2: WORKSPACE (ĐÃ TRẢM SIDEBAR)
    # ==========================================
    def build_workspace(self):
        # 🚀 KIẾN TRÚC LƯỚI MỚI (CHỈ CÒN 2 CỘT CHÍNH: BẢN VẼ VÀ ĐỘNG CƠ)
        self.grid_rowconfigure(0, weight=0) # Dành đất cho Top Ribbon
        self.grid_rowconfigure(1, weight=1) # Dành đất cho Không gian làm việc
        self.grid_columnconfigure(0, weight=1) # Cột Bản vẽ
        self.grid_columnconfigure(1, weight=0) # Cột Menu phải

        # ==========================================
        # 🚀 TOP TOOLBAR - MACBOOK TOUCH BAR STYLE
        # ==========================================
        self.top_toolbar = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=BG_DARK)
        self.top_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_toolbar.pack_propagate(False) 

        # --- [TRÁI] LOGO & NÚT CƠ BẢN ---
        self.toolbar_left = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_left.pack(side="left", fill="y", padx=(20, 10))

        ctk.CTkLabel(self.toolbar_left, text="P.", font=("Arial", 28, "bold"), text_color=ACCENT_MAIN).pack(side="left", padx=(0, 15))

        ctk.CTkButton(self.toolbar_left, text="📂 OPEN", width=70, height=32, corner_radius=6, fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color="#2E2018", font=("Arial", 12, "bold"), command=self.open_additional_pdf).pack(side="left", padx=5)
        ctk.CTkButton(self.toolbar_left, text="💾 EXPORT", width=70, height=32, corner_radius=6, fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color="#2E2018", font=("Arial", 12, "bold"), command=self.export_markup_pdf).pack(side="left", padx=5)
        
        # Nút INSERT (Gắn bùa bật tắt Touch Bar)
        self.btn_insert = ctk.CTkButton(self.toolbar_left, text="✚ INSERT", width=80, height=32, corner_radius=6, fg_color=ACCENT_MAIN, text_color=BG_DARK, hover_color=ACCENT_HOVER, font=("Arial", 12, "bold"), command=self.toggle_touchbar_insert)
        self.btn_insert.pack(side="left", padx=5)

        # --- [GIỮA] TOUCH BAR DYNAMIC SCREEN ---
        self.touch_bar = ctk.CTkFrame(self.top_toolbar, height=36, corner_radius=8, fg_color=PANEL_BG, border_width=1, border_color="#2C2C2E")
        self.touch_bar.pack(side="left", fill="both", expand=True, padx=10, pady=7)
        self.touch_bar.pack_propagate(False)

        # --- [PHẢI] XOAY TRANG & CHUYỂN TRANG ---
        self.toolbar_right = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_right.pack(side="right", fill="y", padx=(10, 20))

        # Nút Xoay Trang ngạo nghễ
        ctk.CTkButton(self.toolbar_right, text="⟳ XOAY", width=60, height=32, corner_radius=6, fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color="#3A3A3C", font=("Arial", 12, "bold"), command=self.rotate_page).pack(side="left", padx=(0, 15))

        # Cụm chuyển trang siêu tinh gọn
        self.nav_frame = ctk.CTkFrame(self.toolbar_right, fg_color="transparent")
        self.nav_frame.pack(side="left", pady=9)
        ctk.CTkButton(self.nav_frame, text="❮", width=28, height=28, corner_radius=6, fg_color="transparent", text_color=TEXT_MUTED, hover_color="#3A3A3C", font=("Arial", 14, "bold"), command=self.prev_page).pack(side="left", padx=2)
        
        self.lbl_page = ctk.CTkLabel(self.nav_frame, text="00 / 00", font=("Consolas", 13, "bold"), text_color=TEXT_MAIN)
        self.lbl_page.pack(side="left", padx=8)
        
        ctk.CTkButton(self.nav_frame, text="❯", width=28, height=28, corner_radius=6, fg_color="transparent", text_color=TEXT_MUTED, hover_color="#3A3A3C", font=("Arial", 14, "bold"), command=self.next_page).pack(side="left", padx=2)

        # Kẻ vạch mờ ranh giới
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=PANEL_BG).grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- CENTER AREA (Không gian bản vẽ đã rộng tối đa) ---
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")

        # --- CENTER AREA (Không gian bản vẽ đã rộng tối đa) ---
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.center_frame.pack_propagate(False)

        # Tab bar (Bám sát lên trên cùng)
        self.custom_tab_bar = ctk.CTkScrollableFrame(self.center_frame, height=45, orientation="horizontal", fg_color="transparent", bg_color="transparent")
        self.custom_tab_bar.pack(side="top", fill="x", pady=(0, 5))
        self.custom_tab_bar._scrollbar.configure(width=0) 

        # Khung Canvas
        self.canvas_area = ctk.CTkFrame(self.center_frame, corner_radius=12, fg_color=BG_DARK)
        self.canvas_area.pack(side="top", fill="both", expand=True)

        # --- RIGHT PANEL ---
        self.right_panel = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=PANEL_BG)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_propagate(False)

        ctk.CTkLabel(self.right_panel, text="ENGINE CONTROL", font=("Arial", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(20, 10))

        self.mode_var = ctk.StringVar(value="Vật thể")
        self.mode_selector = ctk.CTkSegmentedButton(self.right_panel, values=["Vật thể", "Đường ống", "Diện tích"], variable=self.mode_var, selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, text_color=TEXT_MAIN)
        self.mode_selector.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.right_panel, text="PHẠM VI BÓC TÁCH", font=("Arial", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 5))
        self.area_mode_var = ctk.StringVar(value="Toàn bản vẽ")
        # 🚀 GẮN THÊM COMMAND DỌN DẸP VÀO NÚT BẤM
        self.area_selector = ctk.CTkSegmentedButton(
            self.right_panel, values=["Toàn bản vẽ", "Kéo chọn vùng"], variable=self.area_mode_var,
            selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, text_color=TEXT_MAIN
        )
        self.area_selector.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_learn_legend = ctk.CTkButton(
            self.right_panel, text="📖 ĐỌC BẢNG KÝ HIỆU (TRAIN)", height=40, corner_radius=6, 
            font=("Arial", 13, "bold"), fg_color=PANEL_BG, hover_color=BG_DARK, text_color=ACCENT_MAIN,
            border_width=1, border_color=ACCENT_MAIN,
            command=self.train_legend_action
        )
        self.btn_learn_legend.pack(fill="x", padx=20, pady=(5, 5))

        self.btn_run = ctk.CTkButton(self.right_panel, text="KÍCH HOẠT BÓC TÁCH", height=50, corner_radius=8, font=("Arial", 15, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, text_color=BG_DARK, command=self.run_engine)
        self.btn_run.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(self.right_panel, text="LAYER MANAGER", font=("Arial", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.master_switch_var = ctk.BooleanVar(value=True)
        self.master_switch = ctk.CTkSwitch(self.right_panel, text="BẬT / TẮT TẤT CẢ", font=("Arial", 12, "bold"), text_color=ACCENT_MAIN, progress_color=ACCENT_MAIN, variable=self.master_switch_var, command=self.toggle_all_layers)
        self.master_switch.pack(anchor="w", padx=20, pady=(0, 10))

        self.layer_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color=BG_DARK, height=360, corner_radius=8)
        self.layer_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(self.right_panel, text="TERMINAL LOG", font=("Arial", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 5))
        self.txt_log = ctk.CTkTextbox(self.right_panel, fg_color=BG_DARK, text_color=TEXT_MAIN, font=("Consolas", 12), corner_radius=8, height=120)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.txt_log.configure(state="disabled")

        self.txt_log._textbox.tag_configure("sys", foreground=TEXT_MUTED)
        self.txt_log._textbox.tag_configure("success", foreground="#D5B07C")
        self.txt_log._textbox.tag_configure("error", foreground=CLOSE_BTN_HOVER)
        self.txt_log._textbox.tag_configure("action", foreground=ACCENT_MAIN)

        # Trả Status Bar về sát đáy dưới cùng
        self.statusbar = ctk.CTkFrame(self.center_frame, height=30, corner_radius=8, fg_color=PANEL_BG)
        self.statusbar.pack(side="bottom", fill="x")

        self.lbl_coords = ctk.CTkLabel(self.statusbar, text="X: 0.00 | Y: 0.00", font=("Consolas", 11), text_color=TEXT_MUTED)
        self.lbl_coords.pack(side="left", padx=15)

        self.lbl_zoom = ctk.CTkLabel(self.statusbar, text="Zoom: 200%", font=("Consolas", 11), text_color=TEXT_MUTED)
        self.lbl_zoom.pack(side="right", padx=15)

        self.log_to_terminal("PROMA Core Module Initialized (Ribbon UI).", "sys")

    # ==========================================
    # KHU VỰC 3: TAB MANAGER & CHỌN MÀU LAYER
    # ==========================================
    def add_layer_toggle_ui(self, ma_den, mau_sac, so_luong=0):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]

        row = ctk.CTkFrame(self.layer_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        # 🚀 CHỮA BỆNH ĐỔI MÀU: Dùng CTkButton thay vì CTkFrame để click đéo bao giờ trượt!
        color_box = ctk.CTkButton(
            row, text="", width=18, height=18, corner_radius=3, 
            fg_color=mau_sac, hover_color=mau_sac, cursor="hand2"
        )
        color_box.pack(side="left", padx=(5, 5))
        
        switch_var = ctk.BooleanVar(value=data["layer_visibility"].get(ma_den, True))
        text_hien_thi = f"{ma_den}: {so_luong}"
        switch = ctk.CTkSwitch(
            row, text=text_hien_thi, font=("Arial", 12, "bold"), 
            text_color=TEXT_MAIN, progress_color=mau_sac,
            variable=switch_var, command=lambda m=ma_den, v=switch_var: self.toggle_layer(m, v.get())
        )
        switch.pack(side="left", fill="x", expand=True)

        data["layer_switches"][ma_den] = switch

        # Nút xóa ✖
        btn_delete = ctk.CTkButton(
            row, text="✖", width=24, height=24, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color="#B3543E", font=("Arial", 14),
            command=lambda m=ma_den, r=row: self.delete_layer(m, r)
        )
        btn_delete.pack(side="right", padx=(5, 5))

        # Thanh trượt Scale
        scale_val = data.setdefault("layer_scale", {}).setdefault(ma_den, 1.0)
        slider = ctk.CTkSlider(
            row, width=70, height=12, from_=1.0, to=5.0, 
            button_color=mau_sac, progress_color=mau_sac,
            command=lambda v, m=ma_den: self.change_layer_scale(m, v)
        )
        slider.set(scale_val)
        slider.pack(side="right", padx=(5, 0))

        # 🚀 GẮN LỆNH ĐỔI MÀU TRỰC TIẾP VÀO NÚT (ĐÉO DÙNG BIND NỮA)
        color_box.configure(command=lambda m=ma_den, cb=color_box, sw=switch, sl=slider: self.change_layer_color(m, cb, sw, sl))

        # 🚀 GẮN BÙA DOUBLE-CLICK VÀO CHỮ TRÊN CÔNG TẮC ĐỂ RENAME LAYER
        # Thằng CustomTkinter giấu Widget chữ ở biến _text_label bên trong
        switch._text_label.bind("<Double-Button-1>", lambda e, m=ma_den: self.rename_layer_action(m))
        switch._text_label.configure(cursor="xterm") # Đổi con trỏ chuột thành hình chữ I cho người ta biết là sửa được

    # Nâng cấp hàm đổi màu để đổi luôn màu của thanh trượt
    def change_layer_color(self, ma_den, color_box, switch, slider=None):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        mau_hien_tai = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
        _, hex_color = askcolor(title=f"Đổi màu cho mã {ma_den}", initialcolor=mau_hien_tai)
        
        if hex_color: 
            data["bang_mau_vat_the"][ma_den] = hex_color
            color_box.configure(fg_color=hex_color)
            switch.configure(progress_color=hex_color)
            if slider:
                slider.configure(button_color=hex_color, progress_color=hex_color)
            self.log_to_terminal(f"Đã đổi màu mã {ma_den} sang {hex_color}", "sys")
            self.render_page(self.active_tab_name, redraw_pdf=False)

    # 🚀 HÀM XỬ LÝ KHI KÉO THANH TRƯỢT
    def change_layer_scale(self, ma_den, value):
        if not self.active_tab_name: return
        self.tabs[self.active_tab_name]["layer_scale"][ma_den] = value
        
        # Debounce: Cản lại không cho nó vẽ liên tục gây lag khi đang miết chuột
        if hasattr(self, 'scale_timer') and self.scale_timer:
            self.after_cancel(self.scale_timer)
        self.scale_timer = self.after(50, lambda: self.render_page(self.active_tab_name, redraw_pdf=False))

    def change_layer_color(self, ma_den, color_box, switch):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        mau_hien_tai = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
        _, hex_color = askcolor(title=f"Đổi màu cho mã {ma_den}", initialcolor=mau_hien_tai)
        
        if hex_color: 
            data["bang_mau_vat_the"][ma_den] = hex_color
            color_box.configure(fg_color=hex_color)
            switch.configure(progress_color=hex_color)
            self.log_to_terminal(f"Đã đổi màu mã {ma_den} sang {hex_color}", "sys")
            self.render_page(self.active_tab_name, redraw_pdf=False)

    def toggle_layer(self, ma_den, is_visible):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        data["layer_visibility"][ma_den] = is_visible
        self.render_page(self.active_tab_name, redraw_pdf=False)

    def toggle_all_layers(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        trang_thai_tong = self.master_switch_var.get() 
        for ma_den in data["layer_visibility"].keys():
            data["layer_visibility"][ma_den] = trang_thai_tong
            if ma_den in data["layer_switches"]:
                if trang_thai_tong: data["layer_switches"][ma_den].select()
                else: data["layer_switches"][ma_den].deselect()
        self.render_page(self.active_tab_name, redraw_pdf=False)
    # 🚀 HÀM MỚI: PHI TANG KÝ HIỆU RÁC KHỎI BỘ NHỚ VÀ BẢN VẼ
    def delete_layer(self, ma_den, row_widget):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # 1. Xóa sạch mọi thứ liên quan trong bộ nhớ não
        if ma_den in data["bang_mau_vat_the"]: del data["bang_mau_vat_the"][ma_den]
        if ma_den in data["layer_visibility"]: del data["layer_visibility"][ma_den]
        if ma_den in data["layer_switches"]: del data["layer_switches"][ma_den]
        if ma_den in data["layer_scale"]: del data["layer_scale"][ma_den]
        
        # Xóa tọa độ đóng dấu trên trang hiện tại
        trang_idx = data["current_page"]
        if trang_idx in data.get("markers", {}) and ma_den in data["markers"][trang_idx]:
            del data["markers"][trang_idx][ma_den]
            
        # 2. Hủy thi thể trên giao diện danh sách
        row_widget.destroy()
        
        # 3. Quét lại bản vẽ (Mất tích luôn trên màn hình)
        self.render_page(self.active_tab_name, redraw_pdf=False)
        self.log_to_terminal(f"Đã phi tang toàn bộ mã '{ma_den}' khỏi bản vẽ!", "error")
    
    # ==========================================
    # 🚀 HÀM MỚI: DOUBLE CLICK ĐỂ RENAME LAYER
    # ==========================================
    def rename_layer_action(self, ma_cu):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # 1. Bật cửa sổ hỏi Tên mới
        dialog = ctk.CTkInputDialog(text=f"Đổi tên cho Layer [{ma_cu}]:", title="Rename Layer")
        ma_moi = dialog.get_input()
        
        if not ma_moi or ma_moi.strip() == "" or ma_moi.upper().strip() == ma_cu:
            return # Hủy nếu bấm Cancel hoặc để trống hoặc gõ lại tên cũ
            
        ma_moi = ma_moi.upper().strip()
        
        # 2. Chặn lỗi trùng tên
        if ma_moi in data["bang_mau_vat_the"]:
            self.log_to_terminal(f"LỖI: Tên '{ma_moi}' đã tồn tại trên bản vẽ rồi sếp ơi!", "error")
            return

        # 3. CHUYỂN GIAO TÀI SẢN TRONG NÃO AI (Màu, Trạng thái, Scale)
        data["bang_mau_vat_the"][ma_moi] = data["bang_mau_vat_the"].pop(ma_cu)
        data["layer_visibility"][ma_moi] = data["layer_visibility"].pop(ma_cu)
        if ma_cu in data["layer_scale"]:
            data["layer_scale"][ma_moi] = data["layer_scale"].pop(ma_cu)

        # 4. CHUYỂN GIAO TỌA ĐỘ TRÊN TẤT CẢ CÁC TRANG PDF
        for trang_idx, markers_trang in data.get("markers", {}).items():
            if ma_cu in markers_trang:
                markers_trang[ma_moi] = markers_trang.pop(ma_cu)

        # 5. Xây lại danh sách UI cho chuẩn tên mới
        self.log_to_terminal(f"Đã rename Layer: [{ma_cu}] -> [{ma_moi}]", "success")
        
        # Refresh lại toàn bộ Layer Manager và Canvas
        for child in self.layer_frame.winfo_children(): child.destroy()
        data["layer_switches"] = {}
        
        trang_hien_tai = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_hien_tai, {})
        
        for ma_den in sorted(data["bang_mau_vat_the"].keys()):
            mau_sac = data["bang_mau_vat_the"][ma_den]
            so_l = markers_trang_nay.get(ma_den, {}).get("so_luong", 0)
            self.add_layer_toggle_ui(ma_den, mau_sac, so_l)
            
        self.render_page(self.active_tab_name, redraw_pdf=False)

    def update_layer_manager_counts(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        for ma_den, switch in data["layer_switches"].items():
            switch.configure(text=f"{ma_den}: 0")
            
        for ma_den, thong_tin in markers_trang_nay.items():
            if ma_den in data["layer_switches"]:
                switch = data["layer_switches"][ma_den]
                switch.configure(text=f"{ma_den}: {thong_tin['so_luong']}")

    def add_new_tab(self, filepath):
        base_name = os.path.basename(filepath)
        tab_name = base_name
        
        count = 1
        while tab_name in self.tabs:
            tab_name = f"{base_name} ({count})"
            count += 1

        tab_ui = ctk.CTkFrame(self.custom_tab_bar, fg_color=TAB_ACTIVE, corner_radius=8)
        tab_ui.pack(side="left", padx=(0, 5), pady=2, fill="y") 

        lbl_name = ctk.CTkLabel(tab_ui, text=tab_name, font=("Arial", 12, "bold"), text_color=TEXT_MAIN)
        lbl_name.pack(side="left", padx=(15, 8), pady=5)
        
        btn_close = ctk.CTkButton(
            tab_ui, text="✖", width=24, height=24, corner_radius=6,
            fg_color="transparent", hover_color=CLOSE_BTN_HOVER, text_color=TEXT_MUTED, font=("Arial", 12),
            command=lambda name=tab_name: self.close_specific_tab(name)
        )
        btn_close.pack(side="right", padx=(0, 6), pady=5)

        tab_ui.bind("<Button-1>", lambda e, name=tab_name: self.switch_to_tab(name))
        lbl_name.bind("<Button-1>", lambda e, name=tab_name: self.switch_to_tab(name))

        canvas_container = ctk.CTkFrame(self.canvas_area, fg_color=BG_DARK, corner_radius=0)
        canvas = ctk.CTkCanvas(canvas_container, bg=BG_DARK, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=2, pady=2)

        canvas.bind("<Configure>", lambda e, c=canvas: self.draw_background_grid(e, c))
        canvas.bind("<ButtonPress-1>", self.on_drag_start)
        canvas.bind("<B1-Motion>", self.on_drag_motion)
        canvas.bind("<ButtonRelease-1>", self.on_drag_release)
        canvas.bind("<ButtonPress-2>", self.on_middle_drag_start)
        canvas.bind("<B2-Motion>", self.on_middle_drag_motion)
        canvas.bind("<ButtonRelease-2>", self.on_middle_drag_release)
        canvas.bind("<Button-3>", self.on_right_click)
        canvas.bind("<MouseWheel>", self.on_zoom)
        canvas.bind("<Motion>", self.track_mouse)

        self.tabs[tab_name] = {
            "pdf_doc": fitz.open(filepath),
            "current_page": 0,
            "zoom_level": 2.0,
            "drag_data": {"x": 0, "y": 0},
            "img_pos": [50, 50],
            "markers": {},  
            "bang_mau_vat_the": {},    
            "layer_visibility": {},    
            "layer_switches": {},
            "layer_scale": {},      
            "canvas": canvas,
            "canvas_container": canvas_container,
            "tab_ui": tab_ui,
            "lbl_name": lbl_name,
            "current_img": None
        }

        self.log_to_terminal(f"Opened layer: {tab_name}", "action")
        self.switch_to_tab(tab_name)

    def switch_to_tab(self, target_name):
        if target_name not in self.tabs: return
        self.active_tab_name = target_name

        for child in self.layer_frame.winfo_children():
            child.destroy()

        data = self.tabs[target_name]
        data["layer_switches"] = {} 
        self.master_switch_var.set(True)

        trang_idx = data["current_page"]
        markers_trang_nay = data["markers"].get(trang_idx, {})

        for name, tab_data in self.tabs.items():
            if name == target_name:
                tab_data["tab_ui"].configure(fg_color=TAB_ACTIVE)
                tab_data["lbl_name"].configure(text_color=TEXT_MAIN)
                tab_data["canvas_container"].pack(fill="both", expand=True)
                
                # Cập nhật Text
                self.lbl_page.configure(text=f"{tab_data['current_page'] + 1:02d} / {tab_data['pdf_doc'].page_count:02d}")
                self.lbl_zoom.configure(text=f"Zoom: {int(tab_data['zoom_level'] * 100)}%")
                
                for ma_den in sorted(tab_data["bang_mau_vat_the"].keys()):
                    mau_sac = tab_data["bang_mau_vat_the"][ma_den]
                    so_l = markers_trang_nay.get(ma_den, {}).get("so_luong", 0)
                    self.add_layer_toggle_ui(ma_den, mau_sac, so_l)

                self.render_page(name)
            else:
                # 🚀 LỆNH THẦN THÁNH BỊ XÓA NHẦM NAY ĐÃ TRỞ LẠI!
                # Ẩn sạch các tab không dùng tới để không bị đè hình, kẹt trang!
                tab_data["tab_ui"].configure(fg_color=TAB_INACTIVE)
                tab_data["lbl_name"].configure(text_color=TEXT_MUTED)
                tab_data["canvas_container"].pack_forget()

    def close_specific_tab(self, tab_name):
        if tab_name not in self.tabs: return

        data = self.tabs[tab_name]
        try: data["pdf_doc"].close()
        except: pass

        data["tab_ui"].destroy()
        data["canvas_container"].destroy()
        del self.tabs[tab_name]
        self.log_to_terminal(f"Closed layer: {tab_name}", "error")

        if not self.tabs:
            self.active_tab_name = None
            self.lbl_page.configure(text="00 / 00")
            self.lbl_zoom.configure(text="Zoom: 200%")
            
            for child in self.layer_frame.winfo_children(): child.destroy()

    def render_page(self, tab_name, redraw_pdf=True):
        data = self.tabs.get(tab_name)
        if not data: return

        canvas = data["canvas"]
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]

        if redraw_pdf:
            page = data["pdf_doc"].load_page(data["current_page"])
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            data["current_img"] = ImageTk.PhotoImage(img) 
            
            canvas.delete("pdf_background")
            canvas.create_image(pos_x, pos_y, anchor="nw", image=data["current_img"], tags=("pdf_img", "pdf_background"))
            self.update_layer_manager_counts()

        canvas.delete("marker") 
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        for ma_den, thong_tin in markers_trang_nay.items():
            if not data["layer_visibility"].get(ma_den, True): continue
                
            mau_sac = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
            scale = data.get("layer_scale", {}).get(ma_den, 1.0) 
            
            for box in thong_tin["toa_do"]:
                x0 = pos_x + box[0] * zoom
                y0 = pos_y + box[1] * zoom
                x1 = pos_x + box[2] * zoom
                y1 = pos_y + box[3] * zoom
                
                # 🚀 THUẬT TOÁN TÂM ĐIỂM TUYỆT ĐỐI (TRỊ BỆNH TÔ KHOẢNG TRỐNG)
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                
                # Ép cứng 1 cái ô vuông 15 points (nhân với zoom để nhìn trên màn hình)
                canh_vuong = 15.0 * zoom * scale
                
                # Bành trướng đều ra 4 hướng từ Tâm
                x0_moi = cx - canh_vuong / 2
                y0_moi = cy - canh_vuong / 2
                x1_moi = cx + canh_vuong / 2
                y1_moi = cy + canh_vuong / 2
                
                canvas.create_rectangle(x0_moi, y0_moi, x1_moi, y1_moi, outline=mau_sac, width=3, tags=("pdf_img", "marker"))
    # ==========================================
    # KHU VỰC 4: TƯƠNG TÁC CHUỘT
    # ==========================================
    def draw_background_grid(self, event, canvas):
        canvas.delete("grid")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        step = 50
        for i in range(0, w, step): canvas.create_line([(i, 0), (i, h)], fill=GRID_COLOR, tags="grid", dash=(2, 2))
        for i in range(0, h, step): canvas.create_line([(0, i), (w, i)], fill=GRID_COLOR, tags="grid", dash=(2, 2))
        canvas.tag_lower("grid")

    def track_mouse(self, event):
        now = time.time()
        if not hasattr(self, 'last_mouse_update'): self.last_mouse_update = 0
        if now - self.last_mouse_update > 0.05:
            self.lbl_coords.configure(text=f"X: {event.x:04d} | Y: {event.y:04d}")
            self.last_mouse_update = now

    def on_drag_start(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # 🚀 ƯU TIÊN 1: CHẾ ĐỘ TẨY (ERASE MODE - CLICK TRÁI XÓA BẤT KỲ ĐIỂM NÀO)
        if getattr(self, "current_action", None) == "ERASE":
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            py = (event.y - pos_y) / zoom
            
            trang = data["current_page"]
            markers_trang_nay = data.get("markers", {}).get(trang, {})
            
            for ma_den, thong_tin in markers_trang_nay.items():
                if not data["layer_visibility"].get(ma_den, True): continue
                
                # Quét xem cú click có trúng ô vuông nào không (sai số +-8 points cho dễ bấm trúng)
                for i, box in enumerate(thong_tin["toa_do"]):
                    if (box[0] - 8) <= px <= (box[2] + 8) and (box[1] - 8) <= py <= (box[3] + 8):
                        thong_tin["toa_do"].pop(i)
                        thong_tin["so_luong"] -= 1
                        
                        self.log_to_terminal(f"🗑️ Đã dùng Tẩy xóa 1 điểm của mã [{ma_den}]!", "error")
                        self.update_layer_manager_counts()
                        self.render_page(self.active_tab_name, redraw_pdf=False)
                        return # Xóa xong 1 điểm thì dừng, không quét tiếp
            return # Đang cầm tẩy thì cấm kéo bản vẽ

        # 🚀 ƯU TIÊN 2: TÍNH NĂNG MARK (CẦM SÚNG CHẤM ĐIỂM)
        if getattr(self, "current_action", None) == "MARK":
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            py = (event.y - pos_y) / zoom

            box = [px - 10, py - 10, px + 10, py + 10]
            ma_den = self.current_mark_layer
            trang = data["current_page"]

            data["markers"][trang][ma_den]["toa_do"].append(box)
            data["markers"][trang][ma_den]["so_luong"] += 1

            self.update_layer_manager_counts()
            self.render_page(self.active_tab_name, redraw_pdf=False)
            return 

        # 🚀 ƯU TIÊN 3: CHẾ ĐỘ KÉO CHỌN VÙNG
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            data["canvas"].config(cursor="crosshair")
            data["drag_data"]["start_x"] = event.x
            data["drag_data"]["start_y"] = event.y
            if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
            data["rect_id"] = data["canvas"].create_rectangle(
                event.x, event.y, event.x, event.y, 
                outline=ACCENT_MAIN, width=2, dash=(4, 4), tags="selection_rect"
            )
            
        # 🚀 MẶC ĐỊNH: KÉO THẢ DI CHUYỂN BẢN VẼ
        else: 
            data["canvas"].config(cursor="fleur")
            data["drag_data"]["x"] = event.x
            data["drag_data"]["y"] = event.y

    def on_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # 🚀 CHẶN LỖI TELEPORT: Đang cầm súng MARK hoặc cầm TẨY ERASE thì cấm kéo bản vẽ bằng chuột trái!
        if getattr(self, "current_action", None) in ["MARK", "ERASE"]: return
        
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            start_x = data["drag_data"]["start_x"]
            start_y = data["drag_data"]["start_y"]
            data["canvas"].coords(data.get("rect_id"), start_x, start_y, event.x, event.y)
        else:
            dx, dy = event.x - data["drag_data"]["x"], event.y - data["drag_data"]["y"]
            data["canvas"].move("pdf_img", dx, dy)
            data["img_pos"][0] += dx
            data["img_pos"][1] += dy
            data["drag_data"]["x"], data["drag_data"]["y"] = event.x, event.y

    def on_drag_release(self, event):
        if not self.active_tab_name: return
        
        # 🚀 CHẶN LỖI: Cầm súng MARK hay cầm TẨY ERASE thì đéo tính toán nhả chuột trái!
        if getattr(self, "current_action", None) in ["MARK", "ERASE"]: return

        if not hasattr(self, 'area_mode_var') or self.area_mode_var.get() == "Toàn bản vẽ": return
        
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="")
        
        drag_data = data.get("drag_data", {})
        start_x = int(drag_data.get("start_x", event.x))
        start_y = int(drag_data.get("start_y", event.y))
        end_x = int(event.x)
        end_y = int(event.y)
        
        if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:
            data["vung_chon_pdf"] = None
            rect_id = data.get("rect_id")
            if rect_id: data["canvas"].delete(rect_id)
            self.log_to_terminal("Đã hủy vùng chọn.", "sys")
            return
            
        img_pos = data.get("img_pos", [0, 0])
        pos_x = float(img_pos[0])
        pos_y = float(img_pos[1])
        zoom = float(data.get("zoom_level", 1.0))
        
        px0 = (min(start_x, end_x) - pos_x) / zoom
        py0 = (min(start_y, end_y) - pos_y) / zoom
        px1 = (max(start_x, end_x) - pos_x) / zoom
        py1 = (max(start_y, end_y) - pos_y) / zoom
        
        data["vung_chon_pdf"] = [px0, py0, px1, py1]
        self.log_to_terminal(f"🎯 Đã khoanh vùng mục tiêu! Bấm Kích Hoạt để đếm.", "success")
        
    # ==========================================
    # 🚀 TÍNH NĂNG CHUỘT GIỮA (PAN BẢN VẼ NHƯ AUTOCAD)
    # ==========================================
    def on_middle_drag_start(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="fleur") # Biến thành bàn tay 4 hướng
        data["drag_data"]["mid_x"] = event.x
        data["drag_data"]["mid_y"] = event.y

    def on_middle_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        dx, dy = event.x - data["drag_data"]["mid_x"], event.y - data["drag_data"]["mid_y"]
        data["canvas"].move("pdf_img", dx, dy)
        data["img_pos"][0] += dx
        data["img_pos"][1] += dy
        data["drag_data"]["mid_x"], data["drag_data"]["mid_y"] = event.x, event.y

    def on_middle_drag_release(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # Trả lại trỏ chuột tùy theo việc sếp đang cầm súng hay đang chọn vùng
        if getattr(self, "current_action", None) == "MARK" or (hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng"):
            data["canvas"].config(cursor="crosshair")
        else:
            data["canvas"].config(cursor="")

    # ==========================================
    # 🚀 BÚA TẨY CHUỘT PHẢI THẦN THÁNH (RIGHT-CLICK ERASER)
    # ==========================================
    def on_right_click(self, event):
        if not self.active_tab_name: return
        
        # TRƯỜNG HỢP 1: Đang cầm súng Mark -> Nhấp chuột phải là Undo điểm vừa chấm
        if getattr(self, "current_action", None) == "MARK":
            self.undo_manual_mark()
            return

        # TRƯỜNG HỢP 2: Chế độ bình thường -> Rẽ chuột phải trúng ô nào xóa vĩnh viễn ô đó!
        data = self.tabs[self.active_tab_name]
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]
        
        # Tọa độ mũi chuột trên PDF
        px = (event.x - pos_x) / zoom
        py = (event.y - pos_y) / zoom
        
        trang = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang, {})
        
        for ma_den, thong_tin in markers_trang_nay.items():
            if not data["layer_visibility"].get(ma_den, True): continue
            
            # Quét tìm xem mũi chuột phải có nằm trong ô vuông nào không (Sai số +-8 points cho dễ bấm)
            for i, box in enumerate(thong_tin["toa_do"]):
                if (box[0] - 8) <= px <= (box[2] + 8) and (box[1] - 8) <= py <= (box[3] + 8):
                    thong_tin["toa_do"].pop(i) # Chém bay ô vuông trúng đạn
                    thong_tin["so_luong"] -= 1
                    
                    self.log_to_terminal(f"🗑️ Đã xóa 1 điểm chấm của mã [{ma_den}]!", "error")
                    self.update_layer_manager_counts()
                    self.render_page(self.active_tab_name, redraw_pdf=False)
                    return # Xóa 1 điểm mỗi lần click rồi nghỉ

    def on_zoom(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        old_zoom = data["zoom_level"]
        
        if event.delta > 0: zoom_factor = 1.15
        elif event.delta < 0: zoom_factor = 1 / 1.15
        else: return

        if old_zoom * zoom_factor > 8.0 or old_zoom * zoom_factor < 0.3: return
            
        data["zoom_level"] = old_zoom * zoom_factor
        img_x, img_y = data["img_pos"]
        mx, my = event.x, event.y
        
        data["img_pos"] = [mx - (mx - img_x) * zoom_factor, my - (my - img_y) * zoom_factor]
        self.lbl_zoom.configure(text=f"Zoom: {int(data['zoom_level'] * 100)}%")

        if self.zoom_timer: self.after_cancel(self.zoom_timer)
        self.zoom_timer = self.after(150, lambda n=self.active_tab_name: self.render_page(n, redraw_pdf=True))

    def prev_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] > 0:
            data["current_page"] -= 1
            self.render_page(self.active_tab_name)
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")

    def next_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] < data["pdf_doc"].page_count - 1:
            data["current_page"] += 1
            self.render_page(self.active_tab_name)
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")

    def log_to_terminal(self, text, tag="sys"):
        self.txt_log.configure(state="normal")
        self.txt_log._textbox.insert("end", f"> {text}\n", tag)
        self.txt_log._textbox.see("end")
        self.txt_log.configure(state="disabled")

    # ==========================================
    # ==========================================
    # KHU VỰC 5: KÍCH HOẠT ĐỘNG CƠ BACKEND (PDF) CÓ KHOANH VÙNG
    # ==========================================
    def run_engine(self):
        if not self.active_tab_name:
            self.log_to_terminal("ERROR: Không có bản vẽ nào được chọn!", "error")
            return
            
        mode = self.mode_var.get()
        data_tab = self.tabs[self.active_tab_name]
        duong_dan_file = data_tab["pdf_doc"].name
        trang_hien_tai = data_tab["current_page"]
        
        self.log_to_terminal(f"Khởi chạy module [{mode}] trên layer [{self.active_tab_name}]...", "action")
        self.btn_run.configure(state="disabled", text="ĐANG BÓC TÁCH...")
        
        # 🚀 BẮT TỌA ĐỘ VÙNG CHỌN (NẾU CÓ)
        vung = None
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            vung = data_tab.get("vung_chon_pdf")
            if not vung:
                self.log_to_terminal("CẢNH BÁO: Đang ở chế độ Kéo chọn vùng nhưng sếp chưa khoanh! Máy sẽ quét toàn bản vẽ.", "sys")
        
        # Tránh lỗi mất biến não AI
        chu_ky = getattr(self, 'chu_ky_ai', {})
        
        # 🚀 GỌI LUỒNG NGẦM & Ném 5 tham số đi (duong_dan, trang, mode, chu_ky, vung)
        import threading
        threading.Thread(
            target=self._thread_run_engine, 
            args=(duong_dan_file, trang_hien_tai, mode, chu_ky, vung),
            daemon=True
        ).start()

    # 🚀 Hàm này nhận đủ 5 tham số để chốt đơn với Backend
    def _thread_run_engine(self, filepath, page_idx, mode, chu_ky, vung_chon):
        from logic.api_handler import goi_backend_boc_tach
        thanh_cong, ket_qua = goi_backend_boc_tach(filepath, page_idx, mode, chu_ky, vung_chon)
        self.after(0, self._hoan_thanh_run, thanh_cong, ket_qua)
        
    def _hoan_thanh_run(self, thanh_cong, ket_qua):
        self.btn_run.configure(state="normal", text="KÍCH HOẠT BÓC TÁCH")
        if not self.active_tab_name: return
        data_tab = self.tabs[self.active_tab_name]
        
        if thanh_cong:
            data_dem = ket_qua.get("data", {})
            if data_dem:
                self.log_to_terminal("Đã hoàn tất đếm. Đang đồng bộ tọa độ xoay...", "success")
                if "markers" not in data_tab: data_tab["markers"] = {}
                trang_hien_tai = data_tab["current_page"]
                
                # 🚀 THUẬT TOÁN ĐỒNG BỘ GÓC XOAY: Nắn tọa độ AI từ file gốc theo góc xoay hiện tại của màn hình
                page = data_tab["pdf_doc"].load_page(trang_hien_tai)
                goc_xoay = page.rotation
                
                if goc_xoay != 0:
                    w_goc = page.rect.width if goc_xoay in [0, 180] else page.rect.height
                    h_goc = page.rect.height if goc_xoay in [0, 180] else page.rect.width
                    
                    for ma_den, thong_tin in data_dem.items():
                        toa_do_da_xoay = []
                        for box in thong_tin["toa_do"]:
                            x0, y0, x1, y1 = box[0], box[1], box[2], box[3]
                            # Xoay tương ứng với góc 90, 180, 270 độ
                            if goc_xoay == 90:
                                nx0, ny0, nx1, ny1 = h_goc - y1, x0, h_goc - y0, x1
                            elif goc_xoay == 180:
                                nx0, ny0, nx1, ny1 = w_goc - x1, h_goc - y1, w_goc - x0, h_goc - y0
                            elif goc_xoay == 270:
                                nx0, ny0, nx1, ny1 = y0, w_goc - x1, y1, w_goc - x0
                            else:
                                nx0, ny0, nx1, ny1 = x0, y0, x1, y1
                            toa_do_da_xoay.append([min(nx0, nx1), min(ny0, ny1), max(nx0, nx1), max(ny0, ny1)])
                        thong_tin["toa_do"] = toa_do_da_xoay

                data_tab["markers"][trang_hien_tai] = data_dem
                
                for ma_den, thong_tin in data_dem.items():
                    if ma_den not in data_tab["bang_mau_vat_the"]:
                        mau_moi = self.danh_sach_mau[self.mau_index % len(self.danh_sach_mau)]
                        data_tab["bang_mau_vat_the"][ma_den] = mau_moi
                        self.mau_index += 1
                        data_tab["layer_visibility"][ma_den] = True
                
                self.switch_to_tab(self.active_tab_name)
            else:
                self.log_to_terminal("Không tìm thấy vật thể nào trong vùng này!", "sys")
        else:
            self.log_to_terminal(f"LỖI HỆ THỐNG: {ket_qua}", "error")

    # 🚀 KIẾN TRÚC MỚI: MỞ RỘNG TOUCH BAR KHI BẤM INSERT
    def close_touchbar(self):
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        self.current_action = None
        
    def toggle_touchbar_insert(self):
        if not self.active_tab_name:
            self.log_to_terminal("Sếp phải mở bản vẽ ra mới xài Insert được chứ!", "error")
            return
            
        self.close_touchbar()

        # Nút 1: Mark (Chấm điểm)
        btn_mark = ctk.CTkButton(
            self.touch_bar, text="Mark", width=80, height=28, corner_radius=6, 
            fg_color="#D5B07C", text_color=BG_DARK, hover_color="#C49A6C", font=("Arial", 12, "bold"), 
            command=self.start_manual_mark
        )
        btn_mark.pack(side="left", padx=(15, 5), pady=4)

        # 🚀 NÚT 2: ERASE (CẦM TẤY XÓA ĐIỂM BẤT KỲ)
        btn_erase = ctk.CTkButton(
            self.touch_bar, text="Erase", width=80, height=28, corner_radius=6, 
            fg_color="#B3543E", text_color="#FFFFFF", hover_color="#8F3C29", font=("Arial", 12, "bold"), 
            command=self.start_erase_mode
        )
        btn_erase.pack(side="left", padx=5, pady=4)

        btn_close = ctk.CTkButton(
            self.touch_bar, text="✖", width=28, height=28, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color="#B3543E", 
            command=self.close_touchbar
        )
        btn_close.pack(side="right", padx=10, pady=4)

    # ==========================================
    # 🚀 TÍNH NĂNG INSERT: MARK THỦ CÔNG & TẤY (ERASE)
    # ==========================================

    # --- 1. KÍCH HOẠT CHẤM MARK ---
    def start_manual_mark(self):
        if not self.active_tab_name: return
        
        dialog = ctk.CTkInputDialog(text="Nhập tên Ký hiệu (VD: MARK-01):", title="Tạo Layer Mark")
        layer_name = dialog.get_input()
        
        if not layer_name: 
            self.log_to_terminal("Đã hủy chấm điểm thủ công.", "sys")
            return
            
        layer_name = layer_name.upper().strip()
        data = self.tabs[self.active_tab_name]

        if layer_name not in data["bang_mau_vat_the"]:
            mau_moi = self.danh_sach_mau[self.mau_index % len(self.danh_sach_mau)]
            data["bang_mau_vat_the"][layer_name] = mau_moi
            self.mau_index += 1
            data["layer_visibility"][layer_name] = True
            
            trang_hien_tai = data["current_page"]
            if "markers" not in data: data["markers"] = {}
            if trang_hien_tai not in data["markers"]: data["markers"][trang_hien_tai] = {}
            if layer_name not in data["markers"][trang_hien_tai]:
                data["markers"][trang_hien_tai][layer_name] = {"so_luong": 0, "toa_do": []}
                
            self.add_layer_toggle_ui(layer_name, mau_moi, 0)

        self.current_action = "MARK"
        self.current_mark_layer = layer_name
        data["canvas"].config(cursor="crosshair") 

        # 🚀 DỌN SẠCH TOUCH BAR - CHỈ HIỆN ĐÚNG STATUS SIÊU GỌN
        for widget in self.touch_bar.winfo_children(): widget.destroy()

        ctk.CTkLabel(
            self.touch_bar, text=f"MARKING: [ {layer_name} ]", 
            font=("Consolas", 13, "bold"), text_color=ACCENT_MAIN
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            self.touch_bar, text="Ctrl+Z: Undo  |  Enter / ESC: Chốt sổ", 
            font=("Consolas", 11, "italic"), text_color=TEXT_MUTED
        ).pack(side="left", padx=10)

        # 🚀 TRÓI CHẶT PHÍM ENTER VÀ ESC VÀO TOÀN APP
        self.bind("<Control-z>", self.undo_manual_mark)
        self.bind("<Return>", self.finish_manual_mark)
        self.bind("<Escape>", self.finish_manual_mark)
        data["canvas"].bind("<Return>", self.finish_manual_mark)
        data["canvas"].bind("<Escape>", self.finish_manual_mark)
        
        data["canvas"].focus_set()
        self.log_to_terminal(f"Đã lên đạn mã {layer_name}. Gõ Enter hoặc ESC để thu súng!", "action")

    # --- 2. UNDO ĐIỂM CHẤM GẦN NHẤT (CTRL+Z) ---
    def undo_manual_mark(self, event=None):
        if getattr(self, "current_action", None) != "MARK": return
        data = self.tabs.get(self.active_tab_name)
        if not data: return
        
        trang = data["current_page"]
        ma_den = self.current_mark_layer
        thong_tin = data.get("markers", {}).get(trang, {}).get(ma_den)
        
        if thong_tin and len(thong_tin["toa_do"]) > 0:
            thong_tin["toa_do"].pop() 
            thong_tin["so_luong"] -= 1
            self.update_layer_manager_counts()
            self.render_page(self.active_tab_name, redraw_pdf=False)
            self.log_to_terminal(f"↩ Đã Undo 1 điểm chấm của {ma_den}.", "sys")

    # --- 3. CHỐT SỔ MARK ---
    def finish_manual_mark(self, event=None):
        self.current_action = None
        self.current_mark_layer = None
        if self.active_tab_name:
            data = self.tabs[self.active_tab_name]
            data["canvas"].config(cursor="") 
            data["canvas"].unbind("<Return>")
            data["canvas"].unbind("<Escape>")
            
        self.unbind("<Control-z>")
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self.log_to_terminal("Đã chốt sổ điểm chấm thủ công, về chuột thường!", "success")
        self.toggle_touchbar_insert()

    # --- 4. KÍCH HOẠT CHẾ ĐỘ TẤY (ERASE) ---
    def start_erase_mode(self):
        if not self.active_tab_name: return
        self.current_action = "ERASE"
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="X_cursor") 
        
        # 🚀 DỌN SẠCH TOUCH BAR - CHỈ HIỆN ĐÚNG STATUS TẤY
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(
            self.touch_bar, text="ERASING: [ Click chuột trái vào bất kỳ ô nào để xóa ]", 
            font=("Consolas", 13, "bold"), text_color="#B3543E"
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            self.touch_bar, text="Enter / ESC: Chốt sổ", 
            font=("Consolas", 11, "italic"), text_color=TEXT_MUTED
        ).pack(side="left", padx=10)
        
        self.bind("<Return>", self.finish_erase_mode)
        self.bind("<Escape>", self.finish_erase_mode)
        data["canvas"].bind("<Return>", self.finish_erase_mode)
        data["canvas"].bind("<Escape>", self.finish_erase_mode)
        
        data["canvas"].focus_set()
        self.log_to_terminal("Đã cầm Tẩy trên tay! Gõ Enter hoặc ESC để cất tẩy.", "action")

    # --- 5. CHỐT SỔ TẤY ---
    def finish_erase_mode(self, event=None):
        self.current_action = None
        if self.active_tab_name:
            data = self.tabs[self.active_tab_name]
            data["canvas"].config(cursor="")
            data["canvas"].unbind("<Return>")
            data["canvas"].unbind("<Escape>")
            
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self.log_to_terminal("Đã cất Tẩy, trở lại chuột thường.", "success")
        self.toggle_touchbar_insert()

    # 🚀 KIẾN TRÚC MỚI: XOAY TRANG BẢN VẼ (VÀ XOAY CẢ KÝ HIỆU)
    def rotate_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        doc = data["pdf_doc"]
        page_idx = data["current_page"]
        page = doc.load_page(page_idx)
        
        # Lấy kích thước TRƯỚC KHI xoay
        old_h = page.rect.height
        
        # Xoay tờ giấy PDF 90 độ theo chiều kim đồng hồ
        page.set_rotation((page.rotation + 90) % 360)
        
        # Quét dọn vùng chọn nháp (tránh lỗi tọa độ khi bản vẽ lật ngang)
        data["vung_chon_pdf"] = None
        if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
        
        # 🚀 TOÁN HỌC MA THUẬT: Xoay tọa độ của TẤT CẢ markers đã đếm
        if page_idx in data.get("markers", {}):
            for ma_den, thong_tin in data["markers"][page_idx].items():
                toa_do_moi = []
                for box in thong_tin["toa_do"]:
                    x0, y0, x1, y1 = box[0], box[1], box[2], box[3]
                    # Thuật toán tịnh tiến tọa độ 90 độ CW:
                    nx0 = old_h - y1
                    ny0 = x0
                    nx1 = old_h - y0
                    ny1 = x1
                    toa_do_moi.append([nx0, ny0, nx1, ny1])
                thong_tin["toa_do"] = toa_do_moi
        
        # Bắt nó load lại bản vẽ mới
        self.render_page(self.active_tab_name, redraw_pdf=True)
        self.log_to_terminal("Đã xoay trang 90° và nắn lại tọa độ ký hiệu!", "action")

    # ==========================================
    # KHU VỰC 6: XUẤT BẢN VẼ CÓ THREADING CHỐNG TREO APP
    # ==========================================
    def export_markup_pdf(self):
        if not self.active_tab_name:
            self.log_to_terminal("ERROR: Có bản vẽ nào đâu mà xuất sếp ơi!", "error")
            return
            
        data_tab = self.tabs[self.active_tab_name]
        duong_dan_goc = data_tab["pdf_doc"].name
        
        file_luu = fd.asksaveasfilename(
            title="Chọn nơi lưu bản vẽ bóc tách", defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")], initialfile=f"Boc_Tach_{self.active_tab_name}"
        )
        if not file_luu:
            self.log_to_terminal("Hủy bỏ xuất file.", "sys")
            return
            
        self.log_to_terminal("Đang khởi tạo bản sao và nạp Markup màu... VUI LÒNG ĐỢI!", "action")
        
        markers_data = data_tab.get("markers", {}) 
        bang_mau = data_tab.get("bang_mau_vat_the", {})
        visibility = data_tab.get("layer_visibility", {})
        scales = data_tab.get("layer_scale", {})
        
        # 🚀 BẮT LẠI GÓC XOAY CỦA TẤT CẢ CÁC TRANG ĐỂ GỬI XUỐNG XƯỞNG IN
        goc_xoay = {i: data_tab["pdf_doc"].load_page(i).rotation for i in range(data_tab["pdf_doc"].page_count)}
        
        threading.Thread(
            target=self._thread_export_pdf, 
            args=(duong_dan_goc, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay), 
            daemon=True
        ).start()

    def _thread_export_pdf(self, duong_dan_goc, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay):
        try:
            import fitz
            pdf_copy = fitz.open(duong_dan_goc)
            tong_o_ve = 0
            
            # 🚀 ĐỒNG BỘ GÓC XOAY CHO BẢN SAO TRƯỚC KHI ĐÓNG DẤU
            for i in range(pdf_copy.page_count):
                p = pdf_copy.load_page(i)
                if p.rotation != goc_xoay.get(i, 0):
                    p.set_rotation(goc_xoay.get(i, 0))
            
            for trang_idx, layers in markers_data.items():
                page = pdf_copy.load_page(trang_idx)
                
                for ma_den, thong_tin in layers.items():
                    if not visibility.get(ma_den, True): continue
                        
                    mau_hex = bang_mau.get(ma_den, "#FFFFFF")
                    rgb = tuple(int(mau_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                    scale = scales.get(ma_den, 1.0)
                    
                    shape = page.new_shape() 
                    so_luong_ma_nay = 0
                    
                    for box in thong_tin["toa_do"]:
                        bx0, by0, bx1, by1 = box[0], box[1], box[2], box[3]
                        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
                        canh_vuong = 15.0 * scale
                        
                        bx0_moi = cx - canh_vuong / 2
                        by0_moi = cy - canh_vuong / 2
                        bx1_moi = cx + canh_vuong / 2
                        by1_moi = cy + canh_vuong / 2
                            
                        rect = fitz.Rect(bx0_moi, by0_moi, bx1_moi, by1_moi)
                        shape.draw_rect(rect) 
                        so_luong_ma_nay += 1
                        tong_o_ve += 1
                    
                    if so_luong_ma_nay > 0:
                        shape.finish(color=rgb, width=2)
                        shape.commit()
                        
            pdf_copy.save(file_luu, deflate=True, garbage=4)
            pdf_copy.close()
            
            self.after(0, self._hoan_thanh_export, True, file_luu, tong_o_ve, "")
        except Exception as e:
            self.after(0, self._hoan_thanh_export, False, "", 0, str(e))

    def _hoan_thanh_export(self, thanh_cong, file_luu, tong_o_ve, loi):
        if thanh_cong:
            self.log_to_terminal(f"✅ XUẤT FILE THÀNH CÔNG! Đã đóng dấu {tong_o_ve} markup.", "success")
            self.log_to_terminal(f"File lưu tại: {file_luu}", "sys")
        else:
            self.log_to_terminal(f"❌ LỖI XUẤT FILE: {loi}", "error")
    # ==========================================
    # 🚀 KHU VỰC 5.1: DẠY HỌC MINH BẠCH - HIỆN POPUP XÁC NHẬN
    # ==========================================
    def train_legend_action(self):
        file_bang = fd.askopenfilename(title="Chọn file chứa BẢNG CHÚ THÍCH", filetypes=[("PDF", "*.pdf")])
        if not file_bang: return
        
        dialog = ctk.CTkInputDialog(text="Bảng chú thích nằm ở trang số mấy? (VD: 1)", title="Trang chứa Bảng")
        trang_str = dialog.get_input()
        try:
            trang_so = int(trang_str) - 1 
            if trang_so < 0: raise ValueError
        except:
            self.log_to_terminal("Lỗi: Số trang không hợp lệ!", "error")
            return

        self.log_to_terminal(f"Đang phân tích Bảng Chú Thích tại trang {trang_so + 1}... Đợi em tí!", "action")
        # Gọi Threading để UI không bị đơ cựa
        threading.Thread(target=self._thread_train_legend, args=(file_bang, trang_so), daemon=True).start()

    def _thread_train_legend(self, filepath, page_idx):
        from logic.api_handler import goi_backend_hoc_ky_hieu
        thanh_cong, ket_qua = goi_backend_hoc_ky_hieu(filepath, page_idx)
        # Ném kết quả về UI an toàn
        self.after(0, self._hoan_thanh_train, thanh_cong, ket_qua)
        
    def _hoan_thanh_train(self, thanh_cong, ket_qua):
        if thanh_cong and ket_qua.get("data"):
            self.log_to_terminal("Đã vét được dữ liệu! Vui lòng kiểm tra trên Cửa sổ Xác minh.", "action")
            self.hien_thi_popup_xac_minh(ket_qua["data"])
        else:
            self.log_to_terminal(f"❌ LỖI HỌC BÀI: {ket_qua.get('error', 'Lỗi không xác định!')}", "error")

    def hien_thi_popup_xac_minh(self, du_lieu_hoc_duoc):
        # 🚀 CỬA SỔ POPUP XÁC MINH CỰC CHẤT
        popup = ctk.CTkToplevel(self)
        popup.title("XÁC MINH BẢNG KÝ HIỆU")
        popup.geometry("450x550")
        popup.attributes("-topmost", True) 
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="ĐÃ NHẬN DIỆN CÁC MÃ SAU:", font=("Arial", 16, "bold"), text_color=ACCENT_MAIN).pack(pady=(20, 10))
        ctk.CTkLabel(popup, text="Vui lòng kiểm tra xem máy đã bắt đúng Mã và Kích thước chưa.", font=("Arial", 12), text_color=TEXT_MUTED).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(popup, width=380, height=350, fg_color=PANEL_BG, corner_radius=8)
        scroll.pack(pady=10, padx=20, fill="both", expand=True)

        for ma, thong_so in du_lieu_hoc_duoc.items():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"MÃ: {ma}", font=("Consolas", 14, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"[ Rộng: {thong_so['w']} | Cao: {thong_so['h']} ]", font=("Consolas", 12), text_color=TEXT_MUTED).pack(side="right", padx=10)

        def xac_nhan_luu():
            if not hasattr(self, 'chu_ky_ai'): self.chu_ky_ai = {}
            self.chu_ky_ai.update(du_lieu_hoc_duoc)
            self.log_to_terminal(f"✅ Đã đóng dấu xác nhận. Sẵn sàng bóc tách chống nhầm lẫn!", "success")
            popup.destroy()

        ctk.CTkButton(
            popup, text="✔ XÁC NHẬN CHUẨN ĐÉT", height=45, corner_radius=8,
            font=("Arial", 14, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, text_color=BG_DARK,
            command=xac_nhan_luu
        ).pack(pady=(10, 20), padx=20, fill="x")
