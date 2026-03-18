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

BG = "#1e1e2e"
FRAME_BG = "#252535"
ACCENT = "#cba6f7"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
TEXT = "#cdd6f4"
SUBTEXT = "#a6adc8"
BORDER = "#313244"
ENTRY_BG = "#313244"
BTN_BG = "#45475a"


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
        style.configure(".", background=BG, foreground=TEXT, fieldbackground=ENTRY_BG, bordercolor=BORDER, troughcolor=FRAME_BG)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TButton", background=BTN_BG, foreground=TEXT, bordercolor=BORDER, focuscolor=ACCENT, padding=6)
        style.map("TButton", background=[("active", ACCENT), ("pressed", BORDER)], foreground=[("active", BG)])
        style.configure("Accent.TButton", background=ACCENT, foreground=BG)
        style.map("Accent.TButton", background=[("active", TEXT), ("pressed", BORDER)])
        style.configure("Green.TButton", background=GREEN, foreground=BG)
        style.map("Green.TButton", background=[("active", TEXT)])
        style.configure("Red.TButton", background=RED, foreground=BG)
        style.map("Red.TButton", background=[("active", TEXT)])
        style.configure("TNotebook", background=BG, bordercolor=BORDER)
        style.configure("TNotebook.Tab", background=FRAME_BG, foreground=SUBTEXT, padding=[12, 6])
        style.map("TNotebook.Tab", background=[("selected", BG)], foreground=[("selected", ACCENT)])
        style.configure("TLabelframe", background=FRAME_BG, foreground=ACCENT, bordercolor=BORDER)
        style.configure("TLabelframe.Label", background=FRAME_BG, foreground=ACCENT)
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT, bordercolor=BORDER, insertcolor=TEXT)
        style.configure("TCheckbutton", background=FRAME_BG, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", FRAME_BG)])
        style.configure("Treeview", background=ENTRY_BG, foreground=TEXT, fieldbackground=ENTRY_BG, bordercolor=BORDER)
        style.configure("Treeview.Heading", background=BTN_BG, foreground=ACCENT, bordercolor=BORDER)
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])
        style.configure("TScale", background=FRAME_BG, troughcolor=ENTRY_BG)
        style.configure("Horizontal.TScrollbar", background=BTN_BG, troughcolor=ENTRY_BG, bordercolor=BORDER)
        style.configure("Vertical.TScrollbar", background=BTN_BG, troughcolor=ENTRY_BG, bordercolor=BORDER)
        style.configure("Card.TFrame", background=FRAME_BG, relief="flat")
        style.configure("Card.TLabel", background=FRAME_BG, foreground=TEXT)
        style.configure("CardTitle.TLabel", background=FRAME_BG, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        style.configure("Stat.TLabel", background=FRAME_BG, foreground=TEXT, font=("Segoe UI", 18, "bold"))
        style.configure("StatTitle.TLabel", background=FRAME_BG, foreground=SUBTEXT, font=("Segoe UI", 8))
        style.configure("Header.TFrame", background=BORDER)
        style.configure("Header.TLabel", background=BORDER, foreground=TEXT, font=("Segoe UI", 13, "bold"))

    def _build_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame", height=48)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = ttk.Label(header, text="CoC Attack Bot", style="Header.TLabel")
        title.pack(side="left", padx=16, pady=8)

        self._status_label = tk.Label(header, text="  Stopped", bg=BORDER, fg=RED, font=("Segoe UI", 10))
        self._status_label.pack(side="right", padx=16, pady=8)

        self._status_dot = tk.Label(header, text="●", bg=BORDER, fg=RED, font=("Segoe UI", 14))
        self._status_dot.pack(side="right", padx=4, pady=8)

    def _build_notebook(self):
        self._notebook = ttk.Notebook(self.root)
        self._notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._tab_dashboard = ttk.Frame(self._notebook)
        self._tab_auto = ttk.Frame(self._notebook)
        self._tab_recorder = ttk.Frame(self._notebook)
        self._tab_coords = ttk.Frame(self._notebook)
        self._tab_ai = ttk.Frame(self._notebook)
        self._tab_config = ttk.Frame(self._notebook)
        self._tab_logs = ttk.Frame(self._notebook)

        self._notebook.add(self._tab_dashboard, text="Dashboard")
        self._notebook.add(self._tab_auto, text="Auto Attacker")
        self._notebook.add(self._tab_recorder, text="Recorder")
        self._notebook.add(self._tab_coords, text="Coordinates")
        self._notebook.add(self._tab_ai, text="AI Analyzer")
        self._notebook.add(self._tab_config, text="Config")
        self._notebook.add(self._tab_logs, text="Logs")

        self._build_dashboard_tab()
        self._build_auto_attacker_tab()
        self._build_recorder_tab()
        self._build_coords_tab()
        self._build_ai_tab()
        self._build_config_tab()
        self._build_logs_tab()

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

        content = ttk.Frame(self._tab_dashboard)
        content.pack(fill="both", expand=True, padx=8, pady=4)

        left_outer, left = self._card(content, "Controls")
        left_outer.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self._dash_start_btn = ttk.Button(left, text="Start Auto Attack", style="Green.TButton",
                                          command=self._dashboard_start)
        self._dash_start_btn.pack(fill="x", pady=3)

        self._dash_stop_btn = ttk.Button(left, text="Stop Auto Attack", style="Red.TButton",
                                         command=self._dashboard_stop)
        self._dash_stop_btn.pack(fill="x", pady=3)

        ttk.Separator(left).pack(fill="x", pady=8)

        ttk.Button(left, text="Take Screenshot", command=self._take_screenshot).pack(fill="x", pady=3)
        ttk.Button(left, text="Detect Game Window", command=self._detect_window).pack(fill="x", pady=3)
        ttk.Button(left, text="Validate Config", command=self._validate_config_dash).pack(fill="x", pady=3)

        right_outer, right = self._card(content, "Status")
        right_outer.pack(side="left", fill="both", expand=True, padx=(4, 0))

        ttk.Label(right, text="Game Window:", style="Card.TLabel", font=("Segoe UI", 9, "bold"),
                  background=FRAME_BG).pack(anchor="w")
        self._window_status_lbl = ttk.Label(right, text="Not detected", style="Card.TLabel", foreground=RED)
        self._window_status_lbl.pack(anchor="w", pady=(0, 8))

        ttk.Label(right, text="Config Validation:", style="Card.TLabel", font=("Segoe UI", 9, "bold"),
                  background=FRAME_BG).pack(anchor="w")
        self._config_status_lbl = ttk.Label(right, text="Not checked", style="Card.TLabel", foreground=SUBTEXT)
        self._config_status_lbl.pack(anchor="w")

        self._config_errors_text = tk.Text(right, height=6, bg=ENTRY_BG, fg=TEXT,
                                           insertbackground=TEXT, relief="flat", font=("Consolas", 9))
        self._config_errors_text.pack(fill="both", expand=True, pady=(4, 0))
        self._config_errors_text.config(state="disabled")

    def _dashboard_start(self):
        self.controller.start_auto_attack()

    def _dashboard_stop(self):
        self.controller.stop_auto_attack()

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
        self._config_errors_text.config(state="normal")
        self._config_errors_text.delete("1.0", "end")
        if ok:
            self._config_status_lbl.config(text="Valid", foreground=GREEN)
            self._config_errors_text.insert("end", "All checks passed.")
        else:
            self._config_status_lbl.config(text="Invalid", foreground=RED)
            for err in errors:
                self._config_errors_text.insert("end", f"• {err}\n")
        self._config_errors_text.config(state="disabled")

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

        ctrl_frame = ttk.LabelFrame(right, text="Control", padding=8)
        ctrl_frame.pack(fill="x")

        self._auto_start_btn = ttk.Button(ctrl_frame, text="Start Auto Attack", style="Green.TButton",
                                          command=self._dashboard_start)
        self._auto_start_btn.pack(fill="x", pady=3)
        self._auto_stop_btn = ttk.Button(ctrl_frame, text="Stop Auto Attack", style="Red.TButton",
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

    def _build_recorder_tab(self):
        left = ttk.Frame(self._tab_recorder)
        left.pack(side="left", fill="both", padx=(8, 4), pady=8, expand=False)
        left.configure(width=220)

        right = ttk.Frame(self._tab_recorder)
        right.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

        list_frame = ttk.LabelFrame(left, text="Recordings", padding=6)
        list_frame.pack(fill="both", expand=True)

        list_sb = ttk.Scrollbar(list_frame, orient="vertical")
        self._rec_listbox = tk.Listbox(list_frame, bg=ENTRY_BG, fg=TEXT, selectbackground=ACCENT,
                                       selectforeground=BG, relief="flat", font=("Segoe UI", 10),
                                       yscrollcommand=list_sb.set)
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

        self._rec_info_text = tk.Text(info_inner, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                                      relief="flat", font=("Consolas", 9), height=6)
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

        req_frame = ttk.LabelFrame(right, text="Required Buttons Status", padding=8)
        req_frame.pack(fill="x", pady=(0, 6))

        self._req_labels = {}
        for btn_key, desc in ConfigValidator.REQUIRED_BUTTONS.items():
            row = ttk.Frame(req_frame, style="Card.TFrame")
            row.pack(fill="x", pady=1)
            dot = tk.Label(row, text="●", bg=FRAME_BG, fg=RED, font=("Segoe UI", 10))
            dot.pack(side="left", padx=(0, 4))
            ttk.Label(row, text=f"{btn_key}: {desc}", style="Card.TLabel",
                      font=("Segoe UI", 8)).pack(side="left")
            self._req_labels[btn_key] = dot

        wizard_frame = ttk.LabelFrame(right, text="Mapping Wizard", padding=8)
        wizard_frame.pack(fill="x", pady=(0, 6))

        ttk.Button(wizard_frame, text="Start Mapping Wizard",
                   command=self._coord_wizard).pack(fill="x")

        val_frame = ttk.LabelFrame(right, text="Validate", padding=8)
        val_frame.pack(fill="both", expand=True)

        ttk.Button(val_frame, text="Validate Coordinates", command=self._coord_validate).pack(fill="x", pady=(0, 4))
        self._coord_val_text = tk.Text(val_frame, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                                       relief="flat", font=("Consolas", 9))
        val_vsb = ttk.Scrollbar(val_frame, orient="vertical", command=self._coord_val_text.yview)
        self._coord_val_text.configure(yscrollcommand=val_vsb.set)
        self._coord_val_text.pack(side="left", fill="both", expand=True)
        val_vsb.pack(side="right", fill="y")
        self._coord_val_text.config(state="disabled")

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
        results = self.controller.coordinate_mapper.validate_coordinates()
        self._coord_val_text.config(state="normal")
        self._coord_val_text.delete("1.0", "end")
        for name, ok in results.items():
            marker = "✓" if ok else "✗"
            self._coord_val_text.insert("end", f"{marker} {name}\n")
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
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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

    def _build_config_tab(self):
        inner = self._build_scrollable_tab(self._tab_config)
        inner.columnconfigure(1, weight=1)
        self._config_vars = {}
        row = 0

        sections = [
            ("App", [
                ("Name", "app.name", "str"),
                ("Version", "app.version", "str"),
                ("Author", "app.author", "str"),
            ]),
            ("Automation", [
                ("Default Click Delay", "automation.default_click_delay", "float"),
                ("Default Playback Speed", "automation.default_playback_speed", "float"),
                ("Failsafe Enabled", "automation.failsafe_enabled", "bool"),
                ("Max Recording Duration", "automation.max_recording_duration", "int"),
                ("Enable Click Variation", "automation.enable_click_variation", "bool"),
                ("Click Variance Pixels", "automation.click_variance_pixels", "int"),
            ]),
            ("Auto Attacker", [
                ("Max Search Attempts", "auto_attacker.max_search_attempts", "int"),
                ("Base Wait After Reject", "auto_attacker.base_wait_after_reject", "float"),
                ("Base Search Wait", "auto_attacker.base_search_wait", "float"),
                ("Base Info Display Wait", "auto_attacker.base_info_display_wait", "float"),
                ("Base Load Wait", "auto_attacker.base_load_wait", "float"),
                ("Battle Duration Min", "auto_attacker.battle_duration_min", "float"),
                ("Battle Duration Max", "auto_attacker.battle_duration_max", "float"),
                ("Return Home Wait", "auto_attacker.return_home_wait", "float"),
                ("Attack Button Delay", "auto_attacker.attack_button_delay", "float"),
                ("Next Attempt Delay", "auto_attacker.next_attempt_delay", "float"),
                ("Next Attempt Delay Max", "auto_attacker.next_attempt_delay_max", "float"),
                ("Search Delay Variance", "auto_attacker.search_delay_variance", "float"),
                ("Base Load Variance", "auto_attacker.base_load_variance", "float"),
                ("Patience Fatigue Factor", "auto_attacker.patience_fatigue_factor", "float"),
            ]),
            ("Display", [
                ("Colored Output", "display.colored_output", "bool"),
                ("Sound Notifications", "display.sound_notifications", "bool"),
                ("Show Progress Bars", "display.show_progress_bars", "bool"),
            ]),
            ("Game", [
                ("Detection Timeout", "game.detection_timeout", "float"),
                ("Click Precision", "game.click_precision", "int"),
                ("Template Matching Threshold", "game.template_matching_threshold", "float"),
            ]),
        ]

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

        ttk.Button(inner, text="Save Config", style="Accent.TButton",
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

    def _build_logs_tab(self):
        filter_row = ttk.Frame(self._tab_logs)
        filter_row.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(filter_row, text="Level:").pack(side="left", padx=(0, 4))

        self._log_filter_btns = {}
        for lvl in ("ALL", "INFO", "WARNING", "ERROR"):
            btn = ttk.Button(filter_row, text=lvl, width=8,
                             command=lambda l=lvl: self._set_log_filter(l))
            btn.pack(side="left", padx=2)
            self._log_filter_btns[lvl] = btn

        self._set_log_filter("ALL")

        ttk.Button(filter_row, text="Clear", command=self._log_clear).pack(side="left", padx=8)
        ttk.Checkbutton(filter_row, text="Auto-scroll", variable=self._auto_scroll).pack(side="left", padx=4)

        log_frame = ttk.Frame(self._tab_logs)
        log_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._log_text = scrolledtext.ScrolledText(
            log_frame, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Consolas", 9), state="disabled",
            wrap="word"
        )
        self._log_text.pack(fill="both", expand=True)
        self._log_text.tag_config("INFO", foreground=TEXT)
        self._log_text.tag_config("WARNING", foreground=YELLOW)
        self._log_text.tag_config("ERROR", foreground=RED)
        self._log_text.tag_config("DEBUG", foreground=SUBTEXT)

    def _set_log_filter(self, level):
        self._log_level_filter = level
        for lvl, btn in self._log_filter_btns.items():
            if lvl == level:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="TButton")

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
                self._status_label.config(text="  Running", fg=GREEN)
            else:
                self._status_dot.config(fg=RED)
                self._status_label.config(text="  Stopped", fg=RED)

            for btn in (self._dash_start_btn, self._auto_start_btn):
                btn.configure(state="disabled" if running else "normal")
            for btn in (self._dash_stop_btn, self._auto_stop_btn):
                btn.configure(state="normal" if running else "disabled")

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
