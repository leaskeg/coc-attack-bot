import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import scrolledtext
import threading
import queue
import logging
import datetime
import time

from ..bot_controller import BotController
from ..utils.config_validator import ConfigValidator
from ..utils.attack_strategy import AttackStrategyConfig, DeploySpeedSettings, StrategySettings, HeroAbilitySettings, HumanLikeVariations, EndBattleSettings

BG       = "#FFFFFF"
FRAME_BG = "#F5F7FA"
ACCENT   = "#4F6CF7"
GREEN    = "#16A34A"
RED      = "#DC2626"
YELLOW   = "#D97706"
TEXT     = "#111827"
SUBTEXT  = "#6B7280"
BORDER   = "#E5E7EB"
ENTRY_BG = "#F3F4F6"
BTN_BG   = "#E5E7EB"

FARM_COLOR   = "#0EA5E9"
LEGEND_COLOR = "#7C3AED"


class _QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self._queue = log_queue

    def emit(self, record):
        self._queue.put(record)


class BotGUI:
    def __init__(self, controller: BotController):
        self.controller = controller
        self._log_queue = queue.Queue()
        self._log_handler = _QueueHandler(self._log_queue)
        self._log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger("AppLogger").addHandler(self._log_handler)

        self._log_level_filter = "ALL"

        self.root = tk.Tk()
        self._auto_scroll = tk.BooleanVar(value=True)
        self.root.title("CoC Attack Bot")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self._setup_style()
        self._build_header()
        self._build_notebook()
        self._periodic_update()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=TEXT, fieldbackground=ENTRY_BG,
                        bordercolor=BORDER, troughcolor=FRAME_BG, relief="flat")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 9))
        style.configure("TButton", background=BTN_BG, foreground=TEXT, bordercolor=BORDER,
                        focuscolor=ACCENT, padding=(8, 6), font=("Segoe UI", 9))
        style.map("TButton",
                  background=[("active", ACCENT), ("pressed", "#3B56D6")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Accent.TButton", background=ACCENT, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton",
                  background=[("active", "#3B56D6"), ("pressed", "#2D43C4")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Green.TButton", background=GREEN, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"))
        style.map("Green.TButton",
                  background=[("active", "#15803D"), ("pressed", "#166534")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Red.TButton", background=RED, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"))
        style.map("Red.TButton",
                  background=[("active", "#B91C1C"), ("pressed", "#991B1B")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Farm.TButton", background=FARM_COLOR, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"))
        style.map("Farm.TButton", background=[("active", "#0284C7")])
        style.configure("Legend.TButton", background=LEGEND_COLOR, foreground="#FFFFFF",
                        font=("Segoe UI", 9, "bold"))
        style.map("Legend.TButton", background=[("active", "#6D28D9")])
        style.configure("TNotebook", background=BG, bordercolor=BORDER, tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab", background=FRAME_BG, foreground=SUBTEXT,
                        padding=[14, 7], font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", ACCENT)],
                  font=[("selected", ("Segoe UI", 9, "bold"))])
        style.configure("TLabelframe", background=FRAME_BG, foreground=SUBTEXT,
                        bordercolor=BORDER, relief="solid")
        style.configure("TLabelframe.Label", background=FRAME_BG, foreground=SUBTEXT,
                        font=("Segoe UI", 8, "bold"))
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT,
                        bordercolor=BORDER, insertcolor=TEXT, relief="solid")
        style.configure("TCheckbutton", background=BG, foreground=TEXT, font=("Segoe UI", 9))
        style.map("TCheckbutton", background=[("active", BG)])
        style.configure("Card.TCheckbutton", background=FRAME_BG, foreground=TEXT,
                        font=("Segoe UI", 9))
        style.map("Card.TCheckbutton", background=[("active", FRAME_BG)])
        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=TEXT,
                        background=BTN_BG, arrowcolor=SUBTEXT, bordercolor=BORDER)
        style.configure("Treeview", background=BG, foreground=TEXT,
                        fieldbackground=BG, bordercolor=BORDER, rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=FRAME_BG, foreground=SUBTEXT,
                        bordercolor=BORDER, font=("Segoe UI", 8, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("TScale", background=FRAME_BG, troughcolor=ENTRY_BG)
        style.configure("Horizontal.TScrollbar", background=BTN_BG, troughcolor=ENTRY_BG,
                        bordercolor=BORDER, arrowcolor=SUBTEXT)
        style.configure("Vertical.TScrollbar", background=BTN_BG, troughcolor=ENTRY_BG,
                        bordercolor=BORDER, arrowcolor=SUBTEXT)
        style.configure("TSeparator", background=BORDER)
        style.configure("Card.TFrame", background=FRAME_BG, relief="flat")
        style.configure("Card.TLabel", background=FRAME_BG, foreground=TEXT, font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background=FRAME_BG, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"))
        style.configure("Stat.TLabel", background=FRAME_BG, foreground=TEXT,
                        font=("Segoe UI", 20, "bold"))
        style.configure("StatTitle.TLabel", background=FRAME_BG, foreground=SUBTEXT,
                        font=("Segoe UI", 8))
        style.configure("Header.TFrame", background=BG)
        style.configure("Header.TLabel", background=BG, foreground=TEXT,
                        font=("Segoe UI", 14, "bold"))

    def _build_header(self):
        wrapper = tk.Frame(self.root, bg=BG)
        wrapper.pack(fill="x", side="top")

        header = tk.Frame(wrapper, bg=BG, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="⚔  CoC Attack Bot", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=18, pady=14)

        right_bar = tk.Frame(header, bg=BG)
        right_bar.pack(side="right", padx=14, pady=10)

        self._status_dot = tk.Label(right_bar, text="●", bg=BG, fg=RED, font=("Segoe UI", 13))
        self._status_dot.pack(side="right", padx=(2, 0))
        self._status_label = tk.Label(right_bar, text="Stopped", bg=BG, fg=RED,
                                      font=("Segoe UI", 9, "bold"))
        self._status_label.pack(side="right", padx=(0, 6))

        self._mode_pill = tk.Label(right_bar, text="  FARM  ", bg=FARM_COLOR, fg="#FFFFFF",
                                   font=("Segoe UI", 8, "bold"), padx=8, pady=3, relief="flat")
        self._mode_pill.pack(side="right", padx=(0, 10))

        tk.Frame(wrapper, bg=BORDER, height=1).pack(fill="x")

    def _build_notebook(self):
        self._notebook = ttk.Notebook(self.root)
        self._notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._tab_dashboard = ttk.Frame(self._notebook)
        self._tab_auto = ttk.Frame(self._notebook)
        self._tab_strategy = ttk.Frame(self._notebook)
        self._tab_recorder = ttk.Frame(self._notebook)
        self._tab_coords = ttk.Frame(self._notebook)
        self._tab_ai = ttk.Frame(self._notebook)
        self._tab_donation = ttk.Frame(self._notebook)
        self._tab_config = ttk.Frame(self._notebook)

        self._notebook.add(self._tab_dashboard, text="Dashboard")
        self._notebook.add(self._tab_auto, text="Auto Attacker")
        self._notebook.add(self._tab_strategy, text="Attack Strategy")
        self._notebook.add(self._tab_recorder, text="Recorder")
        self._notebook.add(self._tab_coords, text="Coordinates")
        self._notebook.add(self._tab_ai, text="AI Analyzer")
        self._notebook.add(self._tab_donation, text="💚 Donations")
        self._notebook.add(self._tab_config, text="Config")

        self._build_dashboard_tab()
        self._build_auto_attacker_tab()
        self._build_strategy_tab()
        self._build_recorder_tab()
        self._build_coords_tab()
        self._build_ai_tab()
        self._build_donation_tab()
        self._build_config_tab()

    def _card(self, parent, title=None, padx=6, pady=6, **kw):
        outer = ttk.Frame(parent, style="Card.TFrame", padding=1)
        if title:
            lf = ttk.LabelFrame(outer, text=title, style="TLabelframe", padding=8)
            lf.pack(fill="both", expand=True, padx=padx, pady=pady)
            return outer, lf
        inner = ttk.Frame(outer, style="Card.TFrame", padding=8)
        inner.pack(fill="both", expand=True, padx=padx, pady=pady)
        return outer, inner

    def _stat_card(self, parent, title, initial="—"):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=12)
        frame.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        t = ttk.Label(frame, text=title.upper(), style="StatTitle.TLabel")
        t.pack(anchor="w")
        v = ttk.Label(frame, text=initial, style="Stat.TLabel")
        v.pack(anchor="w", pady=(2, 0))
        return v

    def _build_dashboard_tab(self):
        stats_row = ttk.Frame(self._tab_dashboard)
        stats_row.pack(fill="x", padx=8, pady=(8, 4))

        self._stat_total = self._stat_card(stats_row, "Total Attacks", "0")
        self._stat_success = self._stat_card(stats_row, "Successful", "0")
        self._stat_failed = self._stat_card(stats_row, "Failed", "0")
        self._stat_rate = self._stat_card(stats_row, "Success Rate", "0%")
        self._stat_runtime = self._stat_card(stats_row, "Runtime", "0h")
        self._stat_per_hour = self._stat_card(stats_row, "Attacks/Hour", "0")
        self._stat_legend_attacks = self._stat_card(stats_row, "Legend Today", "—")

        content = ttk.Frame(self._tab_dashboard)
        content.pack(fill="both", expand=True, padx=8, pady=4)

        left_outer, left = self._card(content, "Controls")
        left_outer.pack(side="left", fill="both", expand=True, padx=(0, 4))

        mode_lbl = ttk.Label(left, text="ATTACK MODE", style="Card.TLabel",
                             foreground=SUBTEXT, font=("Segoe UI", 7, "bold"),
                             background=FRAME_BG)
        mode_lbl.pack(anchor="w", pady=(0, 4))

        mode_row = ttk.Frame(left, style="Card.TFrame")
        mode_row.pack(fill="x", pady=(0, 6))
        self._dash_farm_btn = ttk.Button(mode_row, text="⚒  Farm", style="Farm.TButton",
                                         command=self._set_mode_farm)
        self._dash_farm_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self._dash_legend_btn = ttk.Button(mode_row, text="🏆  Legend", style="Legend.TButton",
                                           command=self._set_mode_legend)
        self._dash_legend_btn.pack(side="left", fill="x", expand=True, padx=(3, 0))

        ttk.Separator(left, style="TSeparator").pack(fill="x", pady=6)

        self._dash_start_btn = ttk.Button(left, text="▶  Start Auto Attack", style="Green.TButton",
                                          command=self._dashboard_start)
        self._dash_start_btn.pack(fill="x", pady=3)

        self._dash_stop_btn = ttk.Button(left, text="■  Stop Auto Attack", style="Red.TButton",
                                         command=self._dashboard_stop)
        self._dash_stop_btn.pack(fill="x", pady=3)

        ttk.Separator(left, style="TSeparator").pack(fill="x", pady=8)

        ttk.Button(left, text="Take Screenshot", command=self._take_screenshot).pack(fill="x", pady=3)
        ttk.Button(left, text="Detect Game Window", command=self._detect_window).pack(fill="x", pady=3)
        ttk.Button(left, text="Validate Config", command=self._validate_config_dash).pack(fill="x", pady=3)

        right_outer, right = self._card(content, "Status & Activity")
        right_outer.pack(side="left", fill="both", expand=True, padx=(4, 0))

        status_grid = ttk.Frame(right, style="Card.TFrame")
        status_grid.pack(fill="x", pady=(0, 8))

        ttk.Label(status_grid, text="Game Window:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=0, column=0, sticky="w")
        self._window_status_lbl = ttk.Label(status_grid, text="Not detected", style="Card.TLabel", foreground=RED, background=FRAME_BG)
        self._window_status_lbl.grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Label(status_grid, text="Config Status:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._config_status_lbl = ttk.Label(status_grid, text="Not checked", style="Card.TLabel", foreground=SUBTEXT, background=FRAME_BG)
        self._config_status_lbl.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))

        ttk.Separator(right).pack(fill="x", pady=8)

        log_header = ttk.Frame(right, style="Card.TFrame")
        log_header.pack(fill="x", pady=(0, 4))
        ttk.Label(log_header, text="Application Logs", style="CardTitle.TLabel", background=FRAME_BG).pack(side="left")
        
        self._log_level_var = tk.StringVar(value="ALL")
        log_filter = ttk.Combobox(log_header, textvariable=self._log_level_var, 
                                  values=("ALL", "INFO", "WARNING", "ERROR"), 
                                  state="readonly", width=10)
        log_filter.pack(side="right")
        log_filter.bind("<<ComboboxSelected>>", lambda e: self._set_log_filter(self._log_level_var.get()))

        self._log_text = scrolledtext.ScrolledText(right, height=12, bg=ENTRY_BG, fg=TEXT,
                                           insertbackground=TEXT, relief="flat",
                                           font=("Consolas", 9), borderwidth=1)
        self._log_text.pack(fill="both", expand=True)
        self._log_text.config(state="disabled")

        self._log_text.tag_config("INFO", foreground=TEXT)
        self._log_text.tag_config("WARNING", foreground=YELLOW)
        self._log_text.tag_config("ERROR", foreground=RED)
        self._log_text.tag_config("DEBUG", foreground=SUBTEXT)

        btn_row = ttk.Frame(right, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_row, text="Clear Logs", command=self._log_clear, padding=2).pack(side="left")
        ttk.Checkbutton(btn_row, text="Auto-scroll", style="Card.TCheckbutton", variable=self._auto_scroll).pack(side="right")

    def _dashboard_start(self):
        threading.Thread(target=self.controller.start_auto_attack, daemon=True).start()

    def _dashboard_stop(self):
        def _stop():
            self.root.after(0, lambda: self._status_label.config(text="Stopping…", fg=YELLOW))
            self.root.after(0, lambda: self._status_dot.config(fg=YELLOW))
            self.controller.stop_auto_attack()
            self.root.after(0, lambda: self._status_label.config(text="Stopped", fg=RED))
            self.root.after(0, lambda: self._status_dot.config(fg=RED))
        threading.Thread(target=_stop, daemon=True).start()

    def _set_mode_farm(self):
        self.controller.set_attack_mode("farm")
        self._rebuild_required_buttons()

    def _set_mode_legend(self):
        self.controller.set_attack_mode("legend")
        self._rebuild_required_buttons()

    def _take_screenshot(self):
        try:
            path = self.controller.take_screenshot()
            messagebox.showinfo("Screenshot", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _detect_window(self):
        result = self.controller.detect_game_window()
        if result:
            x, y, w, h = result
            self._window_status_lbl.config(text=f"Detected: ({x},{y}) {w}x{h}", foreground=GREEN)
        else:
            self._window_status_lbl.config(text="Not detected", foreground=RED)

    def _validate_config_dash(self):
        ok, errors = self.controller.validate_auto_attack_config()
        if ok:
            self._config_status_lbl.config(text="Valid", foreground=GREEN)
            logging.getLogger("AppLogger").info("Config validation passed.")
        else:
            self._config_status_lbl.config(text="Invalid", foreground=RED)
            for err in errors:
                logging.getLogger("AppLogger").error(f"Config error: {err}")

    def _build_auto_attacker_tab(self):
        left = ttk.Frame(self._tab_auto)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        right = ttk.Frame(self._tab_auto)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        tree_frame = ttk.LabelFrame(left, text="Attack Sessions", padding=6)
        tree_frame.pack(fill="both", expand=True)

        self._auto_tree = ttk.Treeview(tree_frame, columns=("variation",), show="tree headings", selectmode="browse")
        self._auto_tree.heading("#0", text="Group")
        self._auto_tree.heading("variation", text="Variation")
        self._auto_tree.column("#0", width=160)
        self._auto_tree.column("variation", width=160)

        auto_vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._auto_tree.yview)
        self._auto_tree.configure(yscrollcommand=auto_vsb.set)
        self._auto_tree.pack(side="left", fill="both", expand=True)
        auto_vsb.pack(side="right", fill="y")

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=(6, 0))
        ttk.Button(btn_row, text="+ Group", command=self._auto_add_group).pack(side="left", padx=2)
        ttk.Button(btn_row, text="+ Variation", command=self._auto_add_variation).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Remove", command=self._auto_remove).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Save", command=self._auto_save).pack(side="left", padx=2)

        mode_frame = ttk.LabelFrame(right, text="Attack Mode", padding=8)
        mode_frame.pack(fill="x", pady=(0, 6))

        auto_mode_row = ttk.Frame(mode_frame)
        auto_mode_row.pack(fill="x")
        self._auto_farm_btn = ttk.Button(auto_mode_row, text="⚒  Farm (Battle)",
                                         style="Farm.TButton", command=self._set_mode_farm)
        self._auto_farm_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self._auto_legend_btn = ttk.Button(auto_mode_row, text="🏆  Legend League",
                                           style="Legend.TButton", command=self._set_mode_legend)
        self._auto_legend_btn.pack(side="left", fill="x", expand=True, padx=(3, 0))

        self._auto_mode_desc = ttk.Label(mode_frame, text="", foreground=SUBTEXT,
                                         font=("Segoe UI", 8), wraplength=260)
        self._auto_mode_desc.pack(anchor="w", pady=(6, 0))

        legend_frame = ttk.LabelFrame(right, text="Legend League Settings", padding=8)
        legend_frame.pack(fill="x", pady=(0, 6))

        ll_grid = ttk.Frame(legend_frame)
        ll_grid.pack(fill="x")
        ll_grid.columnconfigure(1, weight=1)

        ttk.Label(ll_grid, text="Daily Attacks:").grid(row=0, column=0, sticky="w", pady=2)
        self._ll_daily_var = tk.StringVar(
            value=str(self.controller.config.get("legend_league.daily_attack_limit", 8)))
        ttk.Entry(ll_grid, textvariable=self._ll_daily_var, width=6).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(ll_grid, text="Window Start (UTC):").grid(row=1, column=0, sticky="w", pady=2)
        self._ll_start_var = tk.StringVar(
            value=str(self.controller.config.get("legend_league.window_start_utc", "00:00")))
        ttk.Entry(ll_grid, textvariable=self._ll_start_var, width=8).grid(row=1, column=1, sticky="w", padx=6)

        ttk.Label(ll_grid, text="Window End (UTC):").grid(row=2, column=0, sticky="w", pady=2)
        self._ll_end_var = tk.StringVar(
            value=str(self.controller.config.get("legend_league.window_end_utc", "23:59")))
        ttk.Entry(ll_grid, textvariable=self._ll_end_var, width=8).grid(row=2, column=1, sticky="w", padx=6)

        self._ll_wait_var = tk.BooleanVar(
            value=bool(self.controller.config.get("legend_league.wait_for_window", True)))
        ttk.Checkbutton(legend_frame, text="Wait for window to open",
                        variable=self._ll_wait_var).pack(anchor="w", pady=(4, 0))

        self._ll_ai_var = tk.BooleanVar(
            value=bool(self.controller.config.get("legend_league.ai_strategy_enabled", False)))
        ttk.Checkbutton(legend_frame, text="AI strategy analysis (experimental)",
                        variable=self._ll_ai_var).pack(anchor="w")

        ttk.Button(legend_frame, text="Save Legend Settings", style="Accent.TButton",
                   command=self._save_legend_settings).pack(anchor="w", pady=(6, 0))

        ctrl_frame = ttk.LabelFrame(right, text="Control", padding=8)
        ctrl_frame.pack(fill="x")

        self._auto_start_btn = ttk.Button(ctrl_frame, text="▶  Start Auto Attack", style="Green.TButton",
                                          command=self._dashboard_start)
        self._auto_start_btn.pack(fill="x", pady=3)
        self._auto_stop_btn = ttk.Button(ctrl_frame, text="■  Stop Auto Attack", style="Red.TButton",
                                         command=self._dashboard_stop)
        self._auto_stop_btn.pack(fill="x", pady=3)
        ttk.Button(ctrl_frame, text="Validate Config", command=self._auto_validate).pack(fill="x", pady=3)

        val_frame = ttk.LabelFrame(right, text="Validation Results", padding=8)
        val_frame.pack(fill="both", expand=True, pady=(8, 0))

        self._auto_validate_text = tk.Text(val_frame, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                                           relief="flat", font=("Consolas", 9))
        val_vsb = ttk.Scrollbar(val_frame, orient="vertical", command=self._auto_validate_text.yview)
        self._auto_validate_text.configure(yscrollcommand=val_vsb.set)
        self._auto_validate_text.pack(side="left", fill="both", expand=True)
        val_vsb.pack(side="right", fill="y")
        self._auto_validate_text.config(state="disabled")

        self._auto_refresh_tree()

    def _auto_refresh_tree(self):
        for item in self._auto_tree.get_children():
            self._auto_tree.delete(item)
        sessions = self.controller.auto_attacker.attack_sessions
        for group, variations in sessions.items():
            parent = self._auto_tree.insert("", "end", text=group, values=("",), open=True)
            if isinstance(variations, list):
                for var in variations:
                    self._auto_tree.insert(parent, "end", text="", values=(var,))

    def _auto_add_group(self):
        name = simpledialog.askstring("Add Group", "Group name:", parent=self.root)
        if not name:
            return
        if name not in self.controller.auto_attacker.attack_sessions:
            self.controller.auto_attacker.attack_sessions[name] = []
        self._auto_refresh_tree()

    def _auto_add_variation(self):
        sessions = self.controller.auto_attacker.attack_sessions
        groups = list(sessions.keys())
        recordings = self.controller.list_recorded_attacks()

        if not groups:
            messagebox.showwarning("No Groups", "Create a group first.", parent=self.root)
            return
        if not recordings:
            messagebox.showwarning("No Recordings", "No recordings available.", parent=self.root)
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Add Variation")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set()

        ttk.Label(dlg, text="Group:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        group_var = tk.StringVar(value=groups[0])
        ttk.Combobox(dlg, textvariable=group_var, values=groups, state="readonly").grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(dlg, text="Recording:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        rec_var = tk.StringVar(value=recordings[0])
        ttk.Combobox(dlg, textvariable=rec_var, values=recordings, state="readonly").grid(row=1, column=1, padx=8, pady=6)

        def confirm():
            self.controller.auto_attacker.add_attack_session(group_var.get(), rec_var.get())
            self._auto_refresh_tree()
            dlg.destroy()

        ttk.Button(dlg, text="Add", command=confirm).grid(row=2, column=0, columnspan=2, pady=8)

    def _auto_remove(self):
        sel = self._auto_tree.selection()
        if not sel:
            return
        item = sel[0]
        parent = self._auto_tree.parent(item)
        if parent:
            group = self._auto_tree.item(parent, "text")
            variation = self._auto_tree.item(item, "values")[0]
            self.controller.auto_attacker.remove_attack_session(group, variation)
        else:
            group = self._auto_tree.item(item, "text")
            self.controller.auto_attacker.remove_attack_session(group)
        self._auto_refresh_tree()

    def _auto_save(self):
        try:
            self.controller.config.set("auto_attacker.attack_sessions",
                                       self.controller.auto_attacker.attack_sessions)
            self.controller.config.save_config()
            messagebox.showinfo("Saved", "Attack sessions saved.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def _save_legend_settings(self):
        try:
            self.controller.config.set("legend_league.daily_attack_limit",
                                       int(self._ll_daily_var.get()))
            self.controller.config.set("legend_league.window_start_utc",
                                       self._ll_start_var.get().strip())
            self.controller.config.set("legend_league.window_end_utc",
                                       self._ll_end_var.get().strip())
            self.controller.config.set("legend_league.wait_for_window", self._ll_wait_var.get())
            self.controller.config.set("legend_league.ai_strategy_enabled", self._ll_ai_var.get())
            self.controller.config.save_config()
            messagebox.showinfo("Saved", "Legend League settings saved.", parent=self.root)
        except (ValueError, TypeError) as e:
            messagebox.showerror("Invalid", f"Could not save: {e}", parent=self.root)

    def _auto_validate(self):
        ok, errors = self.controller.validate_auto_attack_config()
        self._auto_validate_text.config(state="normal")
        self._auto_validate_text.delete("1.0", "end")
        if ok:
            self._auto_validate_text.insert("end", "✓ Config is valid.\n", "ok")
        else:
            for err in errors:
                self._auto_validate_text.insert("end", f"✗ {err}\n")
        self._auto_validate_text.config(state="disabled")

    def _build_strategy_tab(self):
        canvas_frame = ttk.Frame(self._tab_strategy)
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        outer, deploy_frame = self._card(scrollable_frame, "⚡ Deploy Speed Settings", padx=4, pady=4)
        outer.pack(fill="x")
        
        deploy_grid = ttk.Frame(deploy_frame)
        deploy_grid.pack(fill="x")
        deploy_grid.columnconfigure(1, weight=1)
        
        ttk.Label(deploy_grid, text="Wave Deployment Speed (1-Fast, 9-Slow):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self._strategy_wave_speed = tk.IntVar(value=self.controller.config.get("attack_strategy.deploy_speed.wave_deployment_speed", 8))
        wave_scale = ttk.Scale(deploy_grid, from_=1, to=9, variable=self._strategy_wave_speed, orient="horizontal")
        wave_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._strategy_wave_label = ttk.Label(deploy_grid, text="8", font=("Segoe UI", 9, "bold"), foreground=ACCENT, width=2)
        self._strategy_wave_label.grid(row=0, column=2, padx=8)
        wave_scale.configure(command=lambda v: self._strategy_wave_label.config(text=str(int(float(v)))))
        
        ttk.Label(deploy_grid, text="Troop Deployment Speed (1-Fast, 9-Slow):", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
        self._strategy_troop_speed = tk.IntVar(value=self.controller.config.get("attack_strategy.deploy_speed.troop_deployment_speed", 7))
        troop_scale = ttk.Scale(deploy_grid, from_=1, to=9, variable=self._strategy_troop_speed, orient="horizontal")
        troop_scale.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._strategy_troop_label = ttk.Label(deploy_grid, text="7", font=("Segoe UI", 9, "bold"), foreground=ACCENT, width=2)
        self._strategy_troop_label.grid(row=1, column=2, padx=8)
        troop_scale.configure(command=lambda v: self._strategy_troop_label.config(text=str(int(float(v)))))
        
        outer, strategy_frame = self._card(scrollable_frame, "🎯 Attack Strategy Settings", padx=4, pady=4)
        outer.pack(fill="x")
        
        outer, sides_frame = self._card(strategy_frame, "Attack Sides", padx=0, pady=4)
        outer.pack(fill="x")
        
        sides_grid = ttk.Frame(sides_frame)
        sides_grid.pack(fill="x")
        
        attack_sides = self.controller.config.get("attack_strategy.strategy.attack_sides", {"NW": True, "NE": True, "SW": True, "SE": True})
        
        self._strategy_nw = tk.BooleanVar(value=attack_sides.get("NW", True))
        self._strategy_ne = tk.BooleanVar(value=attack_sides.get("NE", True))
        self._strategy_sw = tk.BooleanVar(value=attack_sides.get("SW", True))
        self._strategy_se = tk.BooleanVar(value=attack_sides.get("SE", True))
        
        ttk.Checkbutton(sides_grid, text="🔼 North-West", variable=self._strategy_nw).pack(anchor="w", pady=2)
        ttk.Checkbutton(sides_grid, text="🔼 North-East", variable=self._strategy_ne).pack(anchor="w", pady=2)
        ttk.Checkbutton(sides_grid, text="🔽 South-West", variable=self._strategy_sw).pack(anchor="w", pady=2)
        ttk.Checkbutton(sides_grid, text="🔽 South-East", variable=self._strategy_se).pack(anchor="w", pady=2)
        
        ttk.Separator(strategy_frame, style="TSeparator").pack(fill="x", pady=6)
        
        split_grid = ttk.Frame(strategy_frame)
        split_grid.pack(fill="x", pady=4)
        split_grid.columnconfigure(1, weight=1)
        
        ttk.Label(split_grid, text="Split Attack into Waves (1-3):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self._strategy_waves = tk.IntVar(value=self.controller.config.get("attack_strategy.strategy.split_waves", 1))
        waves_scale = ttk.Scale(split_grid, from_=1, to=3, variable=self._strategy_waves, orient="horizontal")
        waves_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._strategy_waves_label = ttk.Label(split_grid, text="1", font=("Segoe UI", 9, "bold"), foreground=ACCENT, width=2)
        self._strategy_waves_label.grid(row=0, column=2, padx=8)
        waves_scale.configure(command=lambda v: self._strategy_waves_label.config(text=str(int(float(v)))))
        
        ttk.Separator(strategy_frame, style="TSeparator").pack(fill="x", pady=6)
        
        self._strategy_red_lines = tk.BooleanVar(value=self.controller.config.get("attack_strategy.strategy.deploy_near_red_lines", True))
        ttk.Checkbutton(strategy_frame, text="✓ Deploy near red lines (defenses)", variable=self._strategy_red_lines).pack(anchor="w", pady=2)
        
        self._strategy_collectors = tk.BooleanVar(value=self.controller.config.get("attack_strategy.strategy.deploy_near_collectors", True))
        ttk.Checkbutton(strategy_frame, text="✓ Deploy near collectors", variable=self._strategy_collectors).pack(anchor="w", pady=2)
        
        outer, hero_frame = self._card(scrollable_frame, "⚔ Hero Ability Settings", padx=4, pady=4)
        outer.pack(fill="x")
        
        hero_grid = ttk.Frame(hero_frame)
        hero_grid.pack(fill="x")
        hero_grid.columnconfigure(1, weight=1)
        
        self._hero_enabled = tk.BooleanVar(value=self.controller.config.get("attack_strategy.hero_ability.enabled", True))
        ttk.Checkbutton(hero_frame, text="✓ Activate hero abilities", variable=self._hero_enabled).pack(anchor="w", pady=4)
        
        ttk.Label(hero_grid, text="Activate after (seconds):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self._hero_delay = tk.IntVar(value=self.controller.config.get("attack_strategy.hero_ability.activate_after_seconds", 10))
        hero_scale = ttk.Scale(hero_grid, from_=5, to=60, variable=self._hero_delay, orient="horizontal")
        hero_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._hero_delay_label = ttk.Label(hero_grid, text="10s", font=("Segoe UI", 9, "bold"), foreground=ACCENT, width=4)
        self._hero_delay_label.grid(row=0, column=2, padx=8)
        hero_scale.configure(command=lambda v: self._hero_delay_label.config(text=f"{int(float(v))}s"))
        
        outer, end_battle_frame = self._card(scrollable_frame, "⏹ End Battle Settings", padx=4, pady=4)
        outer.pack(fill="x")
        
        end_grid = ttk.Frame(end_battle_frame)
        end_grid.pack(fill="x")
        end_grid.columnconfigure(1, weight=1)
        
        self._end_battle_enabled = tk.BooleanVar(value=self.controller.config.get("attack_strategy.end_battle.enabled", True))
        ttk.Checkbutton(end_battle_frame, text="✓ Auto-end battle if no resources", variable=self._end_battle_enabled).pack(anchor="w", pady=4)
        
        ttk.Label(end_grid, text="No resources timeout (seconds):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
        self._end_battle_timeout = tk.IntVar(value=self.controller.config.get("attack_strategy.end_battle.end_if_no_resources_for_seconds", 10))
        end_scale = ttk.Scale(end_grid, from_=5, to=30, variable=self._end_battle_timeout, orient="horizontal")
        end_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)
        self._end_battle_label = ttk.Label(end_grid, text="10s", font=("Segoe UI", 9, "bold"), foreground=ACCENT, width=4)
        self._end_battle_label.grid(row=0, column=2, padx=8)
        end_scale.configure(command=lambda v: self._end_battle_label.config(text=f"{int(float(v))}s"))
        
        outer, human_frame = self._card(scrollable_frame, "🔒 Human-Like Behavior (⚠️ SECURITY)", padx=4, pady=4)
        outer.pack(fill="x")
        
        ttk.Label(human_frame, text="⚠️  Disabling these features increases detection risk!", font=("Segoe UI", 8), foreground=RED).pack(anchor="w", pady=4)
        
        ttk.Separator(human_frame, style="TSeparator").pack(fill="x", pady=4)
        
        self._human_mouse_parking = tk.BooleanVar(value=self.controller.config.get("attack_strategy.human_like_variations.enable_mouse_parking", True))
        ttk.Checkbutton(human_frame, text="✓ Park mouse between actions", variable=self._human_mouse_parking).pack(anchor="w", pady=2)
        
        self._human_hesitation = tk.BooleanVar(value=self.controller.config.get("attack_strategy.human_like_variations.enable_hesitation", True))
        ttk.Checkbutton(human_frame, text="✓ Add human-like hesitations", variable=self._human_hesitation).pack(anchor="w", pady=2)
        
        hesitation_grid = ttk.Frame(human_frame)
        hesitation_grid.pack(fill="x", pady=(4, 0))
        hesitation_grid.columnconfigure(1, weight=1)
        
        ttk.Label(hesitation_grid, text="Min hesitation (ms):", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", padx=(20, 0), pady=2)
        self._human_min_hes = tk.IntVar(value=self.controller.config.get("attack_strategy.human_like_variations.min_hesitation_ms", 200))
        ttk.Entry(hesitation_grid, textvariable=self._human_min_hes, width=6).grid(row=0, column=1, sticky="w", padx=8, pady=2)
        
        ttk.Label(hesitation_grid, text="Max hesitation (ms):", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", padx=(20, 0), pady=2)
        self._human_max_hes = tk.IntVar(value=self.controller.config.get("attack_strategy.human_like_variations.max_hesitation_ms", 800))
        ttk.Entry(hesitation_grid, textvariable=self._human_max_hes, width=6).grid(row=1, column=1, sticky="w", padx=8, pady=2)
        
        ttk.Separator(human_frame, style="TSeparator").pack(fill="x", pady=4)
        
        variance_grid = ttk.Frame(human_frame)
        variance_grid.pack(fill="x")
        variance_grid.columnconfigure(1, weight=1)
        
        ttk.Label(variance_grid, text="Click variance (pixels):", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self._human_variance = tk.IntVar(value=self.controller.config.get("attack_strategy.human_like_variations.coordinate_variance_pixels", 5))
        variance_scale = ttk.Scale(variance_grid, from_=0, to=15, variable=self._human_variance, orient="horizontal")
        variance_scale.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)
        self._human_variance_label = ttk.Label(variance_grid, text="5", font=("Segoe UI", 8, "bold"), foreground=ACCENT, width=2)
        self._human_variance_label.grid(row=0, column=2, padx=8)
        variance_scale.configure(command=lambda v: self._human_variance_label.config(text=str(int(float(v)))))
        
        ttk.Label(variance_grid, text="Click jitter (pixels):", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self._human_jitter = tk.IntVar(value=self.controller.config.get("attack_strategy.human_like_variations.click_jitter_pixels", 3))
        jitter_scale = ttk.Scale(variance_grid, from_=0, to=10, variable=self._human_jitter, orient="horizontal")
        jitter_scale.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)
        self._human_jitter_label = ttk.Label(variance_grid, text="3", font=("Segoe UI", 8, "bold"), foreground=ACCENT, width=2)
        self._human_jitter_label.grid(row=1, column=2, padx=8)
        jitter_scale.configure(command=lambda v: self._human_jitter_label.config(text=str(int(float(v)))))
        
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", pady=(8, 0))
        
        ttk.Button(button_frame, text="💾 Save Strategy Settings", style="Green.TButton", command=self._save_strategy_settings).pack(side="left", padx=4, fill="x", expand=True)
        ttk.Button(button_frame, text="🔄 Reset to Defaults", style="Accent.TButton", command=self._reset_strategy_defaults).pack(side="left", padx=4)

    def _save_strategy_settings(self):
        try:
            strategy_config = {
                'deploy_speed': {
                    'wave_deployment_speed': self._strategy_wave_speed.get(),
                    'troop_deployment_speed': self._strategy_troop_speed.get()
                },
                'strategy': {
                    'attack_sides': {
                        'NW': self._strategy_nw.get(),
                        'NE': self._strategy_ne.get(),
                        'SW': self._strategy_sw.get(),
                        'SE': self._strategy_se.get()
                    },
                    'split_waves': self._strategy_waves.get(),
                    'deploy_near_red_lines': self._strategy_red_lines.get(),
                    'deploy_near_collectors': self._strategy_collectors.get()
                },
                'hero_ability': {
                    'enabled': self._hero_enabled.get(),
                    'activate_after_seconds': self._hero_delay.get()
                },
                'end_battle': {
                    'enabled': self._end_battle_enabled.get(),
                    'end_if_no_resources_for_seconds': self._end_battle_timeout.get()
                },
                'human_like_variations': {
                    'enable_mouse_parking': self._human_mouse_parking.get(),
                    'enable_hesitation': self._human_hesitation.get(),
                    'min_hesitation_ms': self._human_min_hes.get(),
                    'max_hesitation_ms': self._human_max_hes.get(),
                    'coordinate_variance_pixels': self._human_variance.get(),
                    'click_jitter_pixels': self._human_jitter.get()
                }
            }
            
            self.controller.config.set("attack_strategy", strategy_config)
            self.controller.config.save_config()
            messagebox.showinfo("✓ Saved", "Attack strategy settings saved successfully.", parent=self.root)
        except (ValueError, TypeError) as e:
            messagebox.showerror("✗ Error", f"Could not save settings: {e}", parent=self.root)
    
    def _reset_strategy_defaults(self):
        if messagebox.askyesno("Reset Defaults", "Reset all strategy settings to defaults?", parent=self.root):
            defaults = AttackStrategyConfig.default()
            
            self._strategy_wave_speed.set(defaults.deploy_speed.wave_deployment_speed)
            self._strategy_troop_speed.set(defaults.deploy_speed.troop_deployment_speed)
            
            self._strategy_nw.set(defaults.strategy.attack_sides['NW'])
            self._strategy_ne.set(defaults.strategy.attack_sides['NE'])
            self._strategy_sw.set(defaults.strategy.attack_sides['SW'])
            self._strategy_se.set(defaults.strategy.attack_sides['SE'])
            
            self._strategy_waves.set(defaults.strategy.split_waves)
            self._strategy_red_lines.set(defaults.strategy.deploy_near_red_lines)
            self._strategy_collectors.set(defaults.strategy.deploy_near_collectors)
            
            self._hero_enabled.set(defaults.hero_ability.enabled)
            self._hero_delay.set(defaults.hero_ability.activate_after_seconds)
            
            self._end_battle_enabled.set(defaults.end_battle.enabled)
            self._end_battle_timeout.set(defaults.end_battle.end_if_no_resources_for_seconds)
            
            self._human_mouse_parking.set(defaults.human_like_variations.enable_mouse_parking)
            self._human_hesitation.set(defaults.human_like_variations.enable_hesitation)
            self._human_min_hes.set(defaults.human_like_variations.min_hesitation_ms)
            self._human_max_hes.set(defaults.human_like_variations.max_hesitation_ms)
            self._human_variance.set(defaults.human_like_variations.coordinate_variance_pixels)
            self._human_jitter.set(defaults.human_like_variations.click_jitter_pixels)

    def _build_recorder_tab(self):
        left = ttk.Frame(self._tab_recorder)
        left.pack(side="left", fill="both", padx=(8, 4), pady=8, expand=False)
        left.configure(width=220)

        right = ttk.Frame(self._tab_recorder)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        list_frame = ttk.LabelFrame(left, text="Recordings", padding=6)
        list_frame.pack(fill="both", expand=True)

        list_sb = ttk.Scrollbar(list_frame, orient="vertical")
        self._rec_listbox = tk.Listbox(list_frame, bg=BG, fg=TEXT, selectbackground=ACCENT,
                                       selectforeground="#FFFFFF", relief="flat", font=("Segoe UI", 10),
                                       borderwidth=0, yscrollcommand=list_sb.set)
        list_sb.config(command=self._rec_listbox.yview)
        self._rec_listbox.pack(side="left", fill="both", expand=True)
        list_sb.pack(side="right", fill="y")
        self._rec_listbox.bind("<<ListboxSelect>>", self._on_rec_select)

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=(4, 0))
        ttk.Button(btn_row, text="Refresh", command=self._rec_refresh).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Rename", command=self._rec_rename).pack(side="left", padx=2)
        ttk.Button(btn_row, text="Delete", command=self._rec_delete).pack(side="left", padx=2)

        rec_card, rec_inner = self._card(right, "Record")
        rec_card.pack(fill="x", pady=(0, 4))

        name_row = ttk.Frame(rec_inner, style="Card.TFrame")
        name_row.pack(fill="x", pady=(0, 4))
        ttk.Label(name_row, text="Name:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self._rec_name_entry = ttk.Entry(name_row)
        self._rec_name_entry.pack(side="left", fill="x", expand=True)

        rec_btn_row = ttk.Frame(rec_inner, style="Card.TFrame")
        rec_btn_row.pack(fill="x")
        ttk.Button(rec_btn_row, text="Start Recording", style="Green.TButton",
                   command=self._rec_start).pack(side="left", padx=(0, 4))
        ttk.Button(rec_btn_row, text="Stop Recording", style="Red.TButton",
                   command=self._rec_stop).pack(side="left")

        self._rec_status_lbl = ttk.Label(rec_inner, text="Idle", style="Card.TLabel", foreground=SUBTEXT)
        self._rec_status_lbl.pack(anchor="w", pady=(4, 0))

        play_card, play_inner = self._card(right, "Playback")
        play_card.pack(fill="x", pady=(0, 4))

        speed_row = ttk.Frame(play_inner, style="Card.TFrame")
        speed_row.pack(fill="x", pady=(0, 4))
        ttk.Label(speed_row, text="Speed:", style="Card.TLabel").pack(side="left", padx=(0, 4))
        self._play_speed_var = tk.DoubleVar(value=1.0)
        self._play_speed_lbl = ttk.Label(speed_row, text="1.00x", style="Card.TLabel", width=5)
        self._play_speed_lbl.pack(side="right")
        speed_scale = ttk.Scale(speed_row, from_=0.25, to=3.0, orient="horizontal",
                                variable=self._play_speed_var,
                                command=lambda v: self._play_speed_lbl.config(text=f"{float(v):.2f}x"))
        speed_scale.pack(side="left", fill="x", expand=True)

        play_btn_row = ttk.Frame(play_inner, style="Card.TFrame")
        play_btn_row.pack(fill="x")
        ttk.Button(play_btn_row, text="Play", style="Green.TButton",
                   command=self._rec_play).pack(side="left", padx=(0, 4))
        ttk.Button(play_btn_row, text="Stop", style="Red.TButton",
                   command=self._rec_play_stop).pack(side="left")

        self._play_status_lbl = ttk.Label(play_inner, text="Idle", style="Card.TLabel", foreground=SUBTEXT)
        self._play_status_lbl.pack(anchor="w", pady=(4, 0))

        info_card, info_inner = self._card(right, "Recording Info")
        info_card.pack(fill="both", expand=True)

        self._rec_info_text = tk.Text(info_inner, bg=BG, fg=TEXT, insertbackground=TEXT,
                                      relief="flat", font=("Consolas", 9), height=6, borderwidth=0)
        self._rec_info_text.pack(fill="both", expand=True)
        self._rec_info_text.config(state="disabled")

        self._rec_refresh()

    def _rec_refresh(self):
        self._rec_listbox.delete(0, "end")
        for name in self.controller.list_recorded_attacks():
            self._rec_listbox.insert("end", name)

    def _on_rec_select(self, event=None):
        sel = self._rec_listbox.curselection()
        if not sel:
            return
        name = self._rec_listbox.get(sel[0])
        self._rec_name_entry.delete(0, "end")
        self._rec_name_entry.insert(0, name)
        try:
            info = self.controller.attack_recorder.get_recording_info(name)
            self._rec_info_text.config(state="normal")
            self._rec_info_text.delete("1.0", "end")
            self._rec_info_text.insert("end", f"Name:     {info.get('name', name)}\n")
            self._rec_info_text.insert("end", f"Created:  {info.get('created', 'N/A')}\n")
            self._rec_info_text.insert("end", f"Duration: {info.get('duration', 0):.1f}s\n")
            self._rec_info_text.insert("end", f"Actions:  {info.get('action_count', 0)}\n")
            types = info.get("action_types", {})
            if types:
                self._rec_info_text.insert("end", "Breakdown:\n")
                for k, v in types.items():
                    self._rec_info_text.insert("end", f"  {k}: {v}\n")
            self._rec_info_text.config(state="disabled")
        except Exception:
            pass

    def _rec_start(self):
        name = self._rec_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Enter a recording name.", parent=self.root)
            return
        self.controller.start_attack_recording(name)
        self._rec_status_lbl.config(text="Recording...", foreground=RED)

    def _rec_stop(self):
        self.controller.stop_attack_recording()
        self._rec_status_lbl.config(text="Stopped", foreground=SUBTEXT)
        self._rec_refresh()

    def _rec_play(self):
        sel = self._rec_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Recording", "Select a recording to play.", parent=self.root)
            return
        name = self._rec_listbox.get(sel[0])

        def _play():
            self.root.after(0, lambda: self._play_status_lbl.config(text="Playing...", foreground=GREEN))
            self.controller.play_attack(name)
            self.root.after(0, lambda: self._play_status_lbl.config(text="Done", foreground=SUBTEXT))

        threading.Thread(target=_play, daemon=True).start()

    def _rec_play_stop(self):
        self.controller.attack_player.stop_playback()
        self._play_status_lbl.config(text="Stopped", foreground=SUBTEXT)

    def _rec_rename(self):
        sel = self._rec_listbox.curselection()
        if not sel:
            return
        old = self._rec_listbox.get(sel[0])
        new = simpledialog.askstring("Rename", f"New name for '{old}':", parent=self.root)
        if not new:
            return
        if self.controller.attack_recorder.rename_recording(old, new):
            self._rec_refresh()
        else:
            messagebox.showerror("Error", "Rename failed.", parent=self.root)

    def _rec_delete(self):
        sel = self._rec_listbox.curselection()
        if not sel:
            return
        name = self._rec_listbox.get(sel[0])
        if not messagebox.askyesno("Delete", f"Delete '{name}'?", parent=self.root):
            return
        if self.controller.attack_recorder.delete_recording(name):
            self._rec_refresh()
        else:
            messagebox.showerror("Error", "Delete failed.", parent=self.root)

    def _build_coords_tab(self):
        left = ttk.Frame(self._tab_coords)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        right = ttk.Frame(self._tab_coords)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        tree_frame = ttk.LabelFrame(left, text="Mapped Coordinates", padding=6)
        tree_frame.pack(fill="both", expand=True)

        cols = ("x", "y")
        self._coord_tree = ttk.Treeview(tree_frame, columns=cols, show="headings tree", selectmode="browse")
        self._coord_tree.heading("#0", text="Button Name")
        self._coord_tree.heading("x", text="X")
        self._coord_tree.heading("y", text="Y")
        self._coord_tree.column("#0", width=180)
        self._coord_tree.column("x", width=70)
        self._coord_tree.column("y", width=70)

        coord_vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._coord_tree.yview)
        self._coord_tree.configure(yscrollcommand=coord_vsb.set)
        self._coord_tree.pack(side="left", fill="both", expand=True)
        coord_vsb.pack(side="right", fill="y")

        coord_btns = ttk.Frame(left)
        coord_btns.pack(fill="x", pady=(4, 0))
        ttk.Button(coord_btns, text="Refresh", command=self._coord_refresh).pack(side="left", padx=2)
        ttk.Button(coord_btns, text="Add/Edit", command=self._coord_add_edit).pack(side="left", padx=2)
        ttk.Button(coord_btns, text="Capture Mouse", command=self._coord_capture).pack(side="left", padx=2)
        ttk.Button(coord_btns, text="Delete", command=self._coord_delete).pack(side="left", padx=2)
        ttk.Button(coord_btns, text="Save", command=self._coord_save).pack(side="left", padx=2)

        self._req_frame = ttk.LabelFrame(right, text="Required Buttons Status", padding=8)
        self._req_frame.pack(fill="x", pady=(0, 6))

        self._req_labels = {}
        self._req_label_frames = {}

        wizard_frame = ttk.LabelFrame(right, text="Mapping Wizard", padding=8)
        wizard_frame.pack(fill="x", pady=(0, 6))

        ttk.Button(wizard_frame, text="Start Mapping Wizard",
                   command=self._coord_wizard).pack(fill="x")

        val_frame = ttk.LabelFrame(right, text="Validate", padding=8)
        val_frame.pack(fill="both", expand=True)

        ttk.Button(val_frame, text="Validate Coordinates", command=self._coord_validate).pack(fill="x", pady=(0, 4))
        self._coord_val_text = tk.Text(val_frame, bg=BG, fg=TEXT, insertbackground=TEXT,
                                       relief="flat", font=("Consolas", 9), borderwidth=0)
        val_vsb = ttk.Scrollbar(val_frame, orient="vertical", command=self._coord_val_text.yview)
        self._coord_val_text.configure(yscrollcommand=val_vsb.set)
        self._coord_val_text.pack(side="left", fill="both", expand=True)
        val_vsb.pack(side="right", fill="y")
        self._coord_val_text.config(state="disabled")

        self._rebuild_required_buttons()
        self._coord_refresh()

    def _coord_refresh(self):
        for item in self._coord_tree.get_children():
            self._coord_tree.delete(item)
        coords = self.controller.get_mapped_coordinates()
        for name, data in coords.items():
            if isinstance(data, dict):
                x, y = data.get("x", ""), data.get("y", "")
            elif isinstance(data, (list, tuple)) and len(data) >= 2:
                x, y = data[0], data[1]
            else:
                x, y = data, ""
            self._coord_tree.insert("", "end", text=name, values=(x, y))
        self._coord_update_required_status(coords)

    def _coord_update_required_status(self, coords):
        for btn_key, dot in self._req_labels.items():
            if btn_key in coords:
                dot.config(fg=GREEN)
            else:
                dot.config(fg=RED)

    def _rebuild_required_buttons(self):
        for row in self._req_label_frames.values():
            row.destroy()
        self._req_labels.clear()
        self._req_label_frames.clear()

        mode = self.controller.get_attack_mode()
        if mode == 'legend':
            buttons = self.controller.get_required_buttons_legend()
        else:
            buttons = self.controller.get_required_buttons()

        for btn_key, desc in buttons.items():
            row = ttk.Frame(self._req_frame, style="Card.TFrame")
            row.pack(fill="x", pady=1)
            dot = tk.Label(row, text="●", bg=FRAME_BG, fg=RED, font=("Segoe UI", 10))
            dot.pack(side="left", padx=(0, 4))
            ttk.Label(row, text=f"{btn_key}: {desc}", style="Card.TLabel",
                      font=("Segoe UI", 8)).pack(side="left")
            self._req_labels[btn_key] = dot
            self._req_label_frames[btn_key] = row

        coords = self.controller.get_mapped_coordinates()
        self._coord_update_required_status(coords)

    def _coord_add_edit(self):
        sel = self._coord_tree.selection()
        init_name, init_x, init_y = "", "", ""
        if sel:
            init_name = self._coord_tree.item(sel[0], "text")
            vals = self._coord_tree.item(sel[0], "values")
            if vals:
                init_x = vals[0] if len(vals) > 0 else ""
                init_y = vals[1] if len(vals) > 1 else ""

        dlg = tk.Toplevel(self.root)
        dlg.title("Add/Edit Coordinate")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set()

        ttk.Label(dlg, text="Name:").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        name_e = ttk.Entry(dlg)
        name_e.insert(0, init_name)
        name_e.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(dlg, text="X:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        x_e = ttk.Entry(dlg)
        x_e.insert(0, str(init_x))
        x_e.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(dlg, text="Y:").grid(row=2, column=0, padx=8, pady=6, sticky="w")
        y_e = ttk.Entry(dlg)
        y_e.insert(0, str(init_y))
        y_e.grid(row=2, column=1, padx=8, pady=6)

        def confirm():
            n = name_e.get().strip()
            try:
                cx, cy = int(x_e.get()), int(y_e.get())
            except ValueError:
                messagebox.showerror("Invalid", "X and Y must be integers.", parent=dlg)
                return
            self.controller.coordinate_mapper.add_coordinate(n, cx, cy)
            self._coord_refresh()
            dlg.destroy()

        ttk.Button(dlg, text="Save", command=confirm).grid(row=3, column=0, columnspan=2, pady=8)

    def _coord_capture(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Capture Mouse Position")
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set()

        ttk.Label(dlg, text="Move your mouse to the target position:", foreground=TEXT).pack(padx=16, pady=8)

        pos_lbl = ttk.Label(dlg, text="X: 0  Y: 0", foreground=ACCENT, font=("Consolas", 14))
        pos_lbl.pack(pady=4)

        captured = {}

        def update_pos():
            try:
                import pyautogui
                x, y = pyautogui.position()
            except Exception:
                try:
                    from ctypes import windll, wintypes, byref
                    pt = wintypes.POINT()
                    windll.user32.GetCursorPos(byref(pt))
                    x, y = pt.x, pt.y
                except Exception:
                    x, y = 0, 0
            pos_lbl.config(text=f"X: {x}  Y: {y}")
            captured["x"] = x
            captured["y"] = y
            if dlg.winfo_exists():
                dlg.after(100, update_pos)

        update_pos()

        def do_capture():
            name = simpledialog.askstring("Name", "Coordinate name:", parent=dlg)
            if not name:
                return
            self.controller.coordinate_mapper.add_coordinate(name, captured.get("x", 0), captured.get("y", 0))
            self._coord_refresh()
            dlg.destroy()

        ttk.Button(dlg, text="Capture", style="Accent.TButton", command=do_capture).pack(pady=8)
        ttk.Button(dlg, text="Cancel", command=dlg.destroy).pack(pady=(0, 8))

    def _coord_delete(self):
        sel = self._coord_tree.selection()
        if not sel:
            return
        name = self._coord_tree.item(sel[0], "text")
        if messagebox.askyesno("Delete", f"Delete coordinate '{name}'?", parent=self.root):
            self.controller.coordinate_mapper.remove_coordinate(name)
            self._coord_refresh()

    def _coord_save(self):
        self.controller.coordinate_mapper.save_coordinates()
        messagebox.showinfo("Saved", "Coordinates saved.", parent=self.root)

    def _coord_wizard(self):
        messagebox.showinfo("Mapping Wizard",
                            "The coordinate mapping wizard will now start.\n\nPlease switch to the console/terminal window and follow the instructions there.",
                            parent=self.root)
        threading.Thread(target=self.controller.start_coordinate_mapping, daemon=True).start()

    def _coord_validate(self):
        mode = self.controller.get_attack_mode()
        if mode == 'legend':
            required = self.controller.get_required_buttons_legend()
        else:
            required = self.controller.get_required_buttons()
        
        coords = self.controller.get_mapped_coordinates()
        self._coord_val_text.config(state="normal")
        self._coord_val_text.delete("1.0", "end")
        
        self._coord_val_text.insert("end", f"Mode: {mode.upper()}\n\n")
        
        for btn_key in required.keys():
            marker = "✓" if btn_key in coords else "✗"
            self._coord_val_text.insert("end", f"{marker} {btn_key}\n")
        
        self._coord_val_text.config(state="disabled")

    def _build_scrollable_tab(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(event):
            canvas.itemconfig(win_id, width=event.width)

        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_resize)

        def on_mousewheel(event):
            if event.state & 0x4:
                if event.delta < 0:
                    canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        return inner

    def _labeled_entry(self, parent, label, row, config_key, width=24):
        ttk.Label(parent, text=label + ":").grid(row=row, column=0, sticky="w", padx=8, pady=3)
        var = tk.StringVar(value=str(self.controller.config.get(config_key, "")))
        entry = ttk.Entry(parent, textvariable=var, width=width)
        entry.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        return var

    def _labeled_check(self, parent, label, row, config_key):
        var = tk.BooleanVar(value=bool(self.controller.config.get(config_key, False)))
        cb = ttk.Checkbutton(parent, text=label, variable=var)
        cb.grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=3)
        return var

    def _section_label(self, parent, row, text):
        lbl = ttk.Label(parent, text=text, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        lbl.grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(12, 2))

    def _build_ai_tab(self):
        inner = self._build_scrollable_tab(self._tab_ai)
        inner.columnconfigure(1, weight=1)

        row = 0
        self._section_label(inner, row, "AI Analyzer Settings")
        row += 1

        self._ai_enabled_var = tk.BooleanVar(value=bool(self.controller.config.get("ai_analyzer.enabled", False)))
        ttk.Checkbutton(inner, text="Enable AI Analyzer", variable=self._ai_enabled_var).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=8, pady=4)
        row += 1

        ttk.Label(inner, text="API Key:").grid(row=row, column=0, sticky="w", padx=8, pady=3)
        api_frame = ttk.Frame(inner)
        api_frame.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        self._ai_key_var = tk.StringVar(value=self.controller.ai_analyzer.api_key or "")
        self._ai_key_entry = ttk.Entry(api_frame, textvariable=self._ai_key_var, show="*", width=30)
        self._ai_key_entry.pack(side="left", fill="x", expand=True)
        self._ai_key_show = tk.BooleanVar(value=False)

        def toggle_key():
            self._ai_key_entry.config(show="" if self._ai_key_show.get() else "*")

        ttk.Checkbutton(api_frame, text="Show", variable=self._ai_key_show,
                        command=toggle_key).pack(side="left", padx=4)
        ttk.Button(api_frame, text="Test Connection", command=self._ai_test).pack(side="left", padx=4)
        row += 1

        self._ai_gold_var = self._labeled_entry(inner, "Min Gold", row, "ai_analyzer.min_gold")
        row += 1
        self._ai_elixir_var = self._labeled_entry(inner, "Min Elixir", row, "ai_analyzer.min_elixir")
        row += 1
        self._ai_dark_var = self._labeled_entry(inner, "Min Dark Elixir", row, "ai_analyzer.min_dark_elixir")
        row += 1
        self._ai_th_var = self._labeled_entry(inner, "Max Town Hall", row, "ai_analyzer.max_townhall_level")
        row += 1

        ttk.Button(inner, text="Save AI Settings", style="Accent.TButton",
                   command=self._ai_save).grid(row=row, column=0, columnspan=2, pady=12, padx=8, sticky="w")

    def _ai_test(self):
        self.controller.ai_analyzer.api_key = self._ai_key_var.get()
        result = self.controller.test_ai_connection()
        if result:
            messagebox.showinfo("Connection Test", "AI connection successful!", parent=self.root)
        else:
            messagebox.showerror("Connection Test", "AI connection failed.", parent=self.root)

    def _ai_save(self):
        self.controller.config.set("ai_analyzer.enabled", self._ai_enabled_var.get())
        self.controller.ai_analyzer.api_key = self._ai_key_var.get()
        self.controller.config.set("ai_analyzer.google_gemini_api_key", self._ai_key_var.get())
        try:
            self.controller.config.set("ai_analyzer.min_gold", int(self._ai_gold_var.get()))
            self.controller.config.set("ai_analyzer.min_elixir", int(self._ai_elixir_var.get()))
            self.controller.config.set("ai_analyzer.min_dark_elixir", int(self._ai_dark_var.get()))
            self.controller.config.set("ai_analyzer.max_townhall_level", int(self._ai_th_var.get()))
        except ValueError:
            messagebox.showerror("Invalid", "Numeric fields must be integers.", parent=self.root)
            return
        self.controller.config.save_config()
        messagebox.showinfo("Saved", "AI settings saved.", parent=self.root)

    def _build_donation_tab(self):
        content = ttk.Frame(self._tab_donation)
        content.pack(fill="both", expand=True, padx=8, pady=8)
        
        controls_outer, controls = self._card(content, "Donation Controls")
        controls_outer.pack(fill="x", padx=(0, 4), pady=(0, 4))
        
        self._donation_is_running = False
        self._donation_thread = None
        
        run_frame = ttk.Frame(controls, style="Card.TFrame")
        run_frame.pack(fill="x", pady=(0, 6))
        
        self._donation_run_btn = ttk.Button(run_frame, text="▶ Run Donation Bot", style="Green.TButton", command=self._donation_start_bot)
        self._donation_run_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        self._donation_stop_btn = ttk.Button(run_frame, text="■ Stop", style="Red.TButton", command=self._donation_stop_bot)
        self._donation_stop_btn.pack(side="left", fill="x", expand=True, padx=(3, 0))
        self._donation_stop_btn.config(state="disabled")
        
        interval_frame = ttk.Frame(controls, style="Card.TFrame")
        interval_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(interval_frame, text="Check Interval (sec):", style="Card.TLabel", background=FRAME_BG).pack(side="left")
        self._donation_interval_var = tk.StringVar(value="30")
        interval_spin = ttk.Spinbox(interval_frame, from_=5, to=300, textvariable=self._donation_interval_var, width=10)
        interval_spin.pack(side="left", padx=(4, 0))
        

        
        status_outer, status = self._card(content, "Donation Status")
        status_outer.pack(fill="both", expand=True, padx=(4, 0))
        
        status_grid = ttk.Frame(status, style="Card.TFrame")
        status_grid.pack(fill="x", pady=(0, 8))
        
        ttk.Label(status_grid, text="Game Window:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=0, column=0, sticky="w")
        self._donation_window_status = ttk.Label(status_grid, text="Not detected", style="Card.TLabel", foreground=RED, background=FRAME_BG)
        self._donation_window_status.grid(row=0, column=1, sticky="w", padx=(8, 0))
        
        ttk.Label(status_grid, text="In Clan Chat:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._donation_clan_chat_status = ttk.Label(status_grid, text="Unknown", style="Card.TLabel", foreground=SUBTEXT, background=FRAME_BG)
        self._donation_clan_chat_status.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
        
        ttk.Label(status_grid, text="Available Troops:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=2, column=0, sticky="w", pady=(4, 0))
        self._donation_troops_status = ttk.Label(status_grid, text="—", style="Card.TLabel", foreground=SUBTEXT, background=FRAME_BG)
        self._donation_troops_status.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
        
        ttk.Label(status_grid, text="Available Spells:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=3, column=0, sticky="w", pady=(4, 0))
        self._donation_spells_status = ttk.Label(status_grid, text="—", style="Card.TLabel", foreground=SUBTEXT, background=FRAME_BG)
        self._donation_spells_status.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
        
        ttk.Label(status_grid, text="Donation Requests:", style="Card.TLabel", font=("Segoe UI", 9, "bold"), background=FRAME_BG).grid(row=4, column=0, sticky="w", pady=(4, 0))
        self._donation_requests_status = ttk.Label(status_grid, text="—", style="Card.TLabel", foreground=SUBTEXT, background=FRAME_BG)
        self._donation_requests_status.grid(row=4, column=1, sticky="w", padx=(8, 0), pady=(4, 0))
        
        ttk.Separator(status).pack(fill="x", pady=8)
        
        ttk.Label(status, text="Detection Details", style="CardTitle.TLabel", background=FRAME_BG).pack(anchor="w")
        
        self._donation_details = scrolledtext.ScrolledText(status, height=10, bg=ENTRY_BG, fg=TEXT,
                                           insertbackground=TEXT, relief="flat",
                                           font=("Consolas", 8), borderwidth=1)
        self._donation_details.pack(fill="both", expand=True, pady=(4, 0))
        self._donation_details.config(state="disabled")
    
    def _donation_log(self, msg: str, tag: str = "INFO"):
        self._donation_details.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._donation_details.insert("end", f"[{ts}] {msg}\n", tag)
        self._donation_details.see("end")
        self._donation_details.config(state="disabled")
    
    def _donation_detect_window(self):
        bounds = self.controller.get_game_window()
        if bounds:
            x, y, w, h = bounds
            self._donation_window_status.config(text=f"Detected at ({x}, {y}) - {w}x{h}", foreground=GREEN)
            self._donation_log(f"Game window detected: ({x}, {y}) {w}x{h}", "INFO")
        else:
            self._donation_window_status.config(text="Not found", foreground=RED)
            self._donation_log("Game window not found", "ERROR")
    
    def _donation_check_clan_chat(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        is_clan = self.controller.donation_detector.is_in_clan_chat(bounds)
        status_text = "Yes ✓" if is_clan else "No ✗"
        status_color = GREEN if is_clan else RED
        self._donation_clan_chat_status.config(text=status_text, foreground=status_color)
        self._donation_log(f"Clan chat check: {'In clan chat' if is_clan else 'Not in clan chat'}", "INFO")
    
    def _donation_scan_troops(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        troops = self.controller.donation_detector.get_available_troops(bounds)
        count = len(troops)
        self._donation_troops_status.config(text=f"{count} found", foreground=GREEN if count > 0 else RED)
        self._donation_log(f"Found {count} available troops to donate", "INFO")
        if troops:
            for i, (x, y) in enumerate(troops, 1):
                self._donation_log(f"  {i}. Troop at ({x}, {y})", "INFO")
    
    def _donation_scan_spells(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        spells = self.controller.donation_detector.get_available_spells(bounds)
        count = len(spells)
        self._donation_spells_status.config(text=f"{count} found", foreground=GREEN if count > 0 else RED)
        self._donation_log(f"Found {count} available spells to donate", "INFO")
        if spells:
            for i, (x, y) in enumerate(spells, 1):
                self._donation_log(f"  {i}. Spell at ({x}, {y})", "INFO")
    
    def _donation_detect_requests(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        requests = self.controller.donation_detector.detect_donation_requests(bounds)
        count = len(requests)
        self._donation_requests_status.config(text=f"{count} requests", foreground=GREEN if count > 0 else RED)
        self._donation_log(f"Found {count} donation requests", "INFO")
        if requests:
            for i, req in enumerate(requests, 1):
                name = req.get('member_name', 'Unknown')
                pos = req.get('position', (0, 0))
                self._donation_log(f"  {i}. {name} at {pos}", "INFO")
    
    def _donation_find_clan_button(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        chat_btn = self.controller.donation_detector.find_clan_chat_button(bounds)
        if chat_btn:
            self._donation_log(f"Clan chat button found at {chat_btn}", "INFO")
        else:
            self._donation_log("Clan chat button not found", "ERROR")
    
    def _donation_find_close_button(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        close_btn = self.controller.donation_detector.find_close_button(bounds)
        if close_btn:
            self._donation_log(f"Close button found at {close_btn}", "INFO")
        else:
            self._donation_log("Close button not found", "ERROR")
    
    def _donation_debug_screenshot(self):
        bounds = self.controller.get_game_window()
        if not bounds:
            self._donation_log("Game window not detected. Detect it first.", "ERROR")
            return
        
        self._donation_log("Creating debug screenshot with detection boxes...", "INFO")
        output_path = self.controller.donation_detector.create_debug_screenshot(bounds, "donation_debug.png")
        if output_path:
            self._donation_log(f"Debug screenshot saved: {output_path}", "INFO")
            self._donation_log(f"Legend: 🟢 Green=Troops(T), 🟡 Yellow=Spells(S), 🟠 Orange=Donate Button(D)", "INFO")
        else:
            self._donation_log("Failed to create debug screenshot", "ERROR")
    
    def _donation_start_bot(self):
        if self._donation_is_running:
            return
        
        self._donation_is_running = True
        self._donation_run_btn.config(state="disabled")
        self._donation_stop_btn.config(state="normal")
        self._donation_log("=== Donation Bot Started ===", "INFO")
        
        self._donation_thread = threading.Thread(target=self._donation_bot_loop, daemon=True)
        self._donation_thread.start()
    
    def _donation_stop_bot(self):
        self._donation_is_running = False
        self._donation_run_btn.config(state="normal")
        self._donation_stop_btn.config(state="disabled")
        self._donation_log("Donation Bot Stopped", "INFO")
    
    def _donation_bot_loop(self):
        try:
            import pyautogui
            iteration = 0
            while self._donation_is_running:
                iteration += 1
                
                self._donation_log(f"\n{'='*60}", "DEBUG")
                self._donation_log(f"[CYCLE {iteration}] Starting donation check...", "INFO")
                self._donation_log(f"{'='*60}", "DEBUG")
                
                self._donation_log(f"[STEP 1] Detecting game window...", "DEBUG")
                bounds = self.controller.get_game_window()
                if not bounds:
                    self._donation_log(f"  ✗ Game window not found", "ERROR")
                    interval = int(self._donation_interval_var.get())
                    self._donation_log(f"  Retrying in {interval}s...", "INFO")
                    time.sleep(interval)
                    continue
                
                x, y, w, h = bounds
                self._donation_log(f"  ✓ Game window detected at ({x}, {y}) - {w}x{h}", "INFO")
                
                self._donation_log(f"[STEP 2] Checking if in clan chat...", "DEBUG")
                is_clan = self.controller.donation_detector.is_in_clan_chat(bounds)
                if not is_clan:
                    self._donation_log(f"  ✗ Not in clan chat screen, attempting to open...", "INFO")
                    chat_btn = self.controller.donation_detector.find_clan_chat_button(bounds)
                    if chat_btn:
                        self._donation_log(f"  → Found clan chat button at {chat_btn}, clicking...", "DEBUG")
                        pyautogui.click(chat_btn[0], chat_btn[1])
                        time.sleep(1)
                        is_clan = self.controller.donation_detector.is_in_clan_chat(bounds)
                        if not is_clan:
                            self._donation_log(f"  ✗ Still not in clan chat after click", "WARNING")
                            interval = int(self._donation_interval_var.get())
                            self._donation_log(f"  Waiting {interval}s before next check...", "INFO")
                            time.sleep(interval)
                            continue
                    else:
                        self._donation_log(f"  ✗ Clan chat button not found", "ERROR")
                        interval = int(self._donation_interval_var.get())
                        self._donation_log(f"  Waiting {interval}s before next check...", "INFO")
                        time.sleep(interval)
                        continue
                
                self._donation_log(f"  ✓ In clan chat screen", "INFO")
                
                self._donation_log(f"[STEP 3] Looking for DONATE button in clan chat...", "DEBUG")
                gx, gy, gw, gh = bounds
                chat_region = (gx, gy, int(gw * 0.46), gh)
                donate_btn = self.controller.donation_detector.find_donate_button_template(chat_region)
                
                if not donate_btn:
                    self._donation_log(f"  ✗ No donate button found in chat - no pending requests", "INFO")
                    self._donation_troops_status.config(text="waiting", foreground=RED)
                    self._donation_spells_status.config(text="waiting", foreground=RED)
                    self._donation_requests_status.config(text="0 requests", foreground=RED)
                    interval = int(self._donation_interval_var.get())
                    self._donation_log(f"[WAITING] Next check in {interval}s...", "INFO")
                    time.sleep(interval)
                    continue
                
                self._donation_log(f"  ✓ Found DONATE button at {donate_btn}", "INFO")
                self._donation_requests_status.config(text="1+ requests", foreground=GREEN)
                
                self._donation_log(f"[STEP 4] Clicking DONATE button to open troop selection...", "DEBUG")
                pyautogui.click(donate_btn[0], donate_btn[1])
                time.sleep(1.5)
                
                self._donation_log(f"[STEP 5] Scanning for available (colored) troops...", "DEBUG")
                popup_region = (
                    int(gx + gw * 0.40),
                    int(gy + gh * 0.18),
                    int(gw * 0.57),
                    int(gh * 0.42),
                )
                self._donation_log(f"  Popup scan region: {popup_region}", "DEBUG")
                matched = self.controller.donation_detector.find_troops_by_templates(popup_region)
                
                if matched:
                    self._donation_log(f"  ✓ Found {len(matched)} available troops via template matching", "INFO")
                    for idx, (tx, ty) in enumerate(matched, 1):
                        self._donation_log(f"    {idx}. Troop at ({tx}, {ty})", "DEBUG")
                else:
                    self._donation_log(f"  ✗ No matching troops found (all greyed out or no templates)", "INFO")
                
                self._donation_troops_status.config(text=f"{len(matched)} found", foreground=GREEN if matched else RED)
                self._donation_spells_status.config(text="template", foreground=GREEN)
                
                if matched:
                    self._donation_log(f"[STEP 6] Clicking matched troops...", "DEBUG")
                    
                    for idx, (px, py) in enumerate(matched, 1):
                        pyautogui.click(px, py)
                        self._donation_log(f"  ✓ Clicked troop {idx}/{len(matched)} at ({px}, {py})", "INFO")
                        time.sleep(0.3)
                    
                    self._donation_log(f"[STEP 7] Finding CONFIRM DONATE button...", "DEBUG")
                    confirm_btn = self.controller.donation_detector.find_confirm_donate_button(popup_region)
                    
                    if confirm_btn:
                        self._donation_log(f"  ✓ Found confirm button at {confirm_btn}, clicking...", "INFO")
                        pyautogui.click(confirm_btn[0], confirm_btn[1])
                        time.sleep(1.5)
                        
                        self._donation_log(f"[STEP 8] Verifying donation succeeded...", "DEBUG")
                        if self.controller.donation_detector.verify_donation_completed(bounds):
                            self._donation_log(f"[COMPLETE] Successfully donated {len(matched)} troops ✓", "INFO")
                        else:
                            self._donation_log(f"[WARNING] Donation button still visible - may not have succeeded", "WARNING")
                    else:
                        self._donation_log(f"  ✗ Confirm donate button not found!", "ERROR")
                        self._donation_log(f"    → Donation was NOT sent (button not clicked)", "ERROR")
                else:
                    self._donation_log(f"[STEP 6] No troops available to donate", "WARNING")
                
                self._donation_log(f"[STEP 9] Closing clan chat...", "DEBUG")
                close_btn = self.controller.donation_detector.find_close_button(bounds)
                if close_btn:
                    self._donation_log(f"  → Found close button at {close_btn}, clicking...", "DEBUG")
                    pyautogui.click(close_btn[0], close_btn[1])
                    time.sleep(0.5)
                    self._donation_log(f"  ✓ Closed clan chat", "INFO")
                else:
                    self._donation_log(f"  ✗ Close button not found, skipping...", "WARNING")
                
                interval = int(self._donation_interval_var.get())
                self._donation_log(f"[WAITING] Next check in {interval}s...", "INFO")
                time.sleep(interval)
        
        except Exception as e:
            self._donation_log(f"[ERROR] Bot crashed: {e}", "ERROR")
            import traceback
            self._donation_log(f"  Traceback: {traceback.format_exc()}", "DEBUG")
            self._donation_is_running = False
            self._donation_run_btn.config(state="normal")
            self._donation_stop_btn.config(state="disabled")

    def _build_config_tab(self):
        inner = self._build_scrollable_tab(self._tab_config)
        inner.columnconfigure(1, weight=1)
        self._config_vars = {}
        
        # Add 'Show Advanced' toggle at the top
        self._show_advanced = tk.BooleanVar(value=False)
        
        def toggle_advanced():
            # Rebuild the tab when toggled
            for widget in inner.winfo_children():
                widget.destroy()
            self._build_config_tab_content(inner)
            
        ttk.Checkbutton(inner, text="Show Advanced Settings", variable=self._show_advanced, 
                        command=toggle_advanced).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=8)
        
        ttk.Separator(inner).grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=4)
        
        self._build_config_tab_content(inner, start_row=2)

    def _build_config_tab_content(self, inner, start_row=2):
        row = start_row
        adv = self._show_advanced.get()

        sections = []
        
        # App Section (Advanced Only)
        if adv:
            sections.append(("Application Info", [
                ("App Name", "app.name", "str"),
                ("App Version", "app.version", "str"),
                ("Author", "app.author", "str"),
            ]))

        # Automation Section
        auto_fields = [
            ("Playback Speed", "automation.default_playback_speed", "float"),
            ("Failsafe Enabled", "automation.failsafe_enabled", "bool"),
            ("Click Variation", "automation.enable_click_variation", "bool"),
        ]
        if adv:
            auto_fields.extend([
                ("Default Click Delay", "automation.default_click_delay", "float"),
                ("Max Recording Duration", "automation.max_recording_duration", "int"),
                ("Click Variance Pixels", "automation.click_variance_pixels", "int"),
            ])
        sections.append(("Automation", auto_fields))

        # Auto Attacker Section
        attacker_fields = [
            ("Max Search Attempts", "auto_attacker.max_search_attempts", "int"),
            ("Min Battle Duration (s)", "auto_attacker.battle_duration_min", "float"),
            ("Max Battle Duration (s)", "auto_attacker.battle_duration_max", "float"),
        ]
        if adv:
            attacker_fields.extend([
                ("Base Wait After Reject", "auto_attacker.base_wait_after_reject", "float"),
                ("Base Search Wait", "auto_attacker.base_search_wait", "float"),
                ("Base Info Display Wait", "auto_attacker.base_info_display_wait", "float"),
                ("Base Load Wait", "auto_attacker.base_load_wait", "float"),
                ("Return Home Wait", "auto_attacker.return_home_wait", "float"),
                ("Attack Button Delay", "auto_attacker.attack_button_delay", "float"),
                ("Next Attempt Delay", "auto_attacker.next_attempt_delay", "float"),
                ("Next Attempt Delay Max", "auto_attacker.next_attempt_delay_max", "float"),
                ("Search Delay Variance", "auto_attacker.search_delay_variance", "float"),
                ("Base Load Variance", "auto_attacker.base_load_variance", "float"),
                ("Patience Factor", "auto_attacker.patience_fatigue_factor", "float"),
            ])
        sections.append(("Search & Attack", attacker_fields))

        # Legend League Section
        legend_fields = [
            ("Daily Attack Limit", "legend_league.daily_attack_limit", "int"),
            ("Window Start UTC", "legend_league.window_start_utc", "str"),
            ("Window End UTC", "legend_league.window_end_utc", "str"),
            ("Wait for Window", "legend_league.wait_for_window", "bool"),
            ("Between Attacks Min (s)", "legend_league.between_attack_delay_min", "float"),
            ("Between Attacks Max (s)", "legend_league.between_attack_delay_max", "float"),
        ]
        if adv:
            legend_fields.extend([
                ("AI Strategy", "legend_league.ai_strategy_enabled", "bool"),
                ("Pre-Window Buffer (min)", "legend_league.pre_window_buffer_minutes", "int"),
                ("Skip If Window Closed", "legend_league.skip_if_window_closed", "bool"),
            ])
        sections.append(("Legend League", legend_fields))

        # Display Section
        display_fields = [
            ("Sound Notifications", "display.sound_notifications", "bool"),
        ]
        if adv:
            display_fields.extend([
                ("Colored Output", "display.colored_output", "bool"),
                ("Show Progress Bars", "display.show_progress_bars", "bool"),
            ])
        sections.append(("Display", display_fields))

        # Game Section (Advanced Only)
        if adv:
            sections.append(("Game Window & Detection", [
                ("Detection Timeout", "game.detection_timeout", "float"),
                ("Click Precision", "game.click_precision", "int"),
                ("Matching Threshold", "game.template_matching_threshold", "float"),
            ]))

        # Render sections
        for section_name, fields in sections:
            self._section_label(inner, row, section_name)
            row += 1
            for label, key, ftype in fields:
                if ftype == "bool":
                    var = tk.BooleanVar(value=bool(self.controller.config.get(key, False)))
                    cb = ttk.Checkbutton(inner, text=label, variable=var)
                    cb.grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=2)
                else:
                    ttk.Label(inner, text=label + ":").grid(row=row, column=0, sticky="w", padx=8, pady=2)
                    var = tk.StringVar(value=str(self.controller.config.get(key, "")))
                    ttk.Entry(inner, textvariable=var, width=24).grid(row=row, column=1, sticky="ew", padx=8, pady=2)
                self._config_vars[key] = (var, ftype)
                row += 1

        ttk.Button(inner, text="Save Configuration", style="Accent.TButton",
                   command=self._config_save).grid(row=row, column=0, columnspan=2, pady=16, padx=8, sticky="w")

    def _config_save(self):
        type_map = {"str": str, "int": int, "float": float, "bool": bool}
        errors = []
        for key, (var, ftype) in self._config_vars.items():
            try:
                if ftype == "bool":
                    val = var.get()
                else:
                    val = type_map[ftype](var.get())
                self.controller.config.set(key, val)
            except (ValueError, TypeError):
                errors.append(key)
        if errors:
            messagebox.showerror("Invalid Values", "Could not parse:\n" + "\n".join(errors), parent=self.root)
            return
        self.controller.config.save_config()
        messagebox.showinfo("Saved", "Configuration saved.", parent=self.root)

    def _set_log_filter(self, level):
        self._log_level_filter = level

    def _log_clear(self):
        self._log_text.config(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.config(state="disabled")

    def _drain_log_queue(self):
        while True:
            try:
                record = self._log_queue.get_nowait()
            except queue.Empty:
                break
            level = record.levelname
            if self._log_level_filter != "ALL" and level != self._log_level_filter:
                continue
            ts = datetime.datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            msg = f"[{ts}] [{level}] {record.getMessage()}\n"
            self._log_text.config(state="normal")
            self._log_text.insert("end", msg, level)
            if self._auto_scroll.get():
                self._log_text.see("end")
            self._log_text.config(state="disabled")

    def _periodic_update(self):
        try:
            running = self.controller.is_auto_attacking()

            if running:
                self._status_dot.config(fg=GREEN)
                self._status_label.config(text="Running", fg=GREEN)
            else:
                current_text = self._status_label.cget("text")
                if current_text not in ("Stopping…", "Stopped"):
                    self._status_label.config(text="Stopped", fg=RED)
                    self._status_dot.config(fg=RED)

            for btn in (self._dash_start_btn, self._auto_start_btn):
                btn.configure(state="disabled" if running else "normal")
            for btn in (self._dash_stop_btn, self._auto_stop_btn):
                btn.configure(state="normal" if running else "disabled")

            mode = self.controller.get_attack_mode()
            if mode == "legend":
                self._mode_pill.config(text="  LEGEND  ", bg=LEGEND_COLOR)
                desc = "Legend League: attacks assigned opponents (8/day), no loot filter"
            else:
                self._mode_pill.config(text="  FARM  ", bg=FARM_COLOR)
                desc = "Farm: searches for bases meeting loot thresholds, skips others"
            if hasattr(self, "_auto_mode_desc"):
                self._auto_mode_desc.config(text=desc)

            stats = self.controller.get_auto_attack_stats()
            self._stat_total.config(text=str(stats.get("total_attacks", 0)))
            self._stat_success.config(text=str(stats.get("successful_attacks", 0)))
            self._stat_failed.config(text=str(stats.get("failed_attacks", 0)))
            rate = stats.get("success_rate", 0)
            self._stat_rate.config(text=f"{rate:.1f}%")
            hours = stats.get("runtime_hours", 0)
            self._stat_runtime.config(text=f"{hours:.2f}h")
            aph = stats.get("attacks_per_hour", 0)
            self._stat_per_hour.config(text=f"{aph:.1f}")

            if mode == "legend":
                used = self.controller.auto_attacker._legend_attacks_today
                limit = int(self.controller.config.get("legend_league.daily_attack_limit", 8))
                self._stat_legend_attacks.config(text=f"{used}/{limit}")
            else:
                self._stat_legend_attacks.config(text="—")

            self._drain_log_queue()
        except Exception:
            pass

        self.root.after(500, self._periodic_update)

    def _on_close(self):
        try:
            self.controller.shutdown()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()
