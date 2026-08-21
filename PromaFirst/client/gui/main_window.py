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
# 🚀 CẤU HÌNH PALETTE "APPLE PROMA THEME"
# ==========================================
ctk.set_appearance_mode("dark")

# Nền đen sâu & xám không gian chuẩn macOS
BG_DARK = "#120C08"          
PANEL_BG = "#1C1510"         # Xám nâu nhẹ, mượt hơn Zinc
PANEL_BORDER = "#2E241C"     # Viền bo góc dịu mắt

# Màu Nâu Vàng Chủ Đạo PROMA
ACCENT_MAIN = "#B07D4C"      
ACCENT_HOVER = "#C49A6C"     
ACCENT_MUTED = "#5E4228"     

# Typography mượt mà
TEXT_MAIN = "#F5F2EB"        
TEXT_MUTED = "#8A7E72"       
GRID_COLOR = "#241A11"       

# Trạng thái Workspace
TAB_ACTIVE = "#1F160E"       
TAB_INACTIVE = "#120C08"     
TAB_HOVER = "#2A1E14"        
CLOSE_BTN_HOVER = "#D9534F"  

class PromaEnterpriseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Proma.")
        self.geometry("1440x880")
        self.configure(fg_color=BG_DARK)

        self.tabs = {}
        self.active_tab_name = None
        self.last_mouse_update = 0
        self.zoom_timer = None

        self.danh_sach_mau = [
            "#F87171", "#FB923C", "#FACC15", "#4ADE80", "#2DD4BF", 
            "#38BDF8", "#818CF8", "#C084FC", "#F472B6", "#FB7185",
            "#E879F9", "#A78BFA", "#34D399", "#60A5FA", "#FBBF24",
            "#F43F5E", "#10B981", "#06B6D4", "#6366F1", "#D946EF"
        ]
        self.mau_index = 0

        self.show_splash_screen()

    # ==========================================
    # KHU VỰC 1: SPLASH SCREEN (APPLE KEYNOTE STYLE)
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
            anh_logo = ctk.CTkImage(light_image=img_goc, dark_image=img_goc, size=(int(w_goc*(160/h_goc)), 160))
            ctk.CTkLabel(self.splash_frame, text="", image=anh_logo).pack(pady=(190, 15))
        except FileNotFoundError:
            ctk.CTkLabel(self.splash_frame, text="PROMA // CORE", font=("Consolas", 42, "bold"), text_color=ACCENT_MAIN).pack(pady=(190, 15))

        ctk.CTkLabel(self.splash_frame, text="Proma.", font=("EB Garamond ExtraBold", 54, "bold"), text_color=TEXT_MAIN).pack(pady=(0, 4))
        ctk.CTkLabel(self.splash_frame, text="The smarter way to manage construction projects.", font=("EB Garamond", 20), text_color=TEXT_MUTED).pack(pady=(0, 45))

        # 🚀 Bo góc 8px sang trọng
        ctk.CTkButton(
            self.splash_frame, text="UPLOAD PROJECT (.PDF)", height=48, width=280, 
            corner_radius=8, font=("Montserrat Bold", 14, "bold"),
            fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, text_color=BG_DARK,
            border_width=1, border_color="#D19E6E",
            command=self.open_first_pdf
        ).pack()

    def open_first_pdf(self):
        filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
        if not filepath: return
        self.splash_frame.pack_forget()
        self.build_workspace()
        self.add_new_tab(filepath)

    def open_additional_pdf(self):
        if not self.active_tab_name: 
            filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
            if filepath: self.add_new_tab(filepath)
            return

        # 🚀 Bo góc 12px cho Popup mượt mà
        popup = ctk.CTkToplevel(self)
        popup.title("Project Workspace")
        popup.geometry("480x220")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="Open Mode Selection", font=("Montserrat Bold", 15, "bold"), text_color=ACCENT_MAIN).pack(pady=(25, 10))
        ctk.CTkLabel(popup, text="Select how you want to load the new blueprint into the workspace.", font=("Montserrat", 12), text_color=TEXT_MUTED).pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        def add_to_current():
            popup.destroy()
            filepath = fd.askopenfilename(title="Merge Blueprint into Project", filetypes=[("Bản vẽ PDF", "*.pdf")])
            if filepath: self.merge_pdf_to_current_project(filepath)

        def create_new():
            popup.destroy()
            filepath = fd.askopenfilename(title="Select Blueprint for New Project", filetypes=[("Bản vẽ PDF", "*.pdf")])
            if filepath: self.add_new_tab(filepath)

        ctk.CTkButton(
            btn_frame, text="Append to Project", height=42, corner_radius=8, 
            font=("Montserrat Bold", 12, "bold"), fg_color=PANEL_BG, hover_color=TAB_HOVER, 
            border_width=1, border_color=ACCENT_MAIN, text_color=ACCENT_MAIN, 
            command=add_to_current
        ).pack(side="left", expand=True, fill="x", padx=6)
        
        ctk.CTkButton(
            btn_frame, text="New Project Tab", height=42, corner_radius=8, 
            font=("Montserrat Bold", 12, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, 
            text_color=BG_DARK, border_width=1, border_color="#D19E6E", 
            command=create_new
        ).pack(side="right", expand=True, fill="x", padx=6)

    def merge_pdf_to_current_project(self, filepath):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        try:
            doc_moi = fitz.open(filepath)
            data["pdf_doc"].insert_pdf(doc_moi)
            doc_moi.close()
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.log_to_terminal(f"APPENDED: {os.path.basename(filepath)} added. Total project pages: {data['pdf_doc'].page_count}", "success")
        except Exception as e:
            self.log_to_terminal(f"MERGE ENGINE EXCEPTION: {e}", "error")

    # ==========================================
    # KHU VỰC 2: WORKSPACE (APPLE DESIGN SYSTEM)
    # ==========================================
    def build_workspace(self):
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0, minsize=350)

        # ==========================================
        # 🚀 TOP RIBBON TOOLBAR
        # ==========================================
        self.top_toolbar = ctk.CTkFrame(self, height=54, corner_radius=0, fg_color=BG_DARK)
        self.top_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_toolbar.pack_propagate(False) 

        self.toolbar_left = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_left.pack(side="left", fill="y", padx=(20, 10))

        ctk.CTkLabel(self.toolbar_left, text="P.", font=("Montserrat Bold", 26, "bold"), text_color=ACCENT_MAIN).pack(side="left", padx=(0, 18))

        # 🚀 Bo góc 6px cho cụm nút nhỏ
        ctk.CTkButton(
            self.toolbar_left, text="OPEN", width=68, height=30, corner_radius=6, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.open_additional_pdf
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            self.toolbar_left, text="EXPORT", width=74, height=30, corner_radius=6, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.export_markup_pdf
        ).pack(side="left", padx=4)
        
        self.btn_insert = ctk.CTkButton(
            self.toolbar_left, text="✚ INSERT", width=86, height=30, corner_radius=6, 
            fg_color=ACCENT_MAIN, text_color=BG_DARK, hover_color=ACCENT_HOVER, 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color="#D19E6E",
            command=self.toggle_touchbar_insert
        )
        self.btn_insert.pack(side="left", padx=(6, 4))

        # 🚀 Touch Bar bo góc 8px mượt mà
        self.touch_bar = ctk.CTkFrame(
            self.top_toolbar, height=34, corner_radius=8, 
            fg_color="#18110B", border_width=1, border_color=PANEL_BORDER
        )
        self.touch_bar.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        self.touch_bar.pack_propagate(False)

        self.toolbar_right = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_right.pack(side="right", fill="y", padx=(10, 20))

        ctk.CTkButton(
            self.toolbar_right, text="⟳ XOAY", width=72, height=30, corner_radius=6, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.rotate_page
        ).pack(side="left", padx=4)

        self.btn_mono = ctk.CTkButton(
            self.toolbar_right, text="◐ MONO", width=74, height=30, corner_radius=6, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.toggle_monochrome
        )
        self.btn_mono.pack(side="left", padx=(4, 16))

        self.nav_frame = ctk.CTkFrame(self.toolbar_right, fg_color="transparent")
        self.nav_frame.pack(side="left", pady=10)
        
        ctk.CTkButton(
            self.nav_frame, text="❮", width=26, height=26, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 13, "bold"), command=self.prev_page
        ).pack(side="left", padx=1)
        
        self.lbl_page = ctk.CTkLabel(
            self.nav_frame, text="00 / 00", 
            font=("Consolas", 12, "bold"), text_color=TEXT_MAIN
        )
        self.lbl_page.pack(side="left", padx=8)
        
        ctk.CTkButton(
            self.nav_frame, text="❯", width=26, height=26, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=TAB_HOVER, 
            font=("Montserrat Bold", 13, "bold"), command=self.next_page
        ).pack(side="left", padx=1)

        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=PANEL_BORDER).grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- CENTER ANNOTATION AREA ---
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(8, 15))
        self.center_frame.pack_propagate(False)

        self.custom_tab_bar = ctk.CTkScrollableFrame(
            self.center_frame, height=42, orientation="horizontal", 
            fg_color="transparent", bg_color="transparent"
        )
        self.custom_tab_bar.pack(side="top", fill="x", pady=(0, 6))
        self.custom_tab_bar._scrollbar.configure(width=0) 

        # 🚀 Khung Canvas bo góc 12px viền mềm
        self.canvas_area = ctk.CTkFrame(
            self.center_frame, corner_radius=12, 
            fg_color=BG_DARK, border_width=1, border_color=PANEL_BORDER
        )
        self.canvas_area.pack(side="top", fill="both", expand=True)

        # --- RIGHT PANEL (APPLE PRO ENGINE CONTROL) ---
        self.right_panel = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color=PANEL_BG)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_propagate(False)

        ctk.CTkLabel(
            self.right_panel, text="MODE", 
            font=("Montserrat Bold", 13, "bold"), text_color=ACCENT_MAIN
        ).pack(anchor="w", padx=16, pady=(22, 6))

        # 🚀 Cụm selector bo tròn 8px
        self.mode_var = ctk.StringVar(value="Vật thể")
        self.mode_selector = ctk.CTkSegmentedButton(
            self.right_panel, values=["Vật thể", "Đường ống", "Diện tích"], variable=self.mode_var, 
            selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, 
            text_color=TEXT_MAIN, font=("Montserrat Bold", 11, "bold"), corner_radius=8
        )
        self.mode_selector.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(
            self.right_panel, text="REGION", 
            font=("Montserrat Bold", 13, "bold"), text_color=TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(16, 6))
        
        self.area_mode_var = ctk.StringVar(value="Toàn bản vẽ")
        self.area_selector = ctk.CTkSegmentedButton(
            self.right_panel, values=["Toàn bản vẽ", "Kéo chọn vùng"], variable=self.area_mode_var,
            selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, 
            text_color=TEXT_MAIN, font=("Montserrat Bold", 11, "bold"), corner_radius=8,
            command=self.on_area_mode_change  # 🚀 BÙA: GẮN DÂY THẦN KINH DỌN RÁC
        )
        self.area_selector.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_learn_legend = ctk.CTkButton(
            self.right_panel, text="📖 Learn Symbols", height=38, corner_radius=8, 
            font=("Montserrat Bold", 12, "bold"), fg_color="#1F160E", hover_color="#2A1E14", 
            text_color=ACCENT_MAIN, border_width=1, border_color=ACCENT_MAIN,
            command=self.train_legend_action
        )
        self.btn_learn_legend.pack(fill="x", padx=16, pady=(4, 6))

        self.btn_run = ctk.CTkButton(
            self.right_panel, text="BREAK GROUND", height=46, corner_radius=8, 
            font=("Montserrat Bold", 14, "bold"), fg_color=ACCENT_MAIN, 
            hover_color=ACCENT_HOVER, text_color=BG_DARK, 
            border_width=1, border_color="#D19E6E",
            command=self.run_engine
        )
        self.btn_run.pack(fill="x", padx=16, pady=(8, 18))
        
        self.master_switch_var = ctk.BooleanVar(value=True)
        self.master_switch = ctk.CTkSwitch(
            self.right_panel, text="LAYERS", font=("Montserrat Bold", 12, "bold"), 
            text_color=TEXT_MAIN, progress_color=ACCENT_MAIN, 
            variable=self.master_switch_var, command=self.toggle_all_layers
        )
        self.master_switch.pack(anchor="w", padx=16, pady=(0, 10))

        # 🚀 Khung Layer List bo góc 8px
        self.layer_frame = ctk.CTkScrollableFrame(
            self.right_panel, fg_color=BG_DARK, height=340, 
            corner_radius=8, border_width=1, border_color=PANEL_BORDER
        )
        self.layer_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            self.right_panel, text="TERMINAL LOG", 
            font=("Montserrat Bold", 11, "bold"), text_color=TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(0, 6))
        
        self.txt_log = ctk.CTkTextbox(
            self.right_panel, fg_color=BG_DARK, text_color=TEXT_MAIN, 
            font=("Consolas", 11), corner_radius=8, height=115,
            border_width=1, border_color=PANEL_BORDER
        )
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 20))
        self.txt_log.configure(state="disabled")

        self.txt_log._textbox.tag_configure("sys", foreground=TEXT_MUTED)
        self.txt_log._textbox.tag_configure("success", foreground="#D5B07C") 
        self.txt_log._textbox.tag_configure("error", foreground=CLOSE_BTN_HOVER)
        self.txt_log._textbox.tag_configure("action", foreground=ACCENT_MAIN)

        # Status Bar bo góc 8px
        self.statusbar = ctk.CTkFrame(self.center_frame, height=30, corner_radius=8, fg_color=PANEL_BG)
        self.statusbar.pack(side="bottom", fill="x")

        self.lbl_coords = ctk.CTkLabel(self.statusbar, text="X: 0000 | Y: 0000", font=("Consolas", 11), text_color=TEXT_MUTED)
        self.lbl_coords.pack(side="left", padx=16)

        self.lbl_zoom = ctk.CTkLabel(self.statusbar, text="Zoom: 200%", font=("Consolas", 11), text_color=TEXT_MUTED)
        self.lbl_zoom.pack(side="right", padx=16)

        self.log_to_terminal("PROMA Enterprise Core Initialized.", "sys")
    
    # ==========================================
    # 🚀 HÀM DỌN RÁC KHI ĐỔI CHẾ ĐỘ QUÉT
    # ==========================================
    def on_area_mode_change(self, new_mode):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        if new_mode == "Toàn bản vẽ":
            # Gạt về Toàn bản vẽ -> Xóa ngay nét đứt và hủy dữ liệu vùng chọn
            if data.get("rect_id"):
                data["canvas"].delete(data["rect_id"])
                data["rect_id"] = None
            data["vung_chon_pdf"] = None
            data["canvas"].config(cursor="")
            self.log_to_terminal("Đã hủy chế độ Kéo Vùng. Trở về quét toàn bản vẽ.", "sys")
        else:
            # Gạt sang Kéo chọn vùng -> Đổi con trỏ chuột thành hình dấu cộng
            data["canvas"].config(cursor="crosshair")
            self.log_to_terminal("Chế độ chọn vùng: Kéo chuột để khoanh vùng đếm.", "action")

    # ==========================================
    # KHU VỰC 3: LAYER MANAGER ROWS (APPLE DRAG & DROP UI)
    # ==========================================
    def build_layer_manager_for_current_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        for child in self.layer_frame.winfo_children():
            child.destroy()
            
        data["layer_switches"] = {}
        data["layer_labels"] = {} 
        data["layer_row_widgets"] = [] 
        
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        active_keys = set(markers_trang_nay.keys())
        if "layer_order" not in data: data["layer_order"] = []
        
        data["layer_order"] = [k for k in data["layer_order"] if k in active_keys]
        for k in sorted(active_keys):
            if k not in data["layer_order"]:
                data["layer_order"].append(k)
        
        for ma_den in data["layer_order"]:
            mau_sac = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
            so_l = markers_trang_nay[ma_den].get("so_luong", 0)
            self.add_layer_toggle_ui(ma_den, mau_sac, so_l)

    def add_layer_toggle_ui(self, ma_den, mau_sac, so_luong=0):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]

        row = ctk.CTkFrame(self.layer_frame, fg_color="transparent", height=32)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False) 
        
        data["layer_row_widgets"].append((ma_den, row))
        
        # 1. BÊN TRÁI
        drag_handle = ctk.CTkLabel(row, text="•", font=("Arial", 22, "bold"), text_color="#52525B", width=16, cursor="fleur")
        drag_handle.pack(side="left", padx=(2, 6))
        
        drag_handle.bind("<ButtonPress-1>", lambda e, m=ma_den, r=row: self.on_drag_layer_start(e, m, r))
        drag_handle.bind("<B1-Motion>", lambda e: self.on_drag_layer_motion(e))
        drag_handle.bind("<ButtonRelease-1>", lambda e: self.on_drag_layer_drop(e))

        # Bo góc mượt 4px cho cục màu
        color_box = ctk.CTkButton(row, text="", width=16, height=16, corner_radius=4, fg_color=mau_sac, hover_color=mau_sac, cursor="hand2")
        color_box.pack(side="left", padx=(0, 8))
        
        switch_var = ctk.BooleanVar(value=data["layer_visibility"].get(ma_den, True))
        switch = ctk.CTkSwitch(
            row, text="", width=28, switch_width=28, switch_height=14, 
            progress_color=mau_sac, variable=switch_var, command=lambda m=ma_den, v=switch_var: self.toggle_layer(m, v.get())
        )
        switch.pack(side="left", padx=(0, 6))
        data["layer_switches"][ma_den] = switch

        # 2. BÊN PHẢI (Các nút chức năng cơ bản)
        btn_delete = ctk.CTkButton(
            row, text="×", width=22, height=22, corner_radius=6, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=CLOSE_BTN_HOVER, font=("Consolas", 16, "bold"),
            command=lambda m=ma_den, r=row: self.delete_layer(m, r)
        )
        btn_delete.pack(side="right", padx=(2, 4))

        # Nút bật Popup Kích thước
        btn_size = ctk.CTkButton(
            row, text="⤢", width=22, height=22, corner_radius=6,
            fg_color="transparent", text_color=TEXT_MUTED, hover_color="#2A1E14", font=("Consolas", 15)
            # Lệnh command sẽ gán ở dưới
        )
        btn_size.pack(side="right", padx=(2, 4))

        # ==========================================
        # 🚀 HỆ THỐNG POPUP NỔI LỀNH BỀNH
        # ==========================================
        # Tạo một cái panel nhỏ màu hơi sáng hơn xíu để làm nền nổi
        popup_panel = ctk.CTkFrame(row, fg_color="#2A1E14", corner_radius=6, height=28)
        
        def hien_popup():
            # Nổi lên góc phải, nằm đè lên vị trí của 2 nút kia cho siêu gọn
            popup_panel.place(relx=1.0, rely=0.5, anchor="e", x=-2)
            popup_panel.tkraise() # Bùa ép nó phải nổi lên trên cùng!

        def an_popup(event=None):
            popup_panel.place_forget()

        btn_size.configure(command=hien_popup)

        # Thanh kéo kích thước
        scale_val = data.setdefault("layer_scale", {}).setdefault(ma_den, 1.0)
        slider = ctk.CTkSlider(
            popup_panel, width=70, height=12, from_=1.0, to=5.0, 
            button_color=mau_sac, progress_color=mau_sac, 
            command=lambda v, m=ma_den: self.change_layer_scale(m, v)
        )
        slider.set(scale_val)
        slider.pack(side="right", padx=(6, 2), pady=4)

        # 🚀 TÍNH NĂNG TỰ ĐỘNG HỦY DIỆT: Kéo buông chuột ra -> Tự tắt Popup!
        slider.bind("<ButtonRelease-1>", an_popup)

        # 3. Ở GIỮA
        text_hien_thi = f"{ma_den} [{so_luong:02d}]"
        lbl_name = ctk.CTkLabel(row, text=text_hien_thi, font=("Consolas", 12, "bold"), text_color=TEXT_MAIN, anchor="w")
        lbl_name.pack(side="left", fill="x", expand=True)
        
        data["layer_labels"][ma_den] = lbl_name
        
        color_box.configure(command=lambda m=ma_den, cb=color_box, sw=switch, sl=slider: self.change_layer_color(m, cb, sw, sl))
        lbl_name.bind("<Double-Button-1>", lambda e, m=ma_den: self.rename_layer_action(m))
        lbl_name.configure(cursor="xterm")
    
    def on_drag_layer_start(self, event, ma_den, row_widget):
        self.drag_data = {"ma": ma_den, "widget": row_widget}
        # Bo viền mềm lúc Highlight kéo thả
        row_widget.configure(fg_color="#2E241C", corner_radius=6) 
        self.log_to_terminal(f"Reordering layer [{ma_den}]...", "sys")

    def on_drag_layer_motion(self, event):
        if getattr(self, 'drag_data', None) is None: return
        
        y_mouse = event.y_root 
        data = self.tabs[self.active_tab_name]
        
        target_ma = None
        for m, w in data.get("layer_row_widgets", []):
            if m == self.drag_data["ma"]: continue
            wy = w.winfo_rooty()
            wh = w.winfo_height()
            if wy <= y_mouse <= wy + wh:
                target_ma = m
                break
        
        if target_ma:
            order = data["layer_order"]
            idx1 = order.index(self.drag_data["ma"])
            idx2 = order.index(target_ma)
            
            if idx1 != idx2:
                order.insert(idx2, order.pop(idx1))
                
                widget_dict = {m: w for m, w in data["layer_row_widgets"]}
                for m in order:
                    if m in widget_dict:
                        widget_dict[m].pack_forget()
                        widget_dict[m].pack(fill="x", pady=2)
                
                self.update_idletasks()

    def on_drag_layer_drop(self, event):
        if getattr(self, 'drag_data', None) is None: return
        self.drag_data["widget"].configure(fg_color="transparent")
        self.drag_data = None
        self.render_page(self.active_tab_name, redraw_pdf=False)
        self.log_to_terminal("Layer order updated.", "success")

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

    def change_layer_scale(self, ma_den, value):
        if not self.active_tab_name: return
        self.tabs[self.active_tab_name]["layer_scale"][ma_den] = value
        
        if hasattr(self, 'scale_timer') and self.scale_timer:
            self.after_cancel(self.scale_timer)
        self.scale_timer = self.after(50, lambda: self.render_page(self.active_tab_name, redraw_pdf=False))

    def change_layer_scale(self, ma_den, value):
        if not self.active_tab_name: return
        self.tabs[self.active_tab_name]["layer_scale"][ma_den] = value
        
        if hasattr(self, 'scale_timer') and self.scale_timer:
            self.after_cancel(self.scale_timer)
        self.scale_timer = self.after(50, lambda: self.render_page(self.active_tab_name, redraw_pdf=False))

    # 🚀 BÙA THÒ RA THỤT VÀO CHO SLIDER KÍCH THƯỚC
    # 🚀 BÙA NỔI LỀNH BỀNH (KHÔNG ÉP LAYOUT CHỮ)
    def toggle_slider_visibility(self, slider_widget):
        # Dùng place_info() để kiểm tra xem nó đang nổi hay đang lặn
        if len(slider_widget.place_info()) > 0:
            # Nếu đang nổi -> Rút lại cho chìm xuống
            slider_widget.place_forget()
        else:
            # Nếu đang chìm -> Bơm lên cho nổi lềnh bềnh!
            # relx=1.0: Căn từ mép phải của thanh layer.
            # x=-70: Đẩy lùi sang trái 70 pixel (Vừa đủ né 2 cái nút Icon và Xóa).
            # rely=0.5, anchor="e": Căn giữa chiều dọc, neo ở bên phải.
            slider_widget.place(relx=1.0, x=-70, rely=0.5, anchor="e")

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

    def delete_layer(self, ma_den, row_widget):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # 1. Dọn dẹp sạch Data gốc
        if ma_den in data["bang_mau_vat_the"]: del data["bang_mau_vat_the"][ma_den]
        if ma_den in data["layer_visibility"]: del data["layer_visibility"][ma_den]
        if ma_den in data["layer_switches"]: del data["layer_switches"][ma_den]
        if ma_den in data["layer_scale"]: del data["layer_scale"][ma_den]
        
        # 🚀 2. DỌN SẠCH XÁC TRONG KHO UI ĐỂ CHỐNG CRASH NGẦM!
        if "layer_labels" in data and ma_den in data["layer_labels"]:
            del data["layer_labels"][ma_den]
            
        if "layer_row_widgets" in data:
            data["layer_row_widgets"] = [(m, w) for m, w in data["layer_row_widgets"] if m != ma_den]
        
        if ma_den in data.get("layer_order", []): 
            data["layer_order"].remove(ma_den)
            
        trang_idx = data["current_page"]
        if trang_idx in data.get("markers", {}) and ma_den in data["markers"][trang_idx]:
            del data["markers"][trang_idx][ma_den]
            
        # 3. Tiêu hủy giao diện
        row_widget.destroy()
        
        # 4. Giờ thì render tẹt ga, luồng code chạy thông suốt từ trên xuống dưới
        self.render_page(self.active_tab_name, redraw_pdf=True)
        self.log_to_terminal(f"Đã gỡ mã '{ma_den}' khỏi bản vẽ.", "error")
    
    def rename_layer_action(self, ma_cu):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        dialog = ctk.CTkInputDialog(text=f"Đổi tên cho Layer [{ma_cu}]:", title="Rename Layer")
        ma_moi = dialog.get_input()
        
        if not ma_moi or ma_moi.strip() == "" or ma_moi.upper().strip() == ma_cu:
            return 
            
        ma_moi = ma_moi.upper().strip()
        
        if ma_moi in data["bang_mau_vat_the"]:
            self.log_to_terminal(f"LỖI: Tên '{ma_moi}' đã tồn tại!", "error")
            return

        data["bang_mau_vat_the"][ma_moi] = data["bang_mau_vat_the"].pop(ma_cu)
        data["layer_visibility"][ma_moi] = data["layer_visibility"].pop(ma_cu)
        if ma_cu in data["layer_scale"]:
            data["layer_scale"][ma_moi] = data["layer_scale"].pop(ma_cu)

        if ma_cu in data.get("layer_order", []):
            idx = data["layer_order"].index(ma_cu)
            data["layer_order"][idx] = ma_moi

        for trang_idx, markers_trang in data.get("markers", {}).items():
            if ma_cu in markers_trang:
                markers_trang[ma_moi] = markers_trang.pop(ma_cu)

        self.log_to_terminal(f"Đổi tên Layer: [{ma_cu}] -> [{ma_moi}]", "success")
        
        self.build_layer_manager_for_current_page()
        self.render_page(self.active_tab_name, redraw_pdf=False)

    def update_layer_manager_counts(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        if "layer_labels" in data:
            for ma_den, lbl in data["layer_labels"].items():
                lbl.configure(text=f"{ma_den} [00]")
                
        for ma_den, thong_tin in markers_trang_nay.items():
            if "layer_labels" in data and ma_den in data["layer_labels"]:
                lbl = data["layer_labels"][ma_den]
                lbl.configure(text=f"{ma_den} [{thong_tin['so_luong']:02d}]")

# ==========================================
    # KHU VỰC 3 (TIẾP THEO): QUẢN LÝ TAB BẢN VẼ
    # ==========================================
    def add_new_tab(self, filepath):
        base_name = os.path.basename(filepath)
        tab_name = base_name
        
        count = 1
        while tab_name in self.tabs:
            tab_name = f"{base_name} ({count})"
            count += 1

        # 🚀 Tab bo góc mượt 8px
        tab_ui = ctk.CTkFrame(
            self.custom_tab_bar, fg_color=TAB_ACTIVE, 
            corner_radius=8, border_width=1, border_color=PANEL_BORDER
        )
        tab_ui.pack(side="left", padx=(0, 6), pady=2, fill="y") 

        lbl_name = ctk.CTkLabel(tab_ui, text=tab_name, font=("Montserrat Bold", 11, "bold"), text_color=TEXT_MAIN)
        lbl_name.pack(side="left", padx=(14, 8), pady=4)
        
        btn_close = ctk.CTkButton(
            tab_ui, text="×", width=22, height=22, corner_radius=6,
            fg_color="transparent", hover_color=CLOSE_BTN_HOVER, text_color=TEXT_MUTED, font=("Consolas", 14, "bold"),
            command=lambda name=tab_name: self.close_specific_tab(name)
        )
        btn_close.pack(side="right", padx=(0, 6), pady=4)

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

        self.canvas_area.update_idletasks() 
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10: cw = 1200  
        if ch < 10: ch = 700

        doc = fitz.open(filepath)
        page = doc.load_page(0)
        
        zoom_macdinh = 2.0
        pw = page.rect.width * zoom_macdinh
        ph = page.rect.height * zoom_macdinh
        
        start_x = (cw - pw) / 2
        start_y = (ch - ph) / 2

        self.tabs[tab_name] = {
            "pdf_doc": doc,
            "current_page": 0,
            "zoom_level": zoom_macdinh,
            "drag_data": {"x": 0, "y": 0},
            "img_pos": [start_x, start_y], 
            "markers": {},  
            "bang_mau_vat_the": {},    
            "layer_visibility": {},    
            "layer_switches": {},
            "layer_scale": {},    
            "layer_order": [],         
            "layer_row_widgets": [],  
            "canvas": canvas,
            "canvas_container": canvas_container,
            "tab_ui": tab_ui,
            "lbl_name": lbl_name,
            "current_img": None
        }

        self.log_to_terminal(f"Opened annotation tab: {tab_name}", "action")
        self.switch_to_tab(tab_name)
        self.show_idle_touchbar()

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
                tab_data["tab_ui"].configure(fg_color=TAB_ACTIVE, border_color="#B07D4C")
                tab_data["lbl_name"].configure(text_color=TEXT_MAIN)
                tab_data["canvas_container"].pack(fill="both", expand=True)
                
                self.lbl_page.configure(text=f"{tab_data['current_page'] + 1:02d} / {tab_data['pdf_doc'].page_count:02d}")
                self.lbl_zoom.configure(text=f"Zoom: {int(tab_data['zoom_level'] * 100)}%")

                if tab_data.get("is_monochrome", False):
                    self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
                else:
                    self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
                
                if tab_data.get("is_monochrome", False):
                    self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
                else:
                    self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
                
                self.build_layer_manager_for_current_page()

                self.render_page(name)
            else:
                tab_data["tab_ui"].configure(fg_color=TAB_INACTIVE, border_color=PANEL_BORDER)
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
        self.log_to_terminal(f"Closed project layer: {tab_name}", "error")

        if not self.tabs:
            self.active_tab_name = None
            self.lbl_page.configure(text="00 / 00")
            self.lbl_zoom.configure(text="Zoom: 200%")
            
            for child in self.layer_frame.winfo_children(): child.destroy()

    def render_page(self, tab_name, redraw_pdf=True):
        data = self.tabs.get(tab_name)
        if not data: return

        if redraw_pdf is False and not (data.get("dragging_table") or data.get("resizing_table")):
            redraw_pdf = True

        canvas = data["canvas"]
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]

        if redraw_pdf:
            page = data["pdf_doc"].load_page(data["current_page"])
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            from PIL import Image, ImageDraw
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if data.get("is_monochrome", False):
                img = img.convert("L").convert("RGB")

            draw = ImageDraw.Draw(img, "RGBA")
            trang_idx = data["current_page"]
            markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
            
            for ma_den, thong_tin in markers_trang_nay.items():
                if not data["layer_visibility"].get(ma_den, True): continue
                mau_hex = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
                scale = data.get("layer_scale", {}).get(ma_den, 1.0) 
                
                for box in thong_tin["toa_do"]:
                    ix0, iy0, ix1, iy1 = box[0]*zoom, box[1]*zoom, box[2]*zoom, box[3]*zoom
                    cx, cy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
                    canh_vuong = 15.0 * zoom * scale
                    nx0, ny0 = cx - canh_vuong / 2, cy - canh_vuong / 2
                    nx1, ny1 = cx + canh_vuong / 2, cy + canh_vuong / 2
                    draw.rectangle([nx0, ny0, nx1, ny1], outline=mau_hex, width=3)

            data["current_img"] = ImageTk.PhotoImage(img) 
            
            # 🚀 FIX CHÍ MẠNG: UPDATE IN-PLACE (THAY RUỘT KHÔNG ĐỔI VỎ)
            # Khóa cứng Z-order, đéo cho Tkinter xóc bài Z-Index nữa!
            if canvas.find_withtag("pdf_background"):
                canvas.itemconfig("pdf_background", image=data["current_img"])
                canvas.coords("pdf_background", pos_x, pos_y)
            else:
                canvas.create_image(pos_x, pos_y, anchor="nw", image=data["current_img"], tags="pdf_background")
                
            self.update_layer_manager_counts()

        canvas.delete("marker") 
        self.draw_table_legend(data)

    # ==========================================
    # 🚀 ENGINE VẼ BẢNG VÀ XỬ LÝ TỌA ĐỘ KỶ LUẬT THÉP
    # ==========================================
    def get_table_hitbox(self, data):
        trang = data["current_page"]
        if "tables" not in data or trang not in data["tables"]: return None
        tb = data["tables"][trang]
        tx = tb["x"] if isinstance(tb, dict) else tb[0]
        ty = tb["y"] if isinstance(tb, dict) else tb[1]
        t_scale = tb.get("scale", 1.0) if isinstance(tb, dict) else 1.0
        
        markers_trang_nay = data.get("markers", {}).get(trang, {})
        active_keys = set(markers_trang_nay.keys())
        danh_sach_ma = [k for k in data.get("layer_order", []) if k in active_keys]
        if not danh_sach_ma: danh_sach_ma = sorted(active_keys) 
        
        w_tb = 230.0 * t_scale
        h_tb = max((len(danh_sach_ma) + 1.8) * 24.0 * t_scale, 60.0 * t_scale)
        return tx, ty, w_tb, h_tb

    def draw_table_legend(self, data):
        canvas = data["canvas"]
        canvas.delete("table_legend")
        
        hitbox = self.get_table_hitbox(data)
        if not hitbox: return
        
        tx_pdf, ty_pdf, w_tb, h_tb = hitbox
        zoom = data["zoom_level"]
        pos_x, pos_y = data["img_pos"]
        
        tx = pos_x + tx_pdf * zoom
        ty = pos_y + ty_pdf * zoom
        w_table = w_tb * zoom
        h_table = h_tb * zoom
        
        trang_idx = data["current_page"]
        t_scale = data["tables"][trang_idx].get("scale", 1.0) if isinstance(data["tables"][trang_idx], dict) else 1.0
        row_h = 24 * zoom * t_scale
        
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        active_keys = set(markers_trang_nay.keys())
        danh_sach_ma = [k for k in data.get("layer_order", []) if k in active_keys]
        if not danh_sach_ma: danh_sach_ma = sorted(active_keys) 
        
        canvas.create_rectangle(tx, ty, tx + w_table, ty + h_table, fill="#1C1510", outline="#B07D4C", width=2, tags="table_legend")
        canvas.create_text(tx + w_table / 2, ty + row_h * 0.7, text="PROMA LEGEND // TOTAL", fill="#F5F2EB", font=("Montserrat Bold", int(11 * zoom * t_scale), "bold"), tags="table_legend")
        canvas.create_line(tx, ty + row_h * 1.3, tx + w_table, ty + row_h * 1.3, fill="#2E241C", width=1, tags="table_legend")
        
        for idx, ma_den in enumerate(danh_sach_ma):
            y_row = ty + (idx + 1.9) * row_h
            mau_sac = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
            so_l = markers_trang_nay.get(ma_den, {}).get("so_luong", 0)
            
            canvas.create_rectangle(tx + 12 * zoom * t_scale, y_row - 6 * zoom * t_scale, tx + 24 * zoom * t_scale, y_row + 6 * zoom * t_scale, fill=mau_sac, outline="#F5F2EB", width=1, tags="table_legend")
            canvas.create_text(tx + 34 * zoom * t_scale, y_row, text=str(ma_den), anchor="w", fill="#F5F2EB", font=("Consolas", int(11 * zoom * t_scale), "bold"), tags="table_legend")
            canvas.create_text(tx + w_table - 15 * zoom * t_scale, y_row, text=f"{so_l:02d}", anchor="e", fill="#B07D4C", font=("Consolas", int(12 * zoom * t_scale), "bold"), tags="table_legend")

        hx, hy = tx + w_table, ty + h_table
        hw = 12 * zoom
        canvas.create_rectangle(hx - hw, hy - hw, hx, hy, fill="#B07D4C", outline="#F5F2EB", width=1, tags="table_legend")
        canvas.create_line(hx - hw + 3, hy - 3, hx - 3, hy - hw + 3, fill="#120C08", width=1.5, tags="table_legend")

        canvas.tag_bind("table_legend", "<Enter>", lambda e: canvas.config(cursor="hand2") if not data.get("resizing_table") else None)
        canvas.tag_bind("table_legend", "<Leave>", lambda e: canvas.config(cursor="") if not (data.get("dragging_table") or data.get("resizing_table")) else None)

        self.enforce_z_order(canvas)

    def enforce_z_order(self, canvas):
        # 🚀 BÙA KỶ LUẬT THÉP: CHỈ DÌM NHỮNG THẰNG Ở ĐÁY XUỐNG
        # Đéo xài tag_raise cho Bảng nữa vì thao tác đó làm Tkinter xóc lộn xộn chữ và nền của Bảng.
        # Chỉ cần dìm Bản vẽ và Lưới xuống đáy cống, cái Bảng nghiễm nhiên bá chủ trên đỉnh!
        canvas.tag_lower("pdf_background")
        canvas.tag_lower("grid")

    # ==========================================
    # KHU VỰC 4: TƯƠNG TÁC CHUỘT (CĂN CHỈNH HITBOX)
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
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]
        px = (event.x - pos_x) / zoom
        py = (event.y - pos_y) / zoom
        trang = data["current_page"]
        
        if getattr(self, "current_action", None) == "ERASE":
            hitbox = self.get_table_hitbox(data)
            if hitbox:
                tx, ty, w_tb, h_tb = hitbox
                if tx <= px <= tx + w_tb and ty <= py <= ty + h_tb:
                    del data["tables"][trang]
                    self.log_to_terminal("🗑️ Đã dùng Tẩy xóa Bảng chú thích bằng Chuột Trái!", "error")
                    self.draw_table_legend(data) 
                    return 

            markers_trang_nay = data.get("markers", {}).get(trang, {})
            for ma_den, thong_tin in markers_trang_nay.items():
                if not data["layer_visibility"].get(ma_den, True): continue
                for i, box in enumerate(thong_tin["toa_do"]):
                    if (box[0] - 8) <= px <= (box[2] + 8) and (box[1] - 8) <= py <= (box[3] + 8):
                        thong_tin["toa_do"].pop(i)
                        thong_tin["so_luong"] -= 1
                        self.log_to_terminal(f"🗑️ Đã xóa 1 điểm của mã [{ma_den}]!", "error")
                        self.update_layer_manager_counts()
                        self.render_page(self.active_tab_name, redraw_pdf=False)
                        return
            return 

        if getattr(self, "current_action", None) == "TABLE":
            if "tables" not in data: data["tables"] = {}
            data["tables"][trang] = {"x": px, "y": py, "scale": 1.0}
            self.draw_table_legend(data)
            self.log_to_terminal("📌 Đã ghim Bảng! Kéo góc dưới-phải để Phóng to/Thu nhỏ.", "success")
            self.finish_table_mode()
            return

        if getattr(self, "current_action", None) == "MARK":
            box = [px - 10, py - 10, px + 10, py + 10]
            ma_den = self.current_mark_layer
            data["markers"][trang][ma_den]["toa_do"].append(box)
            data["markers"][trang][ma_den]["so_luong"] += 1
            self.update_layer_manager_counts()
            self.render_page(self.active_tab_name, redraw_pdf=False)
            return 
            
        if getattr(self, "current_action", None) is None:
            hitbox = self.get_table_hitbox(data)
            if hitbox:
                tx, ty, w_tb, h_tb = hitbox
                # 🚀 FIX HITBOX: Nới rộng 25 pixel bắt góc, chống tuột tay
                if (tx + w_tb - 25) <= px <= (tx + w_tb + 10) and (ty + h_tb - 25) <= py <= (ty + h_tb + 10):
                    data["resizing_table"] = True
                    data["resize_start_tx"] = tx
                    self.log_to_terminal("🔍 Đang kéo đổi kích thước Bảng...", "sys")
                    return
                # Bắt thân bảng để Drag
                if tx - 5 <= px <= tx + w_tb + 5 and ty - 5 <= py <= ty + h_tb + 5:
                    data["dragging_table"] = True
                    data["drag_table_offset"] = [px - tx, py - ty]
                    return

        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            data["canvas"].config(cursor="crosshair")
            data["drag_data"]["start_x"] = event.x
            data["drag_data"]["start_y"] = event.y
            if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
            data["rect_id"] = data["canvas"].create_rectangle(event.x, event.y, event.x, event.y, outline=ACCENT_MAIN, width=2, dash=(4, 4), tags="selection_rect")
        else: 
            data["canvas"].config(cursor="fleur")
            data["drag_data"]["x"] = event.x
            data["drag_data"]["y"] = event.y

    def on_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        if getattr(self, "current_action", None) in ["MARK", "ERASE", "TABLE"]: return
        
        if data.get("resizing_table", False):
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            tx = data["resize_start_tx"]
            new_scale = max(0.4, min(4.0, (px - tx) / 230.0))
            data["tables"][data["current_page"]]["scale"] = new_scale
            self.draw_table_legend(data) 
            return

        if data.get("dragging_table", False):
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            py = (event.y - pos_y) / zoom
            ox, oy = data["drag_table_offset"]
            data["tables"][data["current_page"]]["x"] = px - ox
            data["tables"][data["current_page"]]["y"] = py - oy
            self.draw_table_legend(data) 
            return
        
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            start_x = data["drag_data"]["start_x"]
            start_y = data["drag_data"]["start_y"]
            data["canvas"].coords(data.get("rect_id"), start_x, start_y, event.x, event.y)
        else:
            dx, dy = event.x - data["drag_data"]["x"], event.y - data["drag_data"]["y"]
            data["canvas"].move("pdf_background", dx, dy)
            data["canvas"].move("table_legend", dx, dy)
            data["img_pos"][0] += dx
            data["img_pos"][1] += dy
            data["drag_data"]["x"], data["drag_data"]["y"] = event.x, event.y

    def on_drag_release(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        was_interacting = data.get("dragging_table") or data.get("resizing_table")
        data["dragging_table"] = False
        data["resizing_table"] = False
        
        if getattr(self, "current_action", None) in ["MARK", "ERASE"]: return

        if not hasattr(self, 'area_mode_var') or self.area_mode_var.get() == "Toàn bản vẽ": 
            data["canvas"].config(cursor="")
            return
        
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

    def on_middle_drag_start(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="fleur") 
        data["drag_data"]["mid_x"] = event.x
        data["drag_data"]["mid_y"] = event.y

    def on_middle_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        dx, dy = event.x - data["drag_data"]["mid_x"], event.y - data["drag_data"]["mid_y"]
        data["canvas"].move("pdf_background", dx, dy)
        data["canvas"].move("table_legend", dx, dy)
        data["img_pos"][0] += dx
        data["img_pos"][1] += dy
        data["drag_data"]["mid_x"], data["drag_data"]["mid_y"] = event.x, event.y

    def on_middle_drag_release(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if getattr(self, "current_action", None) == "MARK" or (hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng"):
            data["canvas"].config(cursor="crosshair")
        else:
            data["canvas"].config(cursor="")

    def on_right_click(self, event):
        if not self.active_tab_name: return
        if getattr(self, "current_action", None) == "MARK":
            self.undo_manual_mark()
            return

        data = self.tabs[self.active_tab_name]
        trang = data["current_page"]

        if getattr(self, "current_action", None) == "TABLE":
            if "tables" in data and trang in data["tables"]:
                del data["tables"][trang]
                self.log_to_terminal("🗑️ Đã dùng Chuột phải xóa Bảng chú thích!", "error")
                self.draw_table_legend(data)
            return

        if getattr(self, "current_action", None) == "ERASE":
            return

        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]
        px = (event.x - pos_x) / zoom
        py = (event.y - pos_y) / zoom
        
        markers_trang_nay = data.get("markers", {}).get(trang, {})
        for ma_den, thong_tin in markers_trang_nay.items():
            if not data["layer_visibility"].get(ma_den, True): continue
            for i, box in enumerate(thong_tin["toa_do"]):
                if (box[0] - 8) <= px <= (box[2] + 8) and (box[1] - 8) <= py <= (box[3] + 8):
                    thong_tin["toa_do"].pop(i)
                    thong_tin["so_luong"] -= 1
                    self.log_to_terminal(f"🗑️ Đã xóa 1 điểm chấm của mã [{ma_den}]!", "error")
                    self.update_layer_manager_counts()
                    self.render_page(self.active_tab_name, redraw_pdf=False)
                    return

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
        
        # Cập nhật pos mới
        data["img_pos"] = [mx - (mx - img_x) * zoom_factor, my - (my - img_y) * zoom_factor]
        self.lbl_zoom.configure(text=f"Zoom: {int(data['zoom_level'] * 100)}%")

        # 🚀 FIX CHÍ MẠNG: Dịch chuyển tạm thời Bảng và Bản vẽ CÙNG LÚC để nhìn cho mượt
        dx = data["img_pos"][0] - img_x
        dy = data["img_pos"][1] - img_y
        data["canvas"].move("pdf_background", dx, dy)
        data["canvas"].move("table_legend", dx, dy)

        # 🚀 ĐỢI 150ms THÌ RE-RENDER ĐỒNG LỌAT CẢ BẢN VẼ LẪN BẢNG CÙNG 1 SIZE MỚI!
        if self.zoom_timer: self.after_cancel(self.zoom_timer)
        self.zoom_timer = self.after(150, lambda n=self.active_tab_name: self.render_page(n, redraw_pdf=True))

    def prev_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] > 0:
            data["current_page"] -= 1
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.build_layer_manager_for_current_page()
            self.render_page(self.active_tab_name)

    def next_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] < data["pdf_doc"].page_count - 1:
            data["current_page"] += 1
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.build_layer_manager_for_current_page()
            self.render_page(self.active_tab_name)

    def log_to_terminal(self, text, tag="sys"):
        self.txt_log.configure(state="normal")
        self.txt_log._textbox.insert("end", f">> {text}\n", tag)
        self.txt_log._textbox.see("end")
        self.txt_log.configure(state="disabled")

    # ==========================================
    # KHU VỰC 5: KÍCH HOẠT ĐỘNG CƠ BACKEND 
    # ==========================================
    def run_engine(self):
        if not self.active_tab_name:
            self.log_to_terminal("ERROR: Không có bản vẽ nào được chọn!", "error")
            return
            
        mode = self.mode_var.get()
        data_tab = self.tabs[self.active_tab_name]
        
        tong_so_trang = data_tab["pdf_doc"].page_count
        trang_hien_tai = data_tab["current_page"]
        
        self.log_to_terminal(f"RUNNING MODEL [{mode}] ON PROJECT [{self.active_tab_name}]...", "action")
        self.btn_run.configure(state="disabled", text="PROCESSING...")
        
        vung = None
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            vung = data_tab.get("vung_chon_pdf")
            if not vung:
                self.log_to_terminal("WARN: Chưa vẽ box vùng chọn! Detector quét toàn trang.", "sys")
        
        chu_ky = getattr(self, 'chu_ky_ai', {})
        
        import tempfile
        import time
        temp_path = os.path.join(tempfile.gettempdir(), f"proma_scan_{int(time.time())}.pdf")
        try:
            data_tab["pdf_doc"].save(temp_path)
        except Exception as e:
            self.log_to_terminal(f"LỖI TẠO FILE TẠM (RAM->DISK): {e}", "error")
            self.btn_run.configure(state="normal", text="BREAK GROUND")
            return
        
        threading.Thread(
            target=self._thread_run_engine, 
            args=(temp_path, tong_so_trang, trang_hien_tai, mode, chu_ky, vung),
            daemon=True
        ).start()

    def _thread_run_engine(self, temp_path, tong_so_trang, trang_hien_tai, mode, chu_ky, vung_chon):
        try:
            from client.logic.api_handler import goi_backend_boc_tach
            all_results = {}
            co_loi = False
            loi_msg = ""
            
            for p in range(tong_so_trang):
                vung_cho_trang_nay = vung_chon if p == trang_hien_tai else None
                thanh_cong, ket_qua = goi_backend_boc_tach(temp_path, p, mode, chu_ky, vung_cho_trang_nay)
                
                if thanh_cong:
                    if isinstance(ket_qua, dict) and "error" in ket_qua:
                        co_loi = True
                        loi_msg = ket_qua["error"]
                        break
                    elif isinstance(ket_qua, dict):
                        all_results[p] = ket_qua.get("data", ket_qua) 
                    else:
                        all_results[p] = {}
                else:
                    co_loi = True
                    loi_msg = str(ket_qua)
                    break 
                    
            import os
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass

            if co_loi:
                self.after(0, self._hoan_thanh_run, False, loi_msg)
            else:
                self.after(0, self._hoan_thanh_run, True, all_results)
                
        except Exception as e:
            self.after(0, self._hoan_thanh_run, False, f"THREAD CRASH: {str(e)}")
            
    def _hoan_thanh_run(self, thanh_cong, all_results):
        self.btn_run.configure(state="normal", text="BREAK GROUND")
        if not self.active_tab_name: return
        data_tab = self.tabs[self.active_tab_name]
        
        if thanh_cong:
            has_symbols = any(len(d) > 0 for d in all_results.values() if isinstance(d, dict))
            
            if has_symbols:
                self.log_to_terminal("ANNOTATION SYMBOLS DETECTED. Aligning matrices...", "success")
            else:
                self.log_to_terminal("No target bounding boxes identified.", "sys")
            
            if "markers" not in data_tab: data_tab["markers"] = {}
            
            for p, data_dem in all_results.items():
                if isinstance(data_dem, dict) and data_dem:
                    page = data_tab["pdf_doc"].load_page(p)
                    goc_xoay = page.rotation
                    
                    if goc_xoay != 0:
                        w_goc = page.rect.width if goc_xoay in [0, 180] else page.rect.height
                        h_goc = page.rect.height if goc_xoay in [0, 180] else page.rect.width
                        
                        for ma_den, thong_tin in data_dem.items():
                            toa_do_da_xoay = []
                            for box in thong_tin["toa_do"]:
                                x0, y0, x1, y1 = box[0], box[1], box[2], box[3]
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

                    data_tab["markers"][p] = data_dem
                    
                    for ma_den in data_dem.keys():
                        if ma_den not in data_tab["bang_mau_vat_the"]:
                            mau_moi = self.danh_sach_mau[self.mau_index % len(self.danh_sach_mau)]
                            data_tab["bang_mau_vat_the"][ma_den] = mau_moi
                            self.mau_index += 1
                            data_tab["layer_visibility"][ma_den] = True
                else:
                    data_tab["markers"][p] = {}
            
            self.build_layer_manager_for_current_page() 
            self.render_page(self.active_tab_name)
        else:
            self.log_to_terminal(f"SYSTEM EXCEPTION: {all_results}", "error")

    # ==========================================
    # 🚀 TRẠNG THÁI NGHỈ CỦA TOUCH BAR 
    # ==========================================
    def show_idle_touchbar(self):
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        self.current_action = None
        self.is_insert_menu_open = False
        
        if not hasattr(self, 'touchbar_logo_img') or self.touchbar_logo_img is None:
            try:
                thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
                thu_muc_client = os.path.dirname(thu_muc_hien_tai)
                logo_filename = os.path.join(thu_muc_client, "assets", "Proma Logo 1.png")
                
                img_goc = Image.open(logo_filename).convert("RGBA")
                w_goc, h_goc = img_goc.size
                
                w_mini = int(w_goc * (20 / h_goc))
                img_resized = img_goc.resize((w_mini, 20), Image.Resampling.LANCZOS)
                
                img_tinted = Image.new("RGBA", (w_mini, 20), (176, 125, 76, 170))
                img_final = Image.new("RGBA", (w_mini, 20), (0, 0, 0, 0))
                img_final.paste(img_tinted, (0, 0), mask=img_resized.split()[3]) 
                
                self.touchbar_logo_img = ctk.CTkImage(light_image=img_final, dark_image=img_final, size=(w_mini, 20))
            except Exception as e:
                self.log_to_terminal(f"Lỗi load logo Touch Bar: {e}", "error")
                return
        
        if self.touchbar_logo_img:
            ctk.CTkLabel(self.touch_bar, text="", image=self.touchbar_logo_img).pack(expand=True)
        
    def toggle_touchbar_insert(self):
        if not self.active_tab_name:
            self.log_to_terminal("Sếp phải mở bản vẽ ra mới xài Insert được chứ!", "error")
            return
            
        if getattr(self, "is_insert_menu_open", False):
            self.show_idle_touchbar()
            self.log_to_terminal("HUD menu closed.", "sys")
            return

        self.is_insert_menu_open = True
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        self.current_action = None

        # 🚀 Bo góc mềm 6px cho Touchbar Buttons
        btn_mark = ctk.CTkButton(
            self.touch_bar, text="MARK", width=74, height=24, corner_radius=6, 
            fg_color="#D5B07C", text_color=BG_DARK, hover_color="#C49A6C", 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color="#E8C695",
            command=self.start_manual_mark
        )
        btn_mark.pack(side="left", padx=(14, 4), pady=4)

        btn_erase = ctk.CTkButton(
            self.touch_bar, text="ERASE", width=74, height=24, corner_radius=6, 
            fg_color="#E05B48", text_color="#FFFFFF", hover_color="#C94A38", 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color="#E05B48",
            command=self.start_erase_mode
        )
        btn_erase.pack(side="left", padx=4, pady=4)

        btn_table = ctk.CTkButton(
            self.touch_bar, text="TABLE", width=74, height=24, corner_radius=6, 
            fg_color="#2A9D8F", text_color="#FFFFFF", hover_color="#218277", 
            font=("Montserrat Bold", 11, "bold"), border_width=1, border_color="#2A9D8F",
            command=self.start_table_mode
        )
        btn_table.pack(side="left", padx=4, pady=4)

    # ==========================================
    # 🚀 TÍNH NĂNG INSERT: MARK THỦ CÔNG & TẤY (ERASE)
    # ==========================================
    def start_manual_mark(self):
        if not self.active_tab_name: return
        
        dialog = ctk.CTkInputDialog(text="Nhập mã Annotation Layer (VD: MARK-01):", title="New Annotation Layer")
        layer_name = dialog.get_input()
        
        if not layer_name: 
            self.log_to_terminal("Manual annotation aborted.", "sys")
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

        for widget in self.touch_bar.winfo_children(): widget.destroy()

        ctk.CTkLabel(
            self.touch_bar, text=f"MARKING: [ {layer_name} ]", 
            font=("Montserrat Bold", 12, "bold"), text_color=ACCENT_MAIN
        ).pack(side="left", padx=16)
        
        ctk.CTkLabel(
            self.touch_bar, text="CTRL+Z: Undo  |  ENTER / ESC: Complete", 
            font=("Consolas", 11, "bold"), text_color=TEXT_MUTED
        ).pack(side="left", padx=10)

        self.bind("<Control-z>", self.undo_manual_mark)
        self.bind("<Return>", self.finish_manual_mark)
        self.bind("<Escape>", self.finish_manual_mark)
        data["canvas"].bind("<Return>", self.finish_manual_mark)
        data["canvas"].bind("<Escape>", self.finish_manual_mark)
        
        data["canvas"].focus_set()
        self.log_to_terminal(f"Annotation gun armed for layer '{layer_name}'. Press ENTER to commit.", "action")

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
            self.log_to_terminal(f"↩ Annotation coordinate removed from '{ma_den}'.", "sys")

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
        self.log_to_terminal("Manual annotation finalized.", "success")
        self.is_insert_menu_open = False
        self.toggle_touchbar_insert()

    def start_erase_mode(self):
        if not self.active_tab_name: return
        self.current_action = "ERASE"
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="X_cursor") 
        
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(
            self.touch_bar, text="ERASING: Click target bounding box or table to purge", 
            font=("Montserrat Bold", 12, "bold"), text_color="#E05B48"
        ).pack(side="left", padx=16)
        
        ctk.CTkLabel(
            self.touch_bar, text="ENTER / ESC: Exit", 
            font=("Consolas", 11, "bold"), text_color=TEXT_MUTED
        ).pack(side="left", padx=10)
        
        self.bind("<Return>", self.finish_erase_mode)
        self.bind("<Escape>", self.finish_erase_mode)
        data["canvas"].bind("<Return>", self.finish_erase_mode)
        data["canvas"].bind("<Escape>", self.finish_erase_mode)
        
        data["canvas"].focus_set()
        self.log_to_terminal("Eraser mode armed.", "action")

    def finish_erase_mode(self, event=None):
        self.current_action = None
        if self.active_tab_name:
            data = self.tabs[self.active_tab_name]
            data["canvas"].config(cursor="")
            data["canvas"].unbind("<Return>")
            data["canvas"].unbind("<Escape>")
            
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self.log_to_terminal("Eraser disarmed.", "success")
        self.is_insert_menu_open = False
        self.toggle_touchbar_insert()

    # ==========================================
    # 🚀 CHẾ ĐỘ TABLE 
    # ==========================================
    def start_table_mode(self):
        if not self.active_tab_name: return
        self.current_action = "TABLE"
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="plus") 
        
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(
            self.touch_bar, text="TABLE PLACEMENT: Click canvas to deploy legend", 
            font=("Montserrat Bold", 12, "bold"), text_color="#2A9D8F"
        ).pack(side="left", padx=16)
        
        ctk.CTkLabel(
            self.touch_bar, text="Left: Place/Move/Resize  |  Right/Erase: Purge", 
            font=("Consolas", 11, "bold"), text_color=TEXT_MUTED
        ).pack(side="left", padx=10)
        
        self.bind("<Control-z>", self.undo_table)
        self.bind("<Return>", self.finish_table_mode)
        self.bind("<Escape>", self.finish_table_mode)
        data["canvas"].bind("<Control-z>", self.undo_table)
        data["canvas"].bind("<Return>", self.finish_table_mode)
        data["canvas"].bind("<Escape>", self.finish_table_mode)
        
        data["canvas"].focus_set()
        self.log_to_terminal("Table placement cursor ready.", "action")

    def undo_table(self, event=None):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        trang = data["current_page"]
        if "tables" in data and trang in data["tables"]:
            del data["tables"][trang]
            self.log_to_terminal("↩ Table placement reverted.", "sys")
            self.render_page(self.active_tab_name, redraw_pdf=False)

    def finish_table_mode(self, event=None):
        self.current_action = None
        if self.active_tab_name:
            data = self.tabs[self.active_tab_name]
            data["canvas"].config(cursor="")
            data["canvas"].unbind("<Control-z>")
            data["canvas"].unbind("<Return>")
            data["canvas"].unbind("<Escape>")
            
        self.unbind("<Control-z>")
        self.unbind("<Return>")
        self.unbind("<Escape>")
        self.log_to_terminal("Legend table coordinates locked.", "success")
        self.is_insert_menu_open = False
        self.toggle_touchbar_insert()

    def rotate_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        doc = data["pdf_doc"]
        page_idx = data["current_page"]
        page = doc.load_page(page_idx)
        
        old_h = page.rect.height
        page.set_rotation((page.rotation + 90) % 360)
        
        data["vung_chon_pdf"] = None
        if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
        
        if page_idx in data.get("markers", {}):
            for ma_den, thong_tin in data["markers"][page_idx].items():
                toa_do_moi = []
                for box in thong_tin["toa_do"]:
                    x0, y0, x1, y1 = box[0], box[1], box[2], box[3]
                    nx0 = old_h - y1
                    ny0 = x0
                    nx1 = old_h - y0
                    ny1 = x1
                    toa_do_moi.append([nx0, ny0, nx1, ny1])
                thong_tin["toa_do"] = toa_do_moi
        
        self.render_page(self.active_tab_name, redraw_pdf=True)
        self.log_to_terminal("Page rotated 90° clockwise. Coordinates transformed.", "action")

    def toggle_monochrome(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        data["is_monochrome"] = not data.get("is_monochrome", False)
        
        if data["is_monochrome"]:
            self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
            self.log_to_terminal("◐ Monochrome background filter activated.", "action")
        else:
            self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
            self.log_to_terminal("◐ Original blueprint color scheme restored.", "sys")
            
        self.render_page(self.active_tab_name, redraw_pdf=True)

    # ==========================================
    # KHU VỰC 6: XUẤT BẢN VẼ (RAM-BASED EXPORT & SCOPING)
    # ==========================================
    def export_markup_pdf(self):
        if not self.active_tab_name:
            self.log_to_terminal("ERROR: Có bản vẽ nào đâu mà xuất sếp ơi!", "error")
            return
            
        data_tab = self.tabs[self.active_tab_name]
        
        # 🚀 Bo góc 12px cho Popup
        popup = ctk.CTkToplevel(self)
        popup.title("Export Scope")
        popup.geometry("480x220")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="Select Export Range", font=("Montserrat Bold", 15, "bold"), text_color=ACCENT_MAIN).pack(pady=(25, 10))
        ctk.CTkLabel(popup, text="Export the entire project document or only the current active page?", font=("Montserrat", 12), text_color=TEXT_MUTED).pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        def do_export(scope):
            popup.destroy()
            file_luu = fd.asksaveasfilename(
                title="Select Output Directory for Annotation PDF", defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")], initialfile=f"Takeoff_Export_{self.active_tab_name}"
            )
            if not file_luu:
                self.log_to_terminal("Export procedure canceled.", "sys")
                return
                
            self.log_to_terminal(f"Generating PDF ({scope} MODE) with burned-in annotations... PLEASE WAIT!", "action")
            
            markers_data = data_tab.get("markers", {}) 
            bang_mau = data_tab.get("bang_mau_vat_the", {})
            visibility = data_tab.get("layer_visibility", {})
            scales = data_tab.get("layer_scale", {})
            tables_data = data_tab.get("tables", {})
            is_mono = data_tab.get("is_monochrome", False)
            current_page_idx = data_tab["current_page"]
            
            goc_xoay = {i: data_tab["pdf_doc"].load_page(i).rotation for i in range(data_tab["pdf_doc"].page_count)}
            pdf_bytes = data_tab["pdf_doc"].tobytes()
            
            threading.Thread(
                target=self._thread_export_pdf, 
                args=(pdf_bytes, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay, tables_data, is_mono, scope, current_page_idx), 
                daemon=True
            ).start()

        # 🚀 Nút bấm bo góc 8px
        ctk.CTkButton(
            btn_frame, text="Current Page Only", height=42, corner_radius=8, 
            font=("Montserrat Bold", 12, "bold"), fg_color=PANEL_BG, hover_color=TAB_HOVER, 
            border_width=1, border_color=ACCENT_MAIN, text_color=ACCENT_MAIN, 
            command=lambda: do_export("CURRENT")
        ).pack(side="left", expand=True, fill="x", padx=6)
        
        ctk.CTkButton(
            btn_frame, text="All Project Pages", height=42, corner_radius=8, 
            font=("Montserrat Bold", 12, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, 
            text_color=BG_DARK, border_width=1, border_color="#D19E6E", 
            command=lambda: do_export("ALL")
        ).pack(side="right", expand=True, fill="x", padx=6)

    def _thread_export_pdf(self, pdf_bytes, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay, tables_data, is_mono, scope, current_page_idx):
        try:
            import fitz
            pdf_copy = fitz.open("pdf", pdf_bytes)
            tong_o_ve = 0
            tong_bang_ve = 0

            if scope == "CURRENT":
                pdf_copy.select([current_page_idx]) 
                trang_map = {current_page_idx: 0}   
            else:
                trang_map = {i: i for i in range(pdf_copy.page_count)}
            
            for trang_cu, trang_moi in trang_map.items():
                page = pdf_copy.load_page(trang_moi)
                
                if page.rotation != goc_xoay.get(trang_cu, 0):
                    page.set_rotation(goc_xoay.get(trang_cu, 0))
            
                if is_mono:
                    mat_mono = fitz.Matrix(2.0, 2.0)
                    pix_mono = page.get_pixmap(matrix=mat_mono, colorspace=fitz.csGRAY)
                    rect_page = page.rect
                    page.clean_contents()
                    page.insert_image(rect_page, pixmap=pix_mono)
                
                layers = markers_data.get(trang_cu, {}) 
                
                # A. VẼ BOUNDING BOX MARKERS
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

                # B. VẼ BẢNG CHÚ THÍCH
                if trang_cu in tables_data:
                    tb = tables_data[trang_cu]
                    tx = tb["x"] if isinstance(tb, dict) else tb[0]
                    ty = tb["y"] if isinstance(tb, dict) else tb[1]
                    t_scale = tb.get("scale", 1.0) if isinstance(tb, dict) else 1.0
                    
                    data_tab = self.tabs[self.active_tab_name]
                    active_keys = set(layers.keys())
                    danh_sach_ma = [k for k in data_tab.get("layer_order", []) if k in active_keys]
                    if not danh_sach_ma: danh_sach_ma = sorted(active_keys)
                    w_table = 180.0 * t_scale
                    row_h = 18.0 * t_scale
                    h_table = max((len(danh_sach_ma) + 1.8) * row_h, 45.0 * t_scale)
                    
                    rgb_vien = (0.69, 0.49, 0.30)       
                    rgb_nen = (0.11, 0.08, 0.06)        
                    rgb_chu_trang = (0.96, 0.95, 0.92)  
                    rgb_chu_vang = (0.85, 0.55, 0.28)   
                    
                    shape_table = page.new_shape()
                    
                    rect_table = fitz.Rect(tx, ty, tx + w_table, ty + h_table)
                    shape_table.draw_rect(rect_table)
                    shape_table.finish(color=rgb_vien, fill=rgb_nen, width=1.5 * t_scale)
                    
                    shape_table.draw_line(
                        fitz.Point(tx, ty + row_h * 1.3), 
                        fitz.Point(tx + w_table, ty + row_h * 1.3)
                    )
                    shape_table.finish(color=(0.18, 0.14, 0.11), width=0.5 * t_scale)
                    
                    for idx, ma_den in enumerate(danh_sach_ma):
                        y_row = ty + (idx + 1.9) * row_h
                        mau_hex = bang_mau[ma_den]
                        rgb_layer = tuple(int(mau_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
                        
                        r_color = fitz.Rect(tx + 10 * t_scale, y_row - 4 * t_scale, tx + 18 * t_scale, y_row + 4 * t_scale)
                        shape_table.draw_rect(r_color)
                        shape_table.finish(color=(1, 1, 1), fill=rgb_layer, width=0.5 * t_scale)
                        
                    shape_table.commit()
                    
                    font_size_title = int(8 * t_scale)
                    font_size_row = int(9 * t_scale)
                    
                    page.insert_text(
                        fitz.Point(tx + w_table / 2 - (45 * t_scale), ty + row_h * 0.85), 
                        "PROMA LEGEND // TOTAL", 
                        fontsize=font_size_title, color=rgb_chu_trang
                    )
                    
                    for idx, ma_den in enumerate(danh_sach_ma):
                        y_row = ty + (idx + 1.9) * row_h
                        so_l = layers.get(ma_den, {}).get("so_luong", 0)
                        
                        page.insert_text(
                            fitz.Point(tx + 25 * t_scale, y_row + 3 * t_scale), 
                            str(ma_den), 
                            fontsize=font_size_row, color=rgb_chu_trang
                        )
                        page.insert_text(
                            fitz.Point(tx + w_table - (25 * t_scale), y_row + 3 * t_scale), 
                            f"{so_l:02d}", 
                            fontsize=font_size_row, color=rgb_chu_vang
                        )
                    
                    tong_bang_ve += 1
                        
            pdf_copy.save(file_luu, deflate=True, garbage=4)
            pdf_copy.close()
            
            self.after(0, self._hoan_thanh_export, True, file_luu, tong_o_ve, tong_bang_ve, "")
        except Exception as e:
            self.after(0, self._hoan_thanh_export, False, "", 0, 0, str(e))

    def _hoan_thanh_export(self, thanh_cong, file_luu, tong_o_ve, tong_bang_ve, loi):
        if thanh_cong:
            self.log_to_terminal(f"✅ EXPORT COMPLETE // {tong_o_ve} marks & {tong_bang_ve} tables stamped.", "success")
            self.log_to_terminal(f"Saved at: {file_luu}", "sys")
        else:
            self.log_to_terminal(f"❌ EXPORT ENGINE ERROR: {loi}", "error")


    # ==========================================
    # KHU VỰC 5.1: DẠY HỌC MINH BẠCH - HIỆN POPUP XÁC NHẬN
    # ==========================================
    def train_legend_action(self):
        file_bang = fd.askopenfilename(title="Select Legend PDF Reference", filetypes=[("PDF", "*.pdf")])
        if not file_bang: return
        
        dialog = ctk.CTkInputDialog(text="Enter 1-based page number containing target legend:", title="Legend Reference Page")
        trang_str = dialog.get_input()
        try:
            trang_so = int(trang_str) - 1 
            if trang_so < 0: raise ValueError
        except:
            self.log_to_terminal("ERROR: Invalid target page index provided.", "error")
            return

        self.log_to_terminal(f"Analyzing target legend geometry on page {trang_so + 1}... Please stand by.", "action")
        threading.Thread(target=self._thread_train_legend, args=(file_bang, trang_so), daemon=True).start()

    def _thread_train_legend(self, filepath, page_idx):
        from client.logic.api_handler import goi_backend_hoc_ky_hieu
        thanh_cong, ket_qua = goi_backend_hoc_ky_hieu(filepath, page_idx)
        self.after(0, self._hoan_thanh_train, thanh_cong, ket_qua)
        
    def _hoan_thanh_train(self, thanh_cong, ket_qua):
        if thanh_cong and ket_qua.get("data"):
            self.log_to_terminal("Training signatures captured. Awaiting user verification...", "action")
            self.hien_thi_popup_xac_minh(ket_qua["data"])
        else:
            self.log_to_terminal(f"❌ SYMBOL TRAINING FAULT: {ket_qua.get('error', 'Unknown exception')}", "error")

    def hien_thi_popup_xac_minh(self, du_lieu_hoc_duoc):
        # 🚀 CỬA SỔ POPUP XÁC MINH (APPLE PRO AESTHETIC)
        popup = ctk.CTkToplevel(self)
        popup.title("Symbol Signature Verification")
        popup.geometry("480x560")
        popup.attributes("-topmost", True) 
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="Identified Legend Signatures", font=("Montserrat Bold", 16, "bold"), text_color=ACCENT_MAIN).pack(pady=(25, 6))
        ctk.CTkLabel(popup, text="Verify bounding box dimensions [w x h] before committing.", font=("Montserrat", 12), text_color=TEXT_MUTED).pack(pady=(0, 14))

        # 🚀 Bo góc 8px cho khung Scroll danh sách mã
        scroll = ctk.CTkScrollableFrame(
            popup, width=410, height=360, 
            fg_color=PANEL_BG, corner_radius=8, border_width=1, border_color=PANEL_BORDER
        )
        scroll.pack(pady=10, padx=20, fill="both", expand=True)

        for ma, thong_so in du_lieu_hoc_duoc.items():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=f"LAYER // {ma}", font=("Consolas", 13, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"BOX [ W: {thong_so['w']} | H: {thong_so['h']} ]", font=("Consolas", 12), text_color=TEXT_MUTED).pack(side="right", padx=10)

        def xac_nhan_luu():
            if not hasattr(self, 'chu_ky_ai'): self.chu_ky_ai = {}
            self.chu_ky_ai.update(du_lieu_hoc_duoc)
            self.log_to_terminal(f"✅ Model signatures validated and committed to active pipeline.", "success")
            popup.destroy()

        # 🚀 Nút xác nhận bo góc 8px mượt mà
        ctk.CTkButton(
            popup, text="Confirm Signatures", height=46, corner_radius=8,
            font=("Montserrat Bold", 13, "bold"), fg_color=ACCENT_MAIN, 
            hover_color=ACCENT_HOVER, text_color=BG_DARK, 
            border_width=1, border_color="#D19E6E",
            command=xac_nhan_luu
        ).pack(pady=(12, 20), padx=20, fill="x")
