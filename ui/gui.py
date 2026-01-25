"""
GUI simplificada do Bot COC.
"""

import json
import logging
import threading
import tkinter as tk
import traceback
from tkinter import messagebox, scrolledtext, ttk

from bot.bluestacks import BlueStacks
from bot.device import Device
from bot.i18n import get_available_languages, get_language, set_language, t
from bot.settings import Settings
from functions.army import create_army, delete_army, train_army
from functions.config import go_home, init_game, setup_emulator
from functions.donate import donate_castle, request_castle


class TextHandler(logging.Handler):
    """Handler que envia logs para um widget Text do tkinter."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append, msg, record.levelno)

    def _append(self, msg, level):
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + "\n")

        # Colorir por nivel
        if level >= logging.ERROR:
            self._colorize_last_line("red")
        elif level >= logging.WARNING:
            self._colorize_last_line("orange")
        elif level >= logging.DEBUG:
            self._colorize_last_line("gray")

        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")

    def _colorize_last_line(self, color):
        self.text_widget.tag_add(color, "end-2l", "end-1l")
        self.text_widget.tag_config(color, foreground=color)


class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(t("gui.title"))
        self.root.geometry("800x700")

        self.device = None
        self.is_running = False
        self.ui_widgets = {}
        self.log_text = None
        self.debug_text = None
        self.logger = None

        self.setup_ui()
        self.setup_logging()
        self.load_army_config()

    def setup_ui(self):
        # Menu de idiomas
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=language_menu)

        self.language_var = tk.StringVar(value=get_language())
        for lang in get_available_languages():
            language_menu.add_radiobutton(
                label=lang, variable=self.language_var, value=lang, command=self.change_language
            )

        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Aba: Controle
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text=t("gui.tabs.control"))
        self.setup_control_tab(control_frame)

        # Aba: Exercito
        army_frame = ttk.Frame(self.notebook)
        self.notebook.add(army_frame, text=t("gui.tabs.army"))
        self.setup_army_tab(army_frame)

        # Aba: Log
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text=t("gui.tabs.log"))
        self.setup_log_tab(log_frame)

        # Aba: Debug
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text="Debug")
        self.setup_debug_tab(debug_frame)

    def change_language(self):
        set_language(self.language_var.get())
        self.update_ui_language()

    def update_ui_language(self):
        self.root.title(t("gui.title"))
        self.notebook.tab(0, text=t("gui.tabs.control"))
        self.notebook.tab(1, text=t("gui.tabs.army"))
        self.notebook.tab(2, text=t("gui.tabs.log"))
        self.notebook.tab(3, text="Debug")

        for key, info in self.ui_widgets.items():
            widget = info.get("widget")
            wtype = info.get("type")
            if not widget:
                continue
            if wtype == "button":
                widget.config(text=t(f"gui.buttons.{key}"))
            elif wtype in ("label", "labelframe"):
                widget.config(text=t(f"gui.labels.{key}"))

    def setup_control_tab(self, parent):
        # BlueStacks
        bs_frame = ttk.LabelFrame(parent, text=t("gui.labels.blue_stacks_control"), padding=10)
        bs_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["blue_stacks_control"] = {"type": "labelframe", "widget": bs_frame}

        for name, cmd in [
            ("setup_emulator", self.setup_emulator),
            ("kill_bluestacks", self.kill_bluestacks),
            ("configure_bluestacks", self.configure_bluestacks),
            ("start_bluestacks", self.start_bluestacks),
            ("validate_adb", self.validate_adb),
        ]:
            btn = ttk.Button(bs_frame, text=t(f"gui.buttons.{name}"), command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            self.ui_widgets[name] = {"type": "button", "widget": btn}

        # Conexao
        device_frame = ttk.LabelFrame(parent, text=t("gui.labels.device_connection"), padding=10)
        device_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["device_connection"] = {"type": "labelframe", "widget": device_frame}

        for name, cmd in [
            ("connect_device", self.connect_device),
            ("screenshot", self.take_screenshot),
        ]:
            btn = ttk.Button(device_frame, text=t(f"gui.buttons.{name}"), command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            self.ui_widgets[name] = {"type": "button", "widget": btn}

        # Acoes do Jogo
        game_frame = ttk.LabelFrame(parent, text=t("gui.labels.game_actions"), padding=10)
        game_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["game_actions"] = {"type": "labelframe", "widget": game_frame}

        for name, cmd in [
            ("init_game", self.init_game),
            ("center_view", self.center_view),
            ("go_home", self.go_home),
        ]:
            btn = ttk.Button(game_frame, text=t(f"gui.buttons.{name}"), command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            self.ui_widgets[name] = {"type": "button", "widget": btn}

        # Funcoes do Bot
        bot_frame = ttk.LabelFrame(parent, text=t("gui.labels.bot_functions"), padding=10)
        bot_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["bot_functions"] = {"type": "labelframe", "widget": bot_frame}

        for name, cmd in [
            ("delete_army", self.delete_army),
            ("create_army", self.create_army),
            ("train_army", self.train_army),
            ("donate_castle", self.donate_castle),
            ("request_castle", self.request_castle),
        ]:
            btn = ttk.Button(bot_frame, text=t(f"gui.buttons.{name}"), command=cmd)
            btn.pack(side=tk.LEFT, padx=2)
            self.ui_widgets[name] = {"type": "button", "widget": btn}

    def setup_army_tab(self, parent):
        # Tropas disponiveis
        troops_frame = ttk.LabelFrame(parent, text="Available Troops", padding=10)
        troops_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        listbox_frame = ttk.Frame(troops_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.troops_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        self.troops_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.troops_listbox.yview)

        troops_buttons = ttk.Frame(troops_frame)
        troops_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(troops_buttons, text="Refresh", command=self.refresh_troops_list).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(troops_buttons, text="Add", command=self.add_troop_to_army).pack(
            side=tk.LEFT, padx=2
        )

        # Configuracao do exercito
        army_frame = ttk.LabelFrame(parent, text="Army Configuration", padding=10)
        army_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tree_frame = ttk.Frame(army_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.army_tree = ttk.Treeview(
            tree_frame, columns=("Troop", "Quantity"), show="headings", height=10
        )
        self.army_tree.heading("Troop", text="Troop")
        self.army_tree.heading("Quantity", text="Qty")
        self.army_tree.column("Troop", width=200)
        self.army_tree.column("Quantity", width=80)
        self.army_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.army_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.army_tree.configure(yscrollcommand=tree_scroll.set)

        army_buttons = ttk.Frame(army_frame)
        army_buttons.pack(fill=tk.X, pady=5)

        ttk.Button(army_buttons, text="Remove", command=self.remove_troop).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(army_buttons, text="Update Qty", command=self.update_quantity).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(army_buttons, text="Save", command=self.save_army_config).pack(
            side=tk.LEFT, padx=2
        )

        qty_frame = ttk.Frame(army_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        ttk.Label(qty_frame, text="Quantity:").pack(side=tk.LEFT, padx=5)
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(qty_frame, textvariable=self.quantity_var, width=10).pack(side=tk.LEFT)

        self.refresh_troops_list()

    def setup_log_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(parent, text=t("gui.buttons.clear_log"), command=self.clear_log).pack(pady=5)

    def setup_debug_tab(self, parent):
        # Frame de controles
        controls = ttk.Frame(parent)
        controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(controls, text="Log Level:").pack(side=tk.LEFT, padx=5)

        self.log_level_var = tk.StringVar(value="DEBUG")
        level_combo = ttk.Combobox(
            controls,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10,
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self.change_log_level)

        ttk.Button(controls, text="Clear", command=self.clear_debug).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Copy All", command=self.copy_debug).pack(side=tk.LEFT, padx=5)

        # Area de texto para debug
        self.debug_text = scrolledtext.ScrolledText(
            parent, wrap=tk.WORD, height=30, font=("Consolas", 9)
        )
        self.debug_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.debug_text.configure(state="disabled")

    def setup_logging(self):
        """Configura o sistema de logging."""
        self.logger = logging.getLogger("botcoc")
        self.logger.setLevel(logging.DEBUG)

        # Remove handlers existentes
        self.logger.handlers.clear()

        # Handler para debug_text
        if self.debug_text:
            handler = TextHandler(self.debug_text)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Captura logs de outros modulos
        logging.getLogger().addHandler(logging.NullHandler())

    def change_log_level(self, event=None):
        level = getattr(logging, self.log_level_var.get())
        for handler in self.logger.handlers:
            handler.setLevel(level)

    def clear_debug(self):
        if self.debug_text:
            self.debug_text.configure(state="normal")
            self.debug_text.delete(1.0, tk.END)
            self.debug_text.configure(state="disabled")

    def copy_debug(self):
        if self.debug_text:
            content = self.debug_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)

    def debug(self, message, level="DEBUG"):
        """Envia mensagem para o log de debug."""
        if self.logger:
            log_func = getattr(self.logger, level.lower(), self.logger.debug)
            log_func(message)

    def log(self, message):
        if self.log_text:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)

    def clear_log(self):
        if self.log_text:
            self.log_text.delete(1.0, tk.END)

    def run_in_thread(self, func):
        if self.is_running:
            messagebox.showwarning("Warning", "Another operation is running!")
            return

        self.is_running = True
        func_name = func.__name__

        def wrapper():
            self.debug(f"Starting: {func_name}", "INFO")
            try:
                func()
                self.debug(f"Completed: {func_name}", "INFO")
            except Exception as e:
                self.log(f"ERROR: {e}")
                # Log completo com traceback
                tb = traceback.format_exc()
                self.debug(f"Exception in {func_name}:\n{tb}", "ERROR")
            finally:
                self.is_running = False

        threading.Thread(target=wrapper, daemon=True).start()

    def check_device(self) -> bool:
        if not self.device:
            messagebox.showwarning("Warning", "Connect device first!")
            return False
        return True

    # ==================== BLUESTACKS ====================

    def setup_emulator(self):
        self.run_in_thread(self._setup_emulator)

    def _setup_emulator(self):
        """Configura emulador completo e abre o jogo."""
        success, device = setup_emulator(callback=self.log)

        if success:
            self.device = device
            messagebox.showinfo("Sucesso", "Emulador configurado e jogo aberto!")
        else:
            self.device = device
            messagebox.showwarning("Aviso", "Configuracao concluida, mas vila nao detectada.")

    def kill_bluestacks(self):
        self.run_in_thread(self._kill_bluestacks)

    def _kill_bluestacks(self):
        self.log("[BS] Killing BlueStacks...")
        BlueStacks.kill()
        self.log("[BS] Done")

    def configure_bluestacks(self):
        self.run_in_thread(self._configure_bluestacks)

    def _configure_bluestacks(self):
        self.log("[BS] Configuring...")
        BlueStacks.configure()
        self.log("[BS] Done")

    def start_bluestacks(self):
        self.run_in_thread(self._start_bluestacks)

    def _start_bluestacks(self):
        self.log("[BS] Starting...")
        BlueStacks.start()
        self.log("[BS] Done")

    def validate_adb(self):
        self.run_in_thread(self._validate_adb)

    def _validate_adb(self):
        self.log("[ADB] Validating...")
        result = BlueStacks.validate_adb()
        self.log(f"[ADB] {result}")

    # ==================== DEVICE ====================

    def connect_device(self):
        self.run_in_thread(self._connect_device)

    def _connect_device(self):
        self.log("[DEVICE] Connecting...")
        self.device = Device()
        self.log(f"[DEVICE] Connected to {self.device.serial}")

    def take_screenshot(self):
        if not self.check_device():
            return
        self.run_in_thread(self._take_screenshot)

    def _take_screenshot(self):
        self.log("[DEVICE] Taking screenshot...")
        self.device.screenshot()
        self.log("[DEVICE] Saved to screen.png")

    # ==================== GAME ====================

    def init_game(self):
        if not self.check_device():
            return
        self.run_in_thread(self._init_game)

    def _init_game(self):
        self.log("[GAME] Initializing...")
        init_game(self.device)
        self.log("[GAME] Done")

    def center_view(self):
        if not self.check_device():
            return
        self.run_in_thread(self._center_view)

    def _center_view(self):
        self.log("[GAME] Centering view...")
        self.device.center_view(move_right=120, move_down=50)
        self.log("[GAME] Done")

    def go_home(self):
        if not self.check_device():
            return
        self.run_in_thread(self._go_home)

    def _go_home(self):
        self.log("[GAME] Returning to home...")
        go_home(self.device)
        self.log("[GAME] Done")

    # ==================== BOT ACTIONS ====================

    def delete_army(self):
        if not self.check_device():
            return
        self.run_in_thread(self._delete_army)

    def _delete_army(self):
        self.log("[BOT] Deleting army...")
        delete_army(self.device)
        self.log("[BOT] Done")

    def create_army(self):
        if not self.check_device():
            return
        self.run_in_thread(self._create_army)

    def _create_army(self):
        self.log("[BOT] Creating army...")
        create_army(self.device)
        self.log("[BOT] Done")

    def train_army(self):
        if not self.check_device():
            return
        self.run_in_thread(self._train_army)

    def _train_army(self):
        self.log("[BOT] Training army...")
        train_army(self.device)
        self.log("[BOT] Done")

    def donate_castle(self):
        if not self.check_device():
            return
        self.run_in_thread(self._donate_castle)

    def _donate_castle(self):
        self.log("[BOT] Donating...")
        count = donate_castle(self.device)
        self.log(f"[BOT] Donated {count} times")

    def request_castle(self):
        if not self.check_device():
            return
        self.run_in_thread(self._request_castle)

    def _request_castle(self):
        self.log("[BOT] Requesting troops...")
        request_castle(self.device)
        self.log("[BOT] Done")

    # ==================== ARMY CONFIG ====================

    def refresh_troops_list(self):
        self.troops_listbox.delete(0, tk.END)

        # Usa BotActions se disponivel, senao le diretamente
        troops_dir = Settings.get_template_path("troops")
        troops = []
        if troops_dir.exists():
            for f in troops_dir.glob("*.png"):
                troops.append(f.stem)

        for troop in sorted(troops):
            self.troops_listbox.insert(tk.END, troop)

        self.log(f"[ARMY] Loaded {len(troops)} troops")

    def add_troop_to_army(self):
        selection = self.troops_listbox.curselection()
        if not selection:
            return

        name = self.troops_listbox.get(selection[0])
        qty = int(self.quantity_var.get())

        # Verifica se ja existe
        for item in self.army_tree.get_children():
            if self.army_tree.item(item, "values")[0] == name:
                return

        self.army_tree.insert("", tk.END, values=(name, qty))

    def remove_troop(self):
        selection = self.army_tree.selection()
        for item in selection:
            self.army_tree.delete(item)

    def update_quantity(self):
        selection = self.army_tree.selection()
        if not selection:
            return

        try:
            qty = int(self.quantity_var.get())
        except ValueError:
            return

        for item in selection:
            values = self.army_tree.item(item, "values")
            self.army_tree.item(item, values=(values[0], qty))

    def save_army_config(self):
        troops = []
        for item in self.army_tree.get_children():
            values = self.army_tree.item(item, "values")
            troops.append({"name": values[0], "quantity": int(values[1])})

        config = {"troops": troops, "spells": []}

        config_path = Settings.get_config_path("army.json")
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self.log(f"[ARMY] Saved {len(troops)} troops")
        messagebox.showinfo("Success", "Army config saved!")

    def load_army_config(self):
        config_path = Settings.get_config_path("army.json")
        if not config_path.exists():
            return

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for item in self.army_tree.get_children():
            self.army_tree.delete(item)

        for troop in config.get("troops", []):
            self.army_tree.insert(
                "", tk.END, values=(troop.get("name", ""), troop.get("quantity", 1))
            )


def main():
    root = tk.Tk()
    BotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
