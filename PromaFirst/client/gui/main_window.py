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
# 🚀 CẤU HÌNH PALETTE "SCALE AI // PROMA OBSIDIAN"
# ==========================================
ctk.set_appearance_mode("dark")

# Nền đen Obsidian & Xám Zinc chuẩn Scale AI / Palantir
BG_DARK = "#120C08"          # Đen sâu tuyệt đối (Obsidian Black)
PANEL_BG = "#121215"         # Xám nhám kim loại technical
PANEL_BORDER = "#27272A"     # Viền lưới độ chính xác cao 1px (Zinc 800)

# Màu Nâu Vàng PROMA Amber Bronze (AI Laser Glow)
ACCENT_MAIN = "#B07D4C"      # Nâu vàng kim loại đặc trưng
ACCENT_HOVER = "#D98B48"     # Hover rực sáng amber
ACCENT_MUTED = "#452A14"     # Nâu trầm technical

# Typography kỹ thuật số
TEXT_MAIN = "#FAFAFA"        # Trắng tinh khiết Zinc 50
TEXT_MUTED = "#71717A"       # Xám kỹ thuật Zinc 500
GRID_COLOR = "#18181B"       # Lưới bản vẽ ngầm Zinc 900

# Trạng thái Workspace
TAB_ACTIVE = "#18181B"       
TAB_INACTIVE = "#09090B"     
TAB_HOVER = "#27272A"        
CLOSE_BTN_HOVER = "#EF4444"  

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
    # KHU VỰC 1: SPLASH SCREEN (SCALE AI FOUNDRY BOOT STYLE)
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

        # Badge Version kỹ thuật số chuẩn Scale AI

        ctk.CTkLabel(self.splash_frame, text="PROMA.", font=("EB Garamond ExtraBold", 54, "bold"), text_color=TEXT_MAIN).pack(pady=(0, 4))
        ctk.CTkLabel(self.splash_frame, text="The smarter way to manage construction projects.", font=("EB Garamond", 20), text_color=TEXT_MUTED).pack(pady=(0, 45))

        # Nút bấm góc nhọn 4px chuẩn precision engineering tool
        ctk.CTkButton(
            self.splash_frame, text="UPLOAD PROJECT (.PDF)", height=48, width=280, 
            corner_radius=4, font=("Consolas", 16, "bold"),
            fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, text_color=BG_DARK,
            border_width=1, border_color="#E6A86E",
            command=self.open_first_pdf
        ).pack()

    def open_first_pdf(self):
        filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
        if not filepath: return
        self.splash_frame.pack_forget()
        self.build_workspace()
        self.add_new_tab(filepath)

    def open_additional_pdf(self):
        # Nếu chưa mở Project nào thì mặc định mở New Project luôn, đéo cần hỏi
        if not self.active_tab_name: 
            filepath = fd.askopenfilename(title="Select Blueprint", filetypes=[("Bản vẽ PDF", "*.pdf")])
            if filepath: self.add_new_tab(filepath)
            return

        # 🚀 HUD POPUP: HỎI SẾP MUỐN GỘP VÀO PROJECT HAY TẠO TAB MỚI
        popup = ctk.CTkToplevel(self)
        popup.title("PROJECT WORKSPACE // PROMA")
        popup.geometry("480x220")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="// OPEN MODE SELECTION", font=("Consolas", 15, "bold"), text_color=ACCENT_MAIN).pack(pady=(25, 10))
        ctk.CTkLabel(popup, text="Select how you want to load the new blueprint into the workspace.", font=("Consolas", 11), text_color=TEXT_MUTED).pack(pady=(0, 15))

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
            btn_frame, text="[ + APPEND TO PROJECT ]", height=42, corner_radius=4, 
            font=("Consolas", 12, "bold"), fg_color=PANEL_BG, hover_color=TAB_HOVER, 
            border_width=1, border_color=ACCENT_MAIN, text_color=ACCENT_MAIN, 
            command=add_to_current
        ).pack(side="left", expand=True, fill="x", padx=6)
        
        ctk.CTkButton(
            btn_frame, text="[ NEW PROJECT TAB ]", height=42, corner_radius=4, 
            font=("Consolas", 12, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, 
            text_color=BG_DARK, border_width=1, border_color="#E6A86E", 
            command=create_new
        ).pack(side="right", expand=True, fill="x", padx=6)

    # 🚀 ĐỘNG CƠ GỘP BẢN VẼ BẰNG FITZ VECTOR
    def merge_pdf_to_current_project(self, filepath):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        try:
            doc_moi = fitz.open(filepath)
            # Lệnh sát thủ: Nhét toàn bộ file mới vào đít file hiện tại
            data["pdf_doc"].insert_pdf(doc_moi)
            doc_moi.close()
            
            # Đồng bộ lại số trang trên UI
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.log_to_terminal(f"APPENDED: {os.path.basename(filepath)} added. Total project pages: {data['pdf_doc'].page_count}", "success")
        except Exception as e:
            self.log_to_terminal(f"MERGE ENGINE EXCEPTION: {e}", "error")

    # ==========================================
    # KHU VỰC 2: WORKSPACE (SCALE AI ANNOTATION STUDIO)
    # ==========================================
    def build_workspace(self):
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0) 

        # ==========================================
        # 🚀 TOP HUD TOOLBAR (PRECISION ZINC 800 BORDERS)
        # ==========================================
        self.top_toolbar = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color=BG_DARK)
        self.top_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_toolbar.pack_propagate(False) 

        # --- [TRÁI] BRAND & CORE TOOLS ---
        self.toolbar_left = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_left.pack(side="left", fill="y", padx=(18, 8))

        ctk.CTkLabel(self.toolbar_left, text="P.", font=("Montserrat Bold", 25, "bold"), text_color=ACCENT_MAIN).pack(side="left", padx=(0, 16))

        ctk.CTkButton(
            self.toolbar_left, text="OPEN", width=64, height=28, corner_radius=4, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Consolas", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.open_additional_pdf
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            self.toolbar_left, text="EXPORT", width=70, height=28, corner_radius=4, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Consolas", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.export_markup_pdf
        ).pack(side="left", padx=3)
        
        self.btn_insert = ctk.CTkButton(
            self.toolbar_left, text="+ INSERT", width=84, height=28, corner_radius=4, 
            fg_color=ACCENT_MAIN, text_color=BG_DARK, hover_color=ACCENT_HOVER, 
            font=("Consolas", 11, "bold"), border_width=1, border_color="#E6A86E",
            command=self.toggle_touchbar_insert
        )
        self.btn_insert.pack(side="left", padx=(6, 3))

        # --- [GIỮA] TELEMETRY TOUCH BAR (BẢNG ĐIỀU KHIỂN HUD 4PX) ---
        self.touch_bar = ctk.CTkFrame(
            self.top_toolbar, height=32, corner_radius=4, 
            fg_color="#0E0E11", border_width=1, border_color=PANEL_BORDER
        )
        self.touch_bar.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        self.touch_bar.pack_propagate(False)

        # --- [PHẢI] DISPLAY CONTROLS & NAV ---
        self.toolbar_right = ctk.CTkFrame(self.top_toolbar, fg_color="transparent")
        self.toolbar_right.pack(side="right", fill="y", padx=(8, 18))

        ctk.CTkButton(
            self.toolbar_right, text="⟳ ROTATE", width=74, height=28, corner_radius=4, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Consolas", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.rotate_page
        ).pack(side="left", padx=3)

        self.btn_mono = ctk.CTkButton(
            self.toolbar_right, text="◐ MONO", width=68, height=28, corner_radius=4, 
            fg_color=PANEL_BG, text_color=TEXT_MAIN, hover_color=TAB_HOVER, 
            font=("Consolas", 11, "bold"), border_width=1, border_color=PANEL_BORDER,
            command=self.toggle_monochrome
        )
        self.btn_mono.pack(side="left", padx=(3, 14))

        # Pager Controls kỹ thuật
        self.nav_frame = ctk.CTkFrame(self.toolbar_right, fg_color="transparent")
        self.nav_frame.pack(side="left", pady=10)
        
        ctk.CTkButton(
            self.nav_frame, text="❮", width=24, height=24, corner_radius=4, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=TAB_HOVER, 
            font=("Consolas", 12, "bold"), command=self.prev_page
        ).pack(side="left", padx=1)
        
        self.lbl_page = ctk.CTkLabel(
            self.nav_frame, text="00 / 00", 
            font=("Consolas", 12, "bold"), text_color=TEXT_MAIN
        )
        self.lbl_page.pack(side="left", padx=8)
        
        ctk.CTkButton(
            self.nav_frame, text="❯", width=24, height=24, corner_radius=4, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=TAB_HOVER, 
            font=("Consolas", 12, "bold"), command=self.next_page
        ).pack(side="left", padx=1)

        # Đường viền ngăn cách sắc nét
        ctk.CTkFrame(self, height=1, corner_radius=0, fg_color=PANEL_BORDER).grid(row=0, column=0, columnspan=2, sticky="sew")

        # --- CENTER ANNOTATION AREA ---
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 14))
        self.center_frame.pack_propagate(False)

        # Tab bar thanh mảnh
        self.custom_tab_bar = ctk.CTkScrollableFrame(
            self.center_frame, height=38, orientation="horizontal", 
            fg_color="transparent", bg_color="transparent"
        )
        self.custom_tab_bar.pack(side="top", fill="x", pady=(0, 6))
        self.custom_tab_bar._scrollbar.configure(width=0) 

        # Khung Canvas góc vuông 4px precision engineering
        self.canvas_area = ctk.CTkFrame(
            self.center_frame, corner_radius=4, 
            fg_color=BG_DARK, border_width=1, border_color=PANEL_BORDER
        )
        self.canvas_area.pack(side="top", fill="both", expand=True)

        # --- RIGHT PANEL (SCALE AI ENGINE CONTROL) ---
        self.right_panel = ctk.CTkFrame(self, width=330, corner_radius=0, fg_color=PANEL_BG)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_propagate(False)

        ctk.CTkLabel(
            self.right_panel, text="MODE", 
            font=("Consolas", 15, "bold"), text_color=ACCENT_MAIN
        ).pack(anchor="w", padx=20, pady=(20, 6))

        self.mode_var = ctk.StringVar(value="Vật thể")
        self.mode_selector = ctk.CTkSegmentedButton(
            self.right_panel, values=["Vật thể", "Đường ống", "Diện tích"], variable=self.mode_var, 
            selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, 
            text_color=TEXT_MAIN, font=("Montserrat Bold", 11, "bold"), corner_radius=4
        )
        self.mode_selector.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(
            self.right_panel, text="REGION", 
            font=("Consolas", 15, "bold"), text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(16, 6))
        
        self.area_mode_var = ctk.StringVar(value="Toàn bản vẽ")
        self.area_selector = ctk.CTkSegmentedButton(
            self.right_panel, values=["Toàn bản vẽ", "Kéo chọn vùng"], variable=self.area_mode_var,
            selected_color=ACCENT_MAIN, selected_hover_color=ACCENT_HOVER, unselected_color=BG_DARK, 
            text_color=TEXT_MAIN, font=("Montserrat Bold", 11, "bold"), corner_radius=4
        )
        self.area_selector.pack(fill="x", padx=20, pady=(0, 12))

        self.btn_learn_legend = ctk.CTkButton(
            self.right_panel, text="[ 📖 Learn Symbols ]", height=38, corner_radius=4, 
            font=("Consolas", 12, "bold"), fg_color="#18181B", hover_color="#27272A", 
            text_color=ACCENT_MAIN, border_width=1, border_color=ACCENT_MAIN,
            command=self.train_legend_action
        )
        self.btn_learn_legend.pack(fill="x", padx=20, pady=(4, 6))

        self.btn_run = ctk.CTkButton(
            self.right_panel, text="BREAK GROUND", height=46, corner_radius=4, 
            font=("Consolas", 14, "bold"), fg_color=ACCENT_MAIN, 
            hover_color=ACCENT_HOVER, text_color=BG_DARK, 
            border_width=1, border_color="#E6A86E",
            command=self.run_engine
        )
        self.btn_run.pack(fill="x", padx=20, pady=(8, 16))
        
        self.master_switch_var = ctk.BooleanVar(value=True)
        self.master_switch = ctk.CTkSwitch(
            self.right_panel, text="LAYERS", font=("Consolas", 11, "bold"), 
            text_color=TEXT_MAIN, progress_color=ACCENT_MAIN, 
            variable=self.master_switch_var, command=self.toggle_all_layers
        )
        self.master_switch.pack(anchor="w", padx=20, pady=(0, 10))

        self.layer_frame = ctk.CTkScrollableFrame(
            self.right_panel, fg_color=BG_DARK, height=340, 
            corner_radius=4, border_width=1, border_color=PANEL_BORDER
        )
        self.layer_frame.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(
            self.right_panel, text="// TELEMETRY CLI LOG", 
            font=("Consolas", 11, "bold"), text_color=TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 6))
        
        self.txt_log = ctk.CTkTextbox(
            self.right_panel, fg_color=BG_DARK, text_color=TEXT_MAIN, 
            font=("Consolas", 11), corner_radius=4, height=115,
            border_width=1, border_color=PANEL_BORDER
        )
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.txt_log.configure(state="disabled")

        self.txt_log._textbox.tag_configure("sys", foreground=TEXT_MUTED)
        self.txt_log._textbox.tag_configure("success", foreground="#34D399") # Green AI signal
        self.txt_log._textbox.tag_configure("error", foreground=CLOSE_BTN_HOVER)
        self.txt_log._textbox.tag_configure("action", foreground=ACCENT_MAIN)

        # Status Bar siêu gọn góc trái-phải
        self.statusbar = ctk.CTkFrame(self.center_frame, height=28, corner_radius=4, fg_color=PANEL_BG)
        self.statusbar.pack(side="bottom", fill="x")

        self.lbl_coords = ctk.CTkLabel(self.statusbar, text="COORD // X: 0000 | Y: 0000", font=("Consolas", 11, "bold"), text_color=TEXT_MUTED)
        self.lbl_coords.pack(side="left", padx=14)

        self.lbl_zoom = ctk.CTkLabel(self.statusbar, text="ZOOM // 200%", font=("Consolas", 11, "bold"), text_color=TEXT_MUTED)
        self.lbl_zoom.pack(side="right", padx=14)

        self.log_to_terminal("SCALE AI ANNOTATION ENGINE INITIALIZED.", "sys")

    # ==========================================
    # KHU VỰC 3: LAYER MANAGER ROWS
    # ==========================================

    # 🚀 HÀM MỚI: CHỈ HIỆN LAYER CỦA TRANG HIỆN TẠI
    def build_layer_manager_for_current_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        # Dọn sạch Panel rác của trang cũ
        for child in self.layer_frame.winfo_children():
            child.destroy()
            
        data["layer_switches"] = {}
        
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        # Chỉ lôi ra những mã CÓ MẶT trên trang hiện tại
        for ma_den in sorted(markers_trang_nay.keys()):
            mau_sac = data["bang_mau_vat_the"].get(ma_den, "#FFFFFF")
            so_l = markers_trang_nay[ma_den].get("so_luong", 0)
            self.add_layer_toggle_ui(ma_den, mau_sac, so_l)

    def add_layer_toggle_ui(self, ma_den, mau_sac, so_luong=0):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]

        row = ctk.CTkFrame(self.layer_frame, fg_color="transparent")
        row.pack(fill="x", pady=3)
        
        color_box = ctk.CTkButton(
            row, text="", width=16, height=16, corner_radius=2, 
            fg_color=mau_sac, hover_color=mau_sac, cursor="hand2"
        )
        color_box.pack(side="left", padx=(6, 8))
        
        switch_var = ctk.BooleanVar(value=data["layer_visibility"].get(ma_den, True))
        text_hien_thi = f"{ma_den} [{so_luong:02d}]"
        switch = ctk.CTkSwitch(
            row, text=text_hien_thi, font=("Consolas", 11, "bold"), 
            text_color=TEXT_MAIN, progress_color=mau_sac,
            variable=switch_var, command=lambda m=ma_den, v=switch_var: self.toggle_layer(m, v.get())
        )
        switch.pack(side="left", fill="x", expand=True)

        data["layer_switches"][ma_den] = switch

        btn_delete = ctk.CTkButton(
            row, text="×", width=20, height=20, corner_radius=4, 
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=CLOSE_BTN_HOVER, font=("Consolas", 14, "bold"),
            command=lambda m=ma_den, r=row: self.delete_layer(m, r)
        )
        btn_delete.pack(side="right", padx=(4, 6))

        scale_val = data.setdefault("layer_scale", {}).setdefault(ma_den, 1.0)
        slider = ctk.CTkSlider(
            row, width=60, height=12, from_=1.0, to=5.0, 
            button_color=mau_sac, progress_color=mau_sac,
            command=lambda v, m=ma_den: self.change_layer_scale(m, v)
        )
        slider.set(scale_val)
        slider.pack(side="right", padx=(4, 0))

        color_box.configure(command=lambda m=ma_den, cb=color_box, sw=switch, sl=slider: self.change_layer_color(m, cb, sw, sl))
        switch._text_label.bind("<Double-Button-1>", lambda e, m=ma_den: self.rename_layer_action(m))
        switch._text_label.configure(cursor="xterm")

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
        
        if ma_den in data["bang_mau_vat_the"]: del data["bang_mau_vat_the"][ma_den]
        if ma_den in data["layer_visibility"]: del data["layer_visibility"][ma_den]
        if ma_den in data["layer_switches"]: del data["layer_switches"][ma_den]
        if ma_den in data["layer_scale"]: del data["layer_scale"][ma_den]
        
        trang_idx = data["current_page"]
        if trang_idx in data.get("markers", {}) and ma_den in data["markers"][trang_idx]:
            del data["markers"][trang_idx][ma_den]
            
        row_widget.destroy()
        self.render_page(self.active_tab_name, redraw_pdf=False)
        self.log_to_terminal(f"Đã phi tang toàn bộ mã '{ma_den}' khỏi bản vẽ!", "error")
    
    def rename_layer_action(self, ma_cu):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        dialog = ctk.CTkInputDialog(text=f"Đổi tên cho Layer [{ma_cu}]:", title="Rename Layer")
        ma_moi = dialog.get_input()
        
        if not ma_moi or ma_moi.strip() == "" or ma_moi.upper().strip() == ma_cu:
            return 
            
        ma_moi = ma_moi.upper().strip()
        
        if ma_moi in data["bang_mau_vat_the"]:
            self.log_to_terminal(f"LỖI: Tên '{ma_moi}' đã tồn tại trên bản vẽ rồi sếp ơi!", "error")
            return

        data["bang_mau_vat_the"][ma_moi] = data["bang_mau_vat_the"].pop(ma_cu)
        data["layer_visibility"][ma_moi] = data["layer_visibility"].pop(ma_cu)
        if ma_cu in data["layer_scale"]:
            data["layer_scale"][ma_moi] = data["layer_scale"].pop(ma_cu)

        for trang_idx, markers_trang in data.get("markers", {}).items():
            if ma_cu in markers_trang:
                markers_trang[ma_moi] = markers_trang.pop(ma_cu)

        self.log_to_terminal(f"Đã rename Layer: [{ma_cu}] -> [{ma_moi}]", "success")
        
        # Gọi bùa lọc Layer thay cho mớ code loop cũ
        self.build_layer_manager_for_current_page()
        self.render_page(self.active_tab_name, redraw_pdf=False)

    def update_layer_manager_counts(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        trang_idx = data["current_page"]
        markers_trang_nay = data.get("markers", {}).get(trang_idx, {})
        
        for ma_den, switch in data["layer_switches"].items():
            switch.configure(text=f"{ma_den} [00]")
            
        for ma_den, thong_tin in markers_trang_nay.items():
            if ma_den in data["layer_switches"]:
                switch = data["layer_switches"][ma_den]
                switch.configure(text=f"{ma_den} [{thong_tin['so_luong']:02d}]")
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

        tab_ui = ctk.CTkFrame(
            self.custom_tab_bar, fg_color=TAB_ACTIVE, 
            corner_radius=4, border_width=1, border_color=PANEL_BORDER
        )
        tab_ui.pack(side="left", padx=(0, 6), pady=2, fill="y") 

        lbl_name = ctk.CTkLabel(tab_ui, text=tab_name, font=("Consolas", 11, "bold"), text_color=TEXT_MAIN)
        lbl_name.pack(side="left", padx=(12, 8), pady=4)
        
        btn_close = ctk.CTkButton(
            tab_ui, text="×", width=20, height=20, corner_radius=4,
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

        # 🚀 AUTO-CENTER ALGORITHM: Tính toán Tâm của Canvas trước khi nhét bản vẽ vào
        self.canvas_area.update_idletasks() # Ép TKinter hiện hình để lấy kích thước
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10: cw = 1200  # Fallback nếu UI chưa nở
        if ch < 10: ch = 700

        doc = fitz.open(filepath)
        page = doc.load_page(0)
        
        zoom_macdinh = 2.0
        pw = page.rect.width * zoom_macdinh
        ph = page.rect.height * zoom_macdinh
        
        # Đẩy tọa độ x, y ra chính giữa Canvas
        start_x = (cw - pw) / 2
        start_y = (ch - ph) / 2

        self.tabs[tab_name] = {
            "pdf_doc": doc,
            "current_page": 0,
            "zoom_level": zoom_macdinh,
            "drag_data": {"x": 0, "y": 0},
            "img_pos": [start_x, start_y], # 🚀 BẢN VẼ LẬP TỨC NẰM NGAY GIỮA MÀN HÌNH
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
                self.lbl_zoom.configure(text=f"ZOOM // {int(tab_data['zoom_level'] * 100)}%")

                # Đồng bộ trạng thái nút MONO
                if tab_data.get("is_monochrome", False):
                    self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
                else:
                    self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
                
                if tab_data.get("is_monochrome", False):
                    self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
                else:
                    self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
                
                # 🚀 Chỉ hiện Layer của trang hiện tại trên Tab này
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
        self.log_to_terminal(f"Closed layer: {tab_name}", "error")

        if not self.tabs:
            self.active_tab_name = None
            self.lbl_page.configure(text="00 / 00")
            self.lbl_zoom.configure(text="ZOOM // 200%")
            
            for child in self.layer_frame.winfo_children(): child.destroy()

    def render_page(self, tab_name, redraw_pdf=True):
        data = self.tabs.get(tab_name)
        if not data: return

        canvas = data["canvas"]
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]

        # 1. RENDER NỀN PDF & CẬP NHẬT LAYER COUNTS
        if redraw_pdf:
            page = data["pdf_doc"].load_page(data["current_page"])
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # LỌC MONOCHROME: CHUYỂN NỀN SANG GRAYSCALE SIÊU SẠCH
            if data.get("is_monochrome", False):
                img = img.convert("L").convert("RGB")

            data["current_img"] = ImageTk.PhotoImage(img) 
            
            canvas.delete("pdf_background")
            canvas.create_image(pos_x, pos_y, anchor="nw", image=data["current_img"], tags=("pdf_img", "pdf_background"))
            self.update_layer_manager_counts()

        # 2. VẼ MARKERS (THUẬT TOÁN TÂM ĐIỂM TUYỆT ĐỐI)
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
                
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                canh_vuong = 15.0 * zoom * scale
                
                x0_moi = cx - canh_vuong / 2
                y0_moi = cy - canh_vuong / 2
                x1_moi = cx + canh_vuong / 2
                y1_moi = cy + canh_vuong / 2
                
                canvas.create_rectangle(
                    x0_moi, y0_moi, x1_moi, y1_moi, 
                    outline=mau_sac, width=3, tags=("pdf_img", "marker")
                )

        # 3. VẼ BẢNG CHÚ THÍCH (SCALE AI TECHNICAL LEGEND TABLE) & NÚT RESIZE
        canvas.delete("table_legend")
        if "tables" in data and trang_idx in data["tables"]:
            tb = data["tables"][trang_idx]
            
            if isinstance(tb, list):
                tb = {"x": tb[0], "y": tb[1], "scale": 1.0}
                data["tables"][trang_idx] = tb
                
            t_scale = tb.get("scale", 1.0)
            tx = pos_x + tb["x"] * zoom
            ty = pos_y + tb["y"] * zoom
            
            w_table = 230 * zoom * t_scale
            row_h = 24 * zoom * t_scale
            danh_sach_ma = sorted(data["bang_mau_vat_the"].keys())
            h_table = max((len(danh_sach_ma) + 1.8) * row_h, 60 * zoom * t_scale)
            
            # Khung nền Obsidian Zinc chuẩn Scale AI
            canvas.create_rectangle(
                tx, ty, tx + w_table, ty + h_table, 
                fill="#09090B", outline="#B07D4C", width=2, tags=("pdf_img", "table_legend")
            )
            
            canvas.create_text(
                tx + w_table / 2, ty + row_h * 0.7, 
                text="TAKEOFF LEGEND // ANNOTATIONS", 
                fill="#FAFAFA", font=("Consolas", int(11 * zoom * t_scale), "bold"), tags=("pdf_img", "table_legend")
            )
            canvas.create_line(
                tx, ty + row_h * 1.3, tx + w_table, ty + row_h * 1.3, 
                fill="#27272A", width=1, tags=("pdf_img", "table_legend")
            )
            
            for idx, ma_den in enumerate(danh_sach_ma):
                y_row = ty + (idx + 1.9) * row_h
                mau_sac = data["bang_mau_vat_the"][ma_den]
                so_l = markers_trang_nay.get(ma_den, {}).get("so_luong", 0)
                
                canvas.create_rectangle(
                    tx + 12 * zoom * t_scale, y_row - 6 * zoom * t_scale, 
                    tx + 24 * zoom * t_scale, y_row + 6 * zoom * t_scale,
                    fill=mau_sac, outline="#FAFAFA", width=1, tags=("pdf_img", "table_legend")
                )
                
                canvas.create_text(
                    tx + 34 * zoom * t_scale, y_row, text=str(ma_den), anchor="w",
                    fill="#FAFAFA", font=("Consolas", int(11 * zoom * t_scale), "bold"), tags=("pdf_img", "table_legend")
                )
                
                canvas.create_text(
                    tx + w_table - 15 * zoom * t_scale, y_row, text=f"{so_l:02d}", anchor="e",
                    fill="#B07D4C", font=("Consolas", int(12 * zoom * t_scale), "bold"), tags=("pdf_img", "table_legend")
                )

            # Nút nắm góc dưới-phải (Precision handle)
            hx, hy = tx + w_table, ty + h_table
            hw = 10 * zoom
            canvas.create_rectangle(
                hx - hw, hy - hw, hx, hy,
                fill="#B07D4C", outline="#FAFAFA", width=1, tags=("pdf_img", "table_legend")
            )
            canvas.create_line(
                hx - hw + 3, hy - 3, hx - 3, hy - hw + 3, 
                fill="#09090B", width=1.5, tags=("pdf_img", "table_legend")
            )

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
            self.lbl_coords.configure(text=f"COORD // X: {event.x:04d} | Y: {event.y:04d}")
            self.last_mouse_update = now

    def on_drag_start(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        pos_x, pos_y = data["img_pos"]
        zoom = data["zoom_level"]
        px = (event.x - pos_x) / zoom
        py = (event.y - pos_y) / zoom
        trang = data["current_page"]
        
        # 🚀 ƯU TIÊN 1: CHẾ ĐỘ TẨY (ERASE)
        if getattr(self, "current_action", None) == "ERASE":
            if "tables" in data and trang in data["tables"]:
                tb = data["tables"][trang]
                tx = tb["x"] if isinstance(tb, dict) else tb[0]
                ty = tb["y"] if isinstance(tb, dict) else tb[1]
                t_scale = tb.get("scale", 1.0) if isinstance(tb, dict) else 1.0
                
                so_hang = len(data["bang_mau_vat_the"])
                w_tb = 230 * t_scale
                h_tb = max((so_hang + 1.8) * 24 * t_scale, 60 * t_scale)
                
                if tx <= px <= tx + w_tb and ty <= py <= ty + h_tb:
                    del data["tables"][trang]
                    self.log_to_terminal("🗑️ Đã dùng Tẩy xóa Bảng chú thích bằng Chuột Trái!", "error")
                    self.render_page(self.active_tab_name, redraw_pdf=False)
                    return 

            markers_trang_nay = data.get("markers", {}).get(trang, {})
            for ma_den, thong_tin in markers_trang_nay.items():
                if not data["layer_visibility"].get(ma_den, True): continue
                for i, box in enumerate(thong_tin["toa_do"]):
                    if (box[0] - 8) <= px <= (box[2] + 8) and (box[1] - 8) <= py <= (box[3] + 8):
                        thong_tin["toa_do"].pop(i)
                        thong_tin["so_luong"] -= 1
                        self.log_to_terminal(f"🗑️ Đã dùng Tẩy xóa 1 điểm của mã [{ma_den}]!", "error")
                        self.update_layer_manager_counts()
                        self.render_page(self.active_tab_name, redraw_pdf=False)
                        return
            return 

        # 🚀 ƯU TIÊN 2: CHẾ ĐỘ TABLE
        if getattr(self, "current_action", None) == "TABLE":
            if "tables" not in data: data["tables"] = {}
            data["tables"][trang] = {"x": px, "y": py, "scale": 1.0}
            self.render_page(self.active_tab_name, redraw_pdf=False)
            self.log_to_terminal("📌 Đã ghim Bảng! Kéo góc dưới-phải để Phóng to/Thu nhỏ.", "success")
            return

        # 🚀 ƯU TIÊN 3: CHẾ ĐỘ MARK
        if getattr(self, "current_action", None) == "MARK":
            box = [px - 10, py - 10, px + 10, py + 10]
            ma_den = self.current_mark_layer
            data["markers"][trang][ma_den]["toa_do"].append(box)
            data["markers"][trang][ma_den]["so_luong"] += 1
            self.update_layer_manager_counts()
            self.render_page(self.active_tab_name, redraw_pdf=False)
            return 
            
        # 🚀 ƯU TIÊN 4: CHUỘT THƯỜNG - RESIZE HOẶC KÉO BẢNG
        if getattr(self, "current_action", None) is None:
            if "tables" in data and trang in data["tables"]:
                tb = data["tables"][trang]
                tx = tb["x"] if isinstance(tb, dict) else tb[0]
                ty = tb["y"] if isinstance(tb, dict) else tb[1]
                t_scale = tb.get("scale", 1.0) if isinstance(tb, dict) else 1.0
                
                so_hang = len(data["bang_mau_vat_the"])
                w_tb = 230 * t_scale
                h_tb = max((so_hang + 1.8) * 24 * t_scale, 60 * t_scale)
                
                if (tx + w_tb - 25) <= px <= (tx + w_tb + 15) and (ty + h_tb - 25) <= py <= (ty + h_tb + 15):
                    data["resizing_table"] = True
                    data["resize_start_tx"] = tx
                    self.log_to_terminal("🔍 Đang kéo đổi kích thước Bảng...", "sys")
                    return
                    
                if tx <= px <= tx + w_tb and ty <= py <= ty + h_tb:
                    data["dragging_table"] = True
                    data["drag_table_offset"] = [px - tx, py - ty]
                    return

        # 🚀 ƯU TIÊN 5: KÉO CHỌN VÙNG HOẶC PAN BẢN VẼ
        if hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng":
            data["canvas"].config(cursor="crosshair")
            data["drag_data"]["start_x"] = event.x
            data["drag_data"]["start_y"] = event.y
            if data.get("rect_id"): data["canvas"].delete(data["rect_id"])
            data["rect_id"] = data["canvas"].create_rectangle(
                event.x, event.y, event.x, event.y, 
                outline=ACCENT_MAIN, width=2, dash=(4, 4), tags="selection_rect"
            )
        else: 
            data["canvas"].config(cursor="fleur")
            data["drag_data"]["x"] = event.x
            data["drag_data"]["y"] = event.y

    def on_drag_motion(self, event):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        if getattr(self, "current_action", None) in ["MARK", "ERASE", "TABLE"]: return
        
        # RESIZE 1:1 THEO CHUỘT
        if data.get("resizing_table", False):
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            tx = data["resize_start_tx"]
            
            new_scale = max(0.4, min(4.0, (px - tx) / 230.0))
            data["tables"][data["current_page"]]["scale"] = new_scale
            self.render_page(self.active_tab_name, redraw_pdf=False)
            return

        # DI CHUYỂN BẢNG
        if data.get("dragging_table", False):
            pos_x, pos_y = data["img_pos"]
            zoom = data["zoom_level"]
            px = (event.x - pos_x) / zoom
            py = (event.y - pos_y) / zoom
            ox, oy = data["drag_table_offset"]
            
            data["tables"][data["current_page"]]["x"] = px - ox
            data["tables"][data["current_page"]]["y"] = py - oy
            self.render_page(self.active_tab_name, redraw_pdf=False)
            return
        
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
        data = self.tabs[self.active_tab_name]
        
        data["dragging_table"] = False
        data["resizing_table"] = False
        
        if getattr(self, "current_action", None) in ["MARK", "ERASE"]: return

        if not hasattr(self, 'area_mode_var') or self.area_mode_var.get() == "Toàn bản vẽ": return
        
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
        data["canvas"].config(cursor="fleur") 
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
        
        if getattr(self, "current_action", None) == "MARK" or (hasattr(self, 'area_mode_var') and self.area_mode_var.get() == "Kéo chọn vùng"):
            data["canvas"].config(cursor="crosshair")
        else:
            data["canvas"].config(cursor="")

    # ==========================================
    # 🚀 BÚA TẨY CHUỘT PHẢI (RIGHT-CLICK ERASER / UNDO)
    # ==========================================
    def on_right_click(self, event):
        if not self.active_tab_name: return
        
        # 1. Đang cầm súng Mark -> Nhấp phải là Undo điểm vừa chấm
        if getattr(self, "current_action", None) == "MARK":
            self.undo_manual_mark()
            return

        data = self.tabs[self.active_tab_name]
        trang = data["current_page"]

        # 2. CHỈ KHI Ở CHẾ ĐỘ "TABLE" THÌ NHẤP CHUỘT PHẢI MỚI XÓA BẢNG
        if getattr(self, "current_action", None) == "TABLE":
            if "tables" in data and trang in data["tables"]:
                del data["tables"][trang]
                self.log_to_terminal("🗑️ Đã dùng Chuột phải xóa Bảng chú thích!", "error")
                self.render_page(self.active_tab_name, redraw_pdf=False)
            return

        # 3. Đang cầm Tẩy (ERASE) -> Tẩy chỉ xài chuột trái
        if getattr(self, "current_action", None) == "ERASE":
            return

        # 4. CHUỘT THƯỜNG -> NHẤP PHẢI TRÚNG KÝ HIỆU LÀ XÓA KÝ HIỆU
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
        
        data["img_pos"] = [mx - (mx - img_x) * zoom_factor, my - (my - img_y) * zoom_factor]
        self.lbl_zoom.configure(text=f"ZOOM // {int(data['zoom_level'] * 100)}%")

        if self.zoom_timer: self.after_cancel(self.zoom_timer)
        self.zoom_timer = self.after(150, lambda n=self.active_tab_name: self.render_page(n, redraw_pdf=True))

    def prev_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] > 0:
            data["current_page"] -= 1
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.build_layer_manager_for_current_page() # 🚀 QUÉT RÁC TRANG CŨ
            self.render_page(self.active_tab_name)

    def next_page(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        if data["current_page"] < data["pdf_doc"].page_count - 1:
            data["current_page"] += 1
            self.lbl_page.configure(text=f"{data['current_page'] + 1:02d} / {data['pdf_doc'].page_count:02d}")
            self.build_layer_manager_for_current_page() # 🚀 QUÉT RÁC TRANG CŨ
            self.render_page(self.active_tab_name)

    def log_to_terminal(self, text, tag="sys"):
        self.txt_log.configure(state="normal")
        self.txt_log._textbox.insert("end", f">> {text}\n", tag)
        self.txt_log._textbox.see("end")
        self.txt_log.configure(state="disabled")

    # ==========================================
    # KHU VỰC 5: KÍCH HOẠT ĐỘNG CƠ BACKEND (QUÉT TOÀN PROJECT & BỌC THÉP)
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
        
        # 🚀 THUẬT TOÁN ĐỒNG BỘ RAM -> ĐĨA CỨNG: 
        # Ép phần mềm lưu nguyên cái Project (đã gộp các trang) ra một file tạm dưới ổ cứng.
        # Xong mới ném file tạm đó cho Backend nó quét, đảm bảo đéo bao giờ bị crash vì lệch trang!
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
            from logic.api_handler import goi_backend_boc_tach
            all_results = {}
            co_loi = False
            loi_msg = ""
            
            # Quét sạch sành sanh các trang có trong Project
            for p in range(tong_so_trang):
                # Khoanh vùng chỉ áp dụng trên trang đang mở, trang khác auto quét full
                vung_cho_trang_nay = vung_chon if p == trang_hien_tai else None
                thanh_cong, ket_qua = goi_backend_boc_tach(temp_path, p, mode, chu_ky, vung_cho_trang_nay)
                
                if thanh_cong:
                    # Bắt chặt lỗi ẩn từ Backend ném về
                    if isinstance(ket_qua, dict) and "error" in ket_qua:
                        co_loi = True
                        loi_msg = ket_qua["error"]
                        break
                    elif isinstance(ket_qua, dict):
                        # Khớp dữ liệu bất chấp việc backend có bọc trong key "data" hay không
                        all_results[p] = ket_qua.get("data", ket_qua) 
                    else:
                        all_results[p] = {}
                else:
                    co_loi = True
                    loi_msg = str(ket_qua)
                    break 
                    
            # 🚀 Chạy xong thì quét dọn sạch sẽ file tạm trên ổ cứng
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
            
            # Tải lại Layer List của trang hiện tại và Render
            self.build_layer_manager_for_current_page() 
            self.render_page(self.active_tab_name)
        else:
            self.log_to_terminal(f"SYSTEM EXCEPTION: {all_results}", "error")
            
    # ==========================================
    # 🚀 TRẠNG THÁI NGHỈ CỦA TOUCH BAR (SCALE AI TECHNICAL HUD IDLE)
    # ==========================================
    def show_idle_touchbar(self):
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        self.current_action = None
        self.is_insert_menu_open = False
        
        # BÊ PNG GỐC VÀ NHUỘM SANG MÀU NÂU VÀNG PROMA CHÌM TRÊN NỀN OBSIDIAN
        if not hasattr(self, 'touchbar_logo_img') or self.touchbar_logo_img is None:
            try:
                thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
                thu_muc_client = os.path.dirname(thu_muc_hien_tai)
                logo_filename = os.path.join(thu_muc_client, "assets", "Proma Logo 1.png")
                
                img_goc = Image.open(logo_filename).convert("RGBA")
                w_goc, h_goc = img_goc.size
                
                w_mini = int(w_goc * (20 / h_goc))
                img_resized = img_goc.resize((w_mini, 20), Image.Resampling.LANCZOS)
                
                # Nhuộm nâu vàng Proma ấm sắc nét (#B07D4C với Alpha 170)
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
            
        # TOGGLE: Đang mở Insert thì bấm phát nữa sẽ tắt về trạng thái Logo Idle
        if getattr(self, "is_insert_menu_open", False):
            self.show_idle_touchbar()
            self.log_to_terminal("HUD menu closed.", "sys")
            return

        self.is_insert_menu_open = True
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        self.current_action = None

        # --- NÚT 1: MARK (PRECISION ENGINEERING TOOL 4PX) ---
        btn_mark = ctk.CTkButton(
            self.touch_bar, text="[ MARK ]", width=74, height=24, corner_radius=4, 
            fg_color="#D5B07C", text_color=BG_DARK, hover_color="#C49A6C", 
            font=("Consolas", 11, "bold"), border_width=1, border_color="#E8C695",
            command=self.start_manual_mark
        )
        btn_mark.pack(side="left", padx=(14, 4), pady=4)

        # --- NÚT 2: ERASE ---
        btn_erase = ctk.CTkButton(
            self.touch_bar, text="[ ERASE ]", width=74, height=24, corner_radius=4, 
            fg_color="#EF4444", text_color="#FFFFFF", hover_color="#DC2626", 
            font=("Consolas", 11, "bold"), border_width=1, border_color="#F87171",
            command=self.start_erase_mode
        )
        btn_erase.pack(side="left", padx=4, pady=4)

        # --- NÚT 3: TABLE ---
        btn_table = ctk.CTkButton(
            self.touch_bar, text="[ TABLE ]", width=74, height=24, corner_radius=4, 
            fg_color="#10B981", text_color="#09090B", hover_color="#34D399", 
            font=("Consolas", 11, "bold"), border_width=1, border_color="#6EE7B7",
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
            self.touch_bar, text=f"// MARKING ACTIVE: [ {layer_name} ]", 
            font=("Consolas", 11, "bold"), text_color=ACCENT_MAIN
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
            self.touch_bar, text="// ERASING MODE: Click target bounding box or table to purge", 
            font=("Consolas", 11, "bold"), text_color="#EF4444"
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
    # 🚀 CHẾ ĐỘ TABLE (TECHNICAL CAD/SCALE AI LEGEND TABLE)
    # ==========================================
    def start_table_mode(self):
        if not self.active_tab_name: return
        self.current_action = "TABLE"
        data = self.tabs[self.active_tab_name]
        data["canvas"].config(cursor="plus") 
        
        for widget in self.touch_bar.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(
            self.touch_bar, text="// TABLE PLACEMENT: Click canvas to deploy legend", 
            font=("Consolas", 11, "bold"), text_color="#10B981"
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

    # 🚀 XOAY TRANG BẢN VẼ
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

    # ==========================================
    # 🚀 CHẾ ĐỘ MONOCHROME (LỌC TRẮNG ĐEN BẢN VẼ GỐC)
    # ==========================================
    def toggle_monochrome(self):
        if not self.active_tab_name: return
        data = self.tabs[self.active_tab_name]
        
        data["is_monochrome"] = not data.get("is_monochrome", False)
        
        if data["is_monochrome"]:
            self.btn_mono.configure(fg_color=ACCENT_MAIN, text_color=BG_DARK)
            self.log_to_terminal("◐ Monochrome background filter activated (Grayscale).", "action")
        else:
            self.btn_mono.configure(fg_color=PANEL_BG, text_color=TEXT_MAIN)
            self.log_to_terminal("◐ Original blueprint color scheme restored.", "sys")
            
        self.render_page(self.active_tab_name, redraw_pdf=True)

    # ==========================================
    # KHU VỰC 6: XUẤT BẢN VẼ (SCALE AI PRECISION EXPORT)
    # ==========================================
    # ==========================================
    # KHU VỰC 6: XUẤT BẢN VẼ (RAM-BASED EXPORT & SCOPING)
    # ==========================================
    def export_markup_pdf(self):
        if not self.active_tab_name:
            self.log_to_terminal("ERROR: Có bản vẽ nào đâu mà xuất sếp ơi!", "error")
            return
            
        data_tab = self.tabs[self.active_tab_name]
        
        # 🚀 HUD POPUP: HỎI XUẤT 1 TRANG HAY TOÀN BỘ PROJECT
        popup = ctk.CTkToplevel(self)
        popup.title("EXPORT SCOPE // PROMA")
        popup.geometry("480x220")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="// SELECT EXPORT RANGE", font=("Consolas", 15, "bold"), text_color=ACCENT_MAIN).pack(pady=(25, 10))
        ctk.CTkLabel(popup, text="Export the entire project document or only the current active page?", font=("Consolas", 11), text_color=TEXT_MUTED).pack(pady=(0, 15))

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
            
            # 🚀 Lõi RAM: Bóc toàn bộ bản vẽ hiện tại thành Bytes (bao gồm cả các trang đã Nối)
            pdf_bytes = data_tab["pdf_doc"].tobytes()
            
            threading.Thread(
                target=self._thread_export_pdf, 
                args=(pdf_bytes, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay, tables_data, is_mono, scope, current_page_idx), 
                daemon=True
            ).start()

        ctk.CTkButton(
            btn_frame, text="[ CURRENT PAGE ONLY ]", height=42, corner_radius=4, 
            font=("Consolas", 12, "bold"), fg_color=PANEL_BG, hover_color=TAB_HOVER, 
            border_width=1, border_color=ACCENT_MAIN, text_color=ACCENT_MAIN, 
            command=lambda: do_export("CURRENT")
        ).pack(side="left", expand=True, fill="x", padx=6)
        
        ctk.CTkButton(
            btn_frame, text="[ ALL PROJECT PAGES ]", height=42, corner_radius=4, 
            font=("Consolas", 12, "bold"), fg_color=ACCENT_MAIN, hover_color=ACCENT_HOVER, 
            text_color=BG_DARK, border_width=1, border_color="#E6A86E", 
            command=lambda: do_export("ALL")
        ).pack(side="right", expand=True, fill="x", padx=6)

    def _thread_export_pdf(self, pdf_bytes, file_luu, markers_data, bang_mau, visibility, scales, goc_xoay, tables_data, is_mono, scope, current_page_idx):
        try:
            import fitz
            # 🚀 Mở bộ nhớ đệm thành PDF thay vì mở file từ ổ cứng
            pdf_copy = fitz.open("pdf", pdf_bytes)
            tong_o_ve = 0
            tong_bang_ve = 0

            # 🚀 Thuật toán Tỉa Trang: Giữ hết hay cắt gọt chừa đúng 1 trang?
            if scope == "CURRENT":
                pdf_copy.select([current_page_idx]) # Lệnh chém bay toàn bộ các trang khác
                trang_map = {current_page_idx: 0}   # Map trang đang xem thành trang 0 duy nhất
            else:
                trang_map = {i: i for i in range(pdf_copy.page_count)}
            
            for trang_cu, trang_moi in trang_map.items():
                page = pdf_copy.load_page(trang_moi)
                
                if page.rotation != goc_xoay.get(trang_cu, 0):
                    page.set_rotation(goc_xoay.get(trang_cu, 0))
            
                # BỘ LỌC MONOCHROME EXPORT
                if is_mono:
                    mat_mono = fitz.Matrix(2.0, 2.0)
                    pix_mono = page.get_pixmap(matrix=mat_mono, colorspace=fitz.csGRAY)
                    rect_page = page.rect
                    page.clean_contents()
                    page.insert_image(rect_page, pixmap=pix_mono)
                
                # Móc dữ liệu bằng ID Trang Cũ nhưng vẽ lên Trang Mới
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

                # B. VẼ BẢNG CHÚ THÍCH (SCALE AI TECHNICAL LEGEND TABLE)
                if trang_cu in tables_data:
                    tb = tables_data[trang_cu]
                    tx = tb["x"] if isinstance(tb, dict) else tb[0]
                    ty = tb["y"] if isinstance(tb, dict) else tb[1]
                    t_scale = tb.get("scale", 1.0) if isinstance(tb, dict) else 1.0
                    
                    danh_sach_ma = sorted(bang_mau.keys())
                    w_table = 180.0 * t_scale
                    row_h = 18.0 * t_scale
                    h_table = max((len(danh_sach_ma) + 1.8) * row_h, 45.0 * t_scale)
                    
                    rgb_vien = (0.69, 0.49, 0.30)       # PROMA Amber Bronze #B07D4C
                    rgb_nen = (0.04, 0.04, 0.04)        # Scale AI Obsidian #09090B
                    rgb_chu_trang = (0.98, 0.98, 0.98)  # Zinc 50
                    rgb_chu_vang = (0.85, 0.55, 0.28)   # Amber 500
                    
                    shape_table = page.new_shape()
                    
                    rect_table = fitz.Rect(tx, ty, tx + w_table, ty + h_table)
                    shape_table.draw_rect(rect_table)
                    shape_table.finish(color=rgb_vien, fill=rgb_nen, width=1.5 * t_scale)
                    
                    shape_table.draw_line(
                        fitz.Point(tx, ty + row_h * 1.3), 
                        fitz.Point(tx + w_table, ty + row_h * 1.3)
                    )
                    shape_table.finish(color=(0.15, 0.15, 0.16), width=0.5 * t_scale)
                    
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
                        "TAKEOFF LEGEND // ANNOTATIONS", 
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
            self.log_to_terminal(f"✅ ANNOTATION EXPORT COMPLETE // {tong_o_ve} bounding boxes & {tong_bang_ve} legend tables stamped.", "success")
            self.log_to_terminal(f"File stored at: {file_luu}", "sys")
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
        from logic.api_handler import goi_backend_hoc_ky_hieu
        thanh_cong, ket_qua = goi_backend_hoc_ky_hieu(filepath, page_idx)
        self.after(0, self._hoan_thanh_train, thanh_cong, ket_qua)
        
    def _hoan_thanh_train(self, thanh_cong, ket_qua):
        if thanh_cong and ket_qua.get("data"):
            self.log_to_terminal("Training signatures captured. Awaiting user verification...", "action")
            self.hien_thi_popup_xac_minh(ket_qua["data"])
        else:
            self.log_to_terminal(f"❌ SYMBOL TRAINING FAULT: {ket_qua.get('error', 'Unknown exception')}", "error")

    def hien_thi_popup_xac_minh(self, du_lieu_hoc_duoc):
        # 🚀 CỬA SỔ POPUP XÁC MINH CỰC CHẤT (SCALE AI TECHNICAL DIALOG)
        popup = ctk.CTkToplevel(self)
        popup.title("SYMBOL SIGNATURE VERIFICATION // PROMA AI")
        popup.geometry("480x560")
        popup.attributes("-topmost", True) 
        popup.configure(fg_color=BG_DARK)

        ctk.CTkLabel(popup, text="// IDENTIFIED LEGEND SIGNATURES:", font=("Consolas", 14, "bold"), text_color=ACCENT_MAIN).pack(pady=(20, 6))
        ctk.CTkLabel(popup, text="Verify bounding box dimensions [w x h] before committing model weights.", font=("Consolas", 11), text_color=TEXT_MUTED).pack(pady=(0, 14))

        scroll = ctk.CTkScrollableFrame(
            popup, width=410, height=360, 
            fg_color=PANEL_BG, corner_radius=4, border_width=1, border_color=PANEL_BORDER
        )
        scroll.pack(pady=10, padx=20, fill="both", expand=True)

        for ma, thong_so in du_lieu_hoc_duoc.items():
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=f"LAYER // {ma}", font=("Consolas", 13, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"BOX [ W: {thong_so['w']} | H: {thong_so['h']} ]", font=("Consolas", 11, "bold"), text_color=TEXT_MUTED).pack(side="right", padx=10)

        def xac_nhan_luu():
            if not hasattr(self, 'chu_ky_ai'): self.chu_ky_ai = {}
            self.chu_ky_ai.update(du_lieu_hoc_duoc)
            self.log_to_terminal(f"✅ Model signatures validated and committed to active pipeline.", "success")
            popup.destroy()

        ctk.CTkButton(
            popup, text="[ ✔ COMMIT SYMBOL SIGNATURES ]", height=46, corner_radius=4,
            font=("Consolas", 13, "bold"), fg_color=ACCENT_MAIN, 
            hover_color=ACCENT_HOVER, text_color=BG_DARK, 
            border_width=1, border_color="#E6A86E",
            command=xac_nhan_luu
        ).pack(pady=(12, 20), padx=20, fill="x")
