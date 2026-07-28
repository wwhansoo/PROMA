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

        # 🚀 TOP RIBBON SIÊU XỊN
        self.ribbon = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=BG_DARK)
        self.ribbon.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Logo P. 
        ctk.CTkLabel(self.ribbon, text="P.", font=("Arial", 28, "bold"), text_color=ACCENT_MAIN).pack(side="left", padx=(20, 15))

        # Nút OPEN (Trực quan, có chữ đàng hoàng)
        ctk.CTkButton(
            self.ribbon, text="📂 OPEN", width=80, height=34, corner_radius=6,
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color="#2E2018", font=("Arial", 12, "bold"),
            command=self.open_additional_pdf
        ).pack(side="left", padx=(5, 5), pady=8)

        # Nút EXPORT
        ctk.CTkButton(
            self.ribbon, text="💾 EXPORT", width=80, height=34, corner_radius=6,
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color="#2E2018", font=("Arial", 12, "bold"),
            command=self.export_markup_pdf
        ).pack(side="left", padx=5, pady=8)

        # Nút INSERT ngông nghênh
        self.btn_insert = ctk.CTkButton(
            self.ribbon, text="✚ INSERT", width=100, height=34, corner_radius=6,
            fg_color=ACCENT_MAIN, text_color=BG_DARK, hover_color=ACCENT_HOVER, font=("Arial", 12, "bold")
        )
        self.btn_insert.pack(side="left", padx=15, pady=8)

        # Viền mờ ngăn cách
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=PANEL_BG).grid(row=0, column=0, columnspan=2, sticky="sew")

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

        # FLOATING NAVIGATION (Chuyển trang lơ lửng)
        self.floating_nav = ctk.CTkFrame(self.canvas_area, height=40, corner_radius=20, fg_color=PANEL_BG, bg_color=BG_DARK)
        self.floating_nav.place(relx=0.98, rely=0.03, anchor="ne")
        
        ctk.CTkButton(self.floating_nav, text="◀", width=30, height=30, corner_radius=15, fg_color="transparent", text_color=ACCENT_MAIN, hover_color=BG_DARK, command=self.prev_page).pack(side="left", padx=(5, 0), pady=5)
        self.lbl_page = ctk.CTkLabel(self.floating_nav, text="00 / 00", font=("Consolas", 14, "bold"), text_color=TEXT_MAIN)
        self.lbl_page.pack(side="left", padx=15, pady=5)
        ctk.CTkButton(self.floating_nav, text="▶", width=30, height=30, corner_radius=15, fg_color="transparent", text_color=ACCENT_MAIN, hover_color=BG_DARK, command=self.next_page).pack(side="left", padx=(0, 5), pady=5)

        self.floating_nav.place_forget()

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
        
        color_box = ctk.CTkFrame(row, width=15, height=15, corner_radius=3, fg_color=mau_sac, cursor="hand2")
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

        # 🚀 GẮN NÚT XÓA BÊN PHẢI NGOÀI CÙNG
        btn_delete = ctk.CTkButton(
            row, text="✖", width=24, height=24, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color="#B3543E", font=("Arial", 14),
            command=lambda m=ma_den, r=row: self.delete_layer(m, r)
        )
        btn_delete.pack(side="right", padx=(5, 5))

        # 🚀 RÁP THANH TRƯỢT SCALE KẾ BÊN NÚT XÓA
        scale_val = data.setdefault("layer_scale", {}).setdefault(ma_den, 1.0)
        slider = ctk.CTkSlider(
            row, width=70, height=12, from_=1.0, to=5.0, 
            button_color=mau_sac, progress_color=mau_sac,
            command=lambda v, m=ma_den: self.change_layer_scale(m, v)
        )
        slider.set(scale_val)
        slider.pack(side="right", padx=(5, 0))

        color_box.bind("<Button-1>", lambda e, m=ma_den, cb=color_box, sw=switch, sl=slider: self.change_layer_color(m, cb, sw, sl))

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
                
                self.floating_nav.place(relx=0.98, rely=0.03, anchor="ne")
                self.floating_nav.lift()
                self.lbl_page.configure(text=f"{tab_data['current_page'] + 1:02d} / {tab_data['pdf_doc'].page_count:02d}")
                self.lbl_zoom.configure(text=f"Zoom: {int(tab_data['zoom_level'] * 100)}%")
                
                for ma_den in sorted(tab_data["bang_mau_vat_the"].keys()):
                    mau_sac = tab_data["bang_mau_vat_the"][ma_den]
                    so_l = markers_trang_nay.get(ma_den, {}).get("so_luong", 0)
                    self.add_layer_toggle_ui(ma_den, mau_sac, so_l)

                self.render_page(name)
            else:
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
            self.floating_nav.place_forget()
            for child in self.layer_frame.winfo_children(): child.destroy()
        elif self.active_tab_name == tab_name:
            last_tab = list(self.tabs.keys())[-1]
            self.switch_to_tab(last_tab)

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
        
        # 🚀 Nếu đang ở chế độ Kéo chọn vùng
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            data["canvas"].config(cursor="crosshair")
            data["drag_data"]["start_x"] = event.x
            data["drag_data"]["start_y"] = event.y
            # Xóa khung cũ nếu có
            if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
            # Vẽ nét đứt nháp
            data["rect_id"] = data["canvas"].create_rectangle(event.x, event.y, event.x, event.y, outline=ACCENT_MAIN, width=2, dash=(4, 4), tags="selection_rect")
        else: # Trở về mặc định là kéo thả bản vẽ
            data["canvas"].config(cursor="fleur")
            data["drag_data"]["x"] = event.x
            data["drag_data"]["y"] = event.y

    def on_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            # Co giãn hình chữ nhật theo tay kéo
            start_x = data["drag_data"]["start_x"]
            start_y = data["drag_data"]["start_y"]
            data["canvas"].coords(data.get("rect_id"), start_x, start_y, event.x, event.y)
        else:
            dx, dy = event.x - data["drag_data"]["x"], event.y - data["drag_data"]["y"]
            data["canvas"].move("pdf_img", dx, dy)
            data["img_pos"][0] += dx
            data["img_pos"][1] += dy
            data["drag_data"]["x"], data["drag_data"]["y"] = event.x, event.y

    # 🚀 HÀM MỚI: CHỐT TỌA ĐỘ KHI NHẢ CHUỘT
    # 🚀 HÀM MỚI: ĐÃ ÉP KIỂU SẠCH SẼ VÀ ĐỂ NGUYÊN KHUNG CHỌN
    def on_drag_release(self, event):
        if not self.active_tab_name: return
        if not hasattr(self, 'area_mode_var') or self.area_mode_var.get() == "Toàn bản vẽ": return
        
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="") # Trả lại trỏ chuột thường
        
        # Lấy tọa độ an toàn và ép kiểu int
        drag_data = data.get("drag_data", {})
        start_x = int(drag_data.get("start_x", event.x))
        start_y = int(drag_data.get("start_y", event.y))
        end_x = int(event.x)
        end_y = int(event.y)
        
        # Nếu lỡ tay click nhẹ (không kéo), hủy vùng chọn
        if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:
            data["vung_chon_pdf"] = None
            rect_id = data.get("rect_id")
            if rect_id: data["canvas"].delete(rect_id)
            self.log_to_terminal("Đã hủy vùng chọn.", "sys")
            return
            
        # 🚀 Ép từ Tọa độ Màn hình về Tọa độ PDF (Ép float rõ ràng)
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
                self.log_to_terminal("Đã hoàn tất đếm. Đang đóng dấu lên bản vẽ...", "success")
                if "markers" not in data_tab: data_tab["markers"] = {}
                trang_hien_tai = data_tab["current_page"]
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
            
        self.log_to_terminal("Đang khởi tạo bản sao và nạp Markup màu... VUI LÒNG ĐỢI, ĐỪNG BẤM LUNG TUNG!", "action")
        
        # 🚀 Ép kiểu copy dữ liệu ra trước để ném vào luồng ngầm (Tránh đụng độ bộ nhớ với UI)
        markers_data = data_tab.get("markers", {}) 
        bang_mau = data_tab.get("bang_mau_vat_the", {})
        visibility = data_tab.get("layer_visibility", {})
        scales = data_tab.get("layer_scale", {})
        
        # Kích hoạt luồng chạy ngầm để UI vẫn mượt mà lướt web được
        threading.Thread(
            target=self._thread_export_pdf, 
            args=(duong_dan_goc, file_luu, markers_data, bang_mau, visibility, scales), 
            daemon=True
        ).start()

    def _thread_export_pdf(self, duong_dan_goc, file_luu, markers_data, bang_mau, visibility, scales):
        try:
            import fitz
            pdf_copy = fitz.open(duong_dan_goc)
            tong_o_ve = 0
            
            for trang_idx, layers in markers_data.items():
                page = pdf_copy.load_page(trang_idx)
                
                for ma_den, thong_tin in layers.items():
                    if not visibility.get(ma_den, True): continue
                        
                    mau_hex = bang_mau.get(ma_den, "#FFFFFF")
                    rgb = tuple(int(mau_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                    scale = scales.get(ma_den, 1.0)
                    
                    # 🚀 VŨ KHÍ TỐI THƯỢNG: TẠO KHUNG VẼ NHÁP HÀNG LOẠT (SHAPE)
                    shape = page.new_shape() 
                    so_luong_ma_nay = 0
                    
                    for box in thong_tin["toa_do"]:
                        bx0, by0, bx1, by1 = box[0], box[1], box[2], box[3]
                        
                        # 🚀 TÂM ĐIỂM TUYỆT ĐỐI (LÚC XUẤT FILE)
                        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
                        
                        # Kích thước chuẩn 15 points (nhân với scale từ thanh trượt)
                        canh_vuong = 15.0 * scale
                        
                        # Nặn ra hình vuông mới từ tâm
                        bx0_moi = cx - canh_vuong / 2
                        by0_moi = cy - canh_vuong / 2
                        bx1_moi = cx + canh_vuong / 2
                        by1_moi = cy + canh_vuong / 2
                            
                        rect = fitz.Rect(bx0_moi, by0_moi, bx1_moi, by1_moi)
                        
                        # CHỈ VẼ NHÁP VÀO BỘ NHỚ, CHƯA IN RA PDF
                        shape.draw_rect(rect) 
                        so_luong_ma_nay += 1
                        tong_o_ve += 1
                    
                    if so_luong_ma_nay > 0:
                        # 🚀 ĐÓNG DẤU 1 LẦN DUY NHẤT CHO CẢ NGÀN CÁI ĐÈN!
                        shape.finish(color=rgb, width=2)
                        shape.commit()
                        
            # 🚀 LƯU FILE VỚI BÙA ÉP XÁC: garbage=4 (Dọn sạch rác đồ họa thừa của CAD)
            pdf_copy.save(file_luu, deflate=True, garbage=4)
            pdf_copy.close()
            
            # Gửi tín hiệu hoàn thành về cho UI an toàn
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
