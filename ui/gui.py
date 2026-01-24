import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os
import logging
from compat.android import AndroidDevice
from functions.bluestacks_control import (
    configure_bluestacks, start_bluestacks, kill_bluestacks, adb_validate
)
from functions.donate import donate_castle, request_castle
from functions.delete_army import delete_army
from functions.create_army import create_army, train_army, list_available_troops, load_army_config
from compat.logger import BotLogger
from compat.i18n import t, set_language, get_language, get_available_languages


class GUILogHandler(logging.Handler):
    """Custom log handler that sends logs to GUI"""
    def __init__(self, gui_instance):
        super().__init__()
        self.gui = gui_instance
        
    def emit(self, record):
        try:
            msg = self.format(record)
            # Thread-safe: usa after() para executar na thread principal
            self.gui.root.after(0, lambda: self.gui.log(msg))
        except Exception:
            pass


class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x700")
        
        self.device = None
        self.is_running = False
        self.ui_widgets = {}  # Store UI widgets for dynamic updates
        self.bot_controller = None  # BotController instance
        self.log_text = None  # Will be initialized in setup_log_tab
        
        # Inicializa sistema de logs e adiciona handler para GUI
        BotLogger.initialize(log_to_file=True, log_to_console=True)
        gui_handler = GUILogHandler(self)
        gui_handler.setFormatter(logging.Formatter(BotLogger.LOG_FORMAT, BotLogger.DATE_FORMAT))
        root_logger = logging.getLogger()
        root_logger.addHandler(gui_handler)
        
        self.setup_ui()
        self.load_army_config()
        self.update_ui_language()  # Update UI with current language
        
    def setup_ui(self):
        # Menu bar for language selection
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Language menu
        language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=language_menu)
        
        self.language_var = tk.StringVar(value=get_language())
        for lang in get_available_languages():
            language_menu.add_radiobutton(
                label=lang,
                variable=self.language_var,
                value=lang,
                command=self.change_language
            )
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba: Controle
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text=t("gui.tabs.control"))
        self.setup_control_tab(self.control_frame)
        
        # Aba: Exército
        self.army_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.army_frame, text=t("gui.tabs.army"))
        self.setup_army_tab(self.army_frame)
        
        # Aba: Log
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text=t("gui.tabs.log"))
        self.setup_log_tab(self.log_frame)
    
    def change_language(self):
        """Change the application language"""
        new_lang = self.language_var.get()
        set_language(new_lang)
        self.update_ui_language()
    
    def update_ui_language(self):
        """Update all UI text with current language"""
        # Update window title
        self.root.title(t("gui.title"))
        
        # Update notebook tabs
        self.notebook.tab(0, text=t("gui.tabs.control"))
        self.notebook.tab(1, text=t("gui.tabs.army"))
        self.notebook.tab(2, text=t("gui.tabs.log"))
        
        # Update all stored widgets
        for key, widget_info in self.ui_widgets.items():
            widget_type = widget_info.get("type")
            widget = widget_info.get("widget")
            
            if not widget:
                continue
                
            if widget_type == "button":
                widget.config(text=t(f"gui.buttons.{key}"))
            elif widget_type == "label":
                widget.config(text=t(f"gui.labels.{key}"))
            elif widget_type == "labelframe":
                widget.config(text=t(f"gui.labels.{key}"))
        
        # Update treeview headings
        self.army_tree.heading("Troop", text=t("gui.labels.troop"))
        self.army_tree.heading("Quantity", text=t("gui.labels.quantity_col"))
        
    def setup_control_tab(self, parent):
        # Seção: BlueStacks
        bs_frame = ttk.LabelFrame(parent, text=t("gui.labels.blue_stacks_control"), padding=10)
        bs_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["blue_stacks_control"] = {"type": "labelframe", "widget": bs_frame}
        
        btn_kill = ttk.Button(bs_frame, text=t("gui.buttons.kill_bluestacks"), 
                  command=self.kill_bluestacks)
        btn_kill.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["kill_bluestacks"] = {"type": "button", "widget": btn_kill}
        
        btn_config = ttk.Button(bs_frame, text=t("gui.buttons.configure_bluestacks"), 
                  command=self.configure_bluestacks)
        btn_config.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["configure_bluestacks"] = {"type": "button", "widget": btn_config}
        
        btn_start = ttk.Button(bs_frame, text=t("gui.buttons.start_bluestacks"), 
                  command=self.start_bluestacks)
        btn_start.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["start_bluestacks"] = {"type": "button", "widget": btn_start}
        
        btn_validate = ttk.Button(bs_frame, text=t("gui.buttons.validate_adb"), 
                  command=self.validate_adb)
        btn_validate.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["validate_adb"] = {"type": "button", "widget": btn_validate}
        
        # Seção: Device Connection
        device_frame = ttk.LabelFrame(parent, text=t("gui.labels.device_connection"), padding=10)
        device_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["device_connection"] = {"type": "labelframe", "widget": device_frame}
        
        btn_connect = ttk.Button(device_frame, text=t("gui.buttons.connect_device"), 
                  command=self.connect_device)
        btn_connect.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["connect_device"] = {"type": "button", "widget": btn_connect}
        
        btn_screenshot = ttk.Button(device_frame, text=t("gui.buttons.screenshot"), 
                  command=self.take_screenshot)
        btn_screenshot.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["screenshot"] = {"type": "button", "widget": btn_screenshot}
        
        # Seção: Game Actions
        game_frame = ttk.LabelFrame(parent, text=t("gui.labels.game_actions"), padding=10)
        game_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["game_actions"] = {"type": "labelframe", "widget": game_frame}
        
        btn_init = ttk.Button(game_frame, text=t("gui.buttons.init_game"), 
                  command=self.init_game)
        btn_init.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["init_game"] = {"type": "button", "widget": btn_init}
        
        btn_center = ttk.Button(game_frame, text=t("gui.buttons.center_view"), 
                  command=self.center_view)
        btn_center.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["center_view"] = {"type": "button", "widget": btn_center}
        
        # Seção: Bot Functions
        bot_frame = ttk.LabelFrame(parent, text=t("gui.labels.bot_functions"), padding=10)
        bot_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["bot_functions"] = {"type": "labelframe", "widget": bot_frame}
        
        btn_delete = ttk.Button(bot_frame, text=t("gui.buttons.delete_army"), 
                  command=self.delete_army)
        btn_delete.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["delete_army"] = {"type": "button", "widget": btn_delete}
        
        btn_create = ttk.Button(bot_frame, text=t("gui.buttons.create_army"), 
                  command=self.create_army)
        btn_create.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["create_army"] = {"type": "button", "widget": btn_create}
        
        btn_train = ttk.Button(bot_frame, text=t("gui.buttons.train_army"), 
                  command=self.train_army)
        btn_train.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["train_army"] = {"type": "button", "widget": btn_train}
        
        btn_donate = ttk.Button(bot_frame, text=t("gui.buttons.donate_castle"), 
                  command=self.donate_castle)
        btn_donate.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["donate_castle"] = {"type": "button", "widget": btn_donate}
        
        btn_request = ttk.Button(bot_frame, text=t("gui.buttons.request_castle"), 
                  command=self.request_castle)
        btn_request.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["request_castle"] = {"type": "button", "widget": btn_request}
        
        # Seção: Start Bot
        start_bot_frame = ttk.LabelFrame(parent, text=t("gui.labels.start_bot"), padding=10)
        start_bot_frame.pack(fill=tk.X, padx=5, pady=5)
        self.ui_widgets["start_bot"] = {"type": "labelframe", "widget": start_bot_frame}
        
        self.btn_start_bot = ttk.Button(start_bot_frame, text=t("gui.buttons.start_bot"), 
                  command=self.start_bot)
        self.btn_start_bot.pack(side=tk.LEFT, padx=2)
        self.ui_widgets["start_bot_button"] = {"type": "button", "widget": self.btn_start_bot}
        
    def setup_army_tab(self, parent):
        # Lista de tropas disponíveis
        troops_frame = ttk.LabelFrame(parent, text="Available Troops", padding=10)
        troops_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox com scroll
        listbox_frame = ttk.Frame(troops_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.troops_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        self.troops_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.troops_listbox.yview)
        
        # Botões para adicionar/remover tropas
        troops_buttons = ttk.Frame(troops_frame)
        troops_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(troops_buttons, text="Refresh List", 
                  command=self.refresh_troops_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(troops_buttons, text="Add Selected", 
                  command=self.add_troop_to_army).pack(side=tk.LEFT, padx=2)
        
        # Lista de tropas no exército
        army_list_frame = ttk.LabelFrame(parent, text="Army Configuration", padding=10)
        army_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para exército
        tree_frame = ttk.Frame(army_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Troop", "Quantity")
        self.army_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.army_tree.heading("Troop", text="Troop")
        self.army_tree.heading("Quantity", text="Quantity")
        self.army_tree.column("Troop", width=200)
        self.army_tree.column("Quantity", width=100)
        self.army_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.army_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.army_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Botões para gerenciar exército
        army_buttons = ttk.Frame(army_list_frame)
        army_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(army_buttons, text="Remove Selected", 
                  command=self.remove_troop_from_army).pack(side=tk.LEFT, padx=2)
        ttk.Button(army_buttons, text="Update Quantity", 
                  command=self.update_troop_quantity).pack(side=tk.LEFT, padx=2)
        ttk.Button(army_buttons, text="Save Army Config", 
                  command=self.save_army_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(army_buttons, text="Load Army Config", 
                  command=self.load_army_config).pack(side=tk.LEFT, padx=2)
        
        # Campo para quantidade
        quantity_frame = ttk.Frame(army_list_frame)
        quantity_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quantity_frame, text="Quantity:").pack(side=tk.LEFT, padx=5)
        self.quantity_var = tk.StringVar(value="1")
        ttk.Entry(quantity_frame, textvariable=self.quantity_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.refresh_troops_list()
        
    def setup_log_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_clear = ttk.Button(parent, text=t("gui.buttons.clear_log"), 
                  command=self.clear_log)
        btn_clear.pack(pady=5)
        self.ui_widgets["clear_log"] = {"type": "button", "widget": btn_clear}
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            # Log ainda não inicializado, apenas print
            print(message)
        
    def clear_log(self):
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.delete(1.0, tk.END)
        
    def run_in_thread(self, func, *args, **kwargs):
        """Executa função em thread separada"""
        if self.is_running:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.another_operation_running")
            )
            return
            
        self.is_running = True
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.log(f"ERROR: {str(e)}")
                messagebox.showerror(t("gui.messages.error"), str(e))
            finally:
                self.is_running = False
                
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        
    # BlueStacks Control Methods
    def kill_bluestacks(self):
        self.run_in_thread(self._kill_bluestacks)
        
    def _kill_bluestacks(self):
        self.log("[BS] Killing BlueStacks...")
        kill_bluestacks()
        self.log("[BS] BlueStacks killed")
        
    def configure_bluestacks(self):
        self.run_in_thread(self._configure_bluestacks)
        
    def _configure_bluestacks(self):
        self.log("[BS] Configuring BlueStacks...")
        configure_bluestacks()
        self.log("[BS] BlueStacks configured")
        
    def start_bluestacks(self):
        self.run_in_thread(self._start_bluestacks)
        
    def _start_bluestacks(self):
        self.log("[BS] Starting BlueStacks...")
        start_bluestacks()
        self.log("[BS] BlueStacks started")
        
    def validate_adb(self):
        self.run_in_thread(self._validate_adb)
        
    def _validate_adb(self):
        self.log("[ADB] Validating connection...")
        adb_validate()
        self.log("[ADB] Validation complete")
        
    # Device Methods
    def connect_device(self):
        self.run_in_thread(self._connect_device)
        
    def _connect_device(self):
        from config.settings import Settings
        self.log("[DEVICE] Connecting...")
        host = Settings.BLUESTACK_HOST
        port = str(Settings.BLUESTACK_PORT)
        self.device = AndroidDevice(host=host, port=port)
        self.log(f"[DEVICE] Connected to {host}:{port}")
        
    def take_screenshot(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._take_screenshot)
        
    def _take_screenshot(self):
        self.log("[DEVICE] Taking screenshot...")
        self.device.screenshot()
        self.log("[DEVICE] Screenshot saved to screen.png")
        
    # Game Methods
    def init_game(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._init_game)
        
    def _init_game(self):
        from config.settings import Settings
        import time
        self.log("[GAME] Initializing game...")
        self.device.open_app(Settings.GAME_PACKAGE)
        self.log("[GAME] Waiting for game to load...")
        time.sleep(8)
        self.log("[GAME] Zooming out...")
        self.device.zoom_out(steps=15, duration_ms=500)
        time.sleep(0.5)
        self.device.zoom_out(steps=15, duration_ms=500)
        time.sleep(0.3)
        self.log("[GAME] Game initialized")
        
    def center_view(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._center_view)
        
    def _center_view(self):
        # Use default values (can be made configurable in Settings if needed)
        move_right = 100
        move_down = -50
        self.log(f"[GAME] Centering view (right={move_right}, down={move_down})...")
        self.device.center_view(move_right=move_right, move_down=move_down)
        self.log("[GAME] View centered")
        
    # Bot Function Methods
    def delete_army(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._delete_army)
        
    def _delete_army(self):
        self.log("[BOT] Deleting army...")
        delete_army(self.device, castel_delete=True)
        self.log("[BOT] Army deleted")
        
    def create_army(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._create_army)
        
    def _create_army(self):
        self.log("[BOT] Creating army...")
        create_army(self.device, open_menu=True)
        self.log("[BOT] Army created")
        
    def train_army(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._train_army)
        
    def _train_army(self):
        self.log("[BOT] Training army...")
        train_army(self.device)
        self.log("[BOT] Army trained")
        
    def donate_castle(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._donate_castle)
        
    def _donate_castle(self):
        self.log("[BOT] Donating to castle...")
        donate_castle(self.device)
        self.log("[BOT] Donation complete")
        
    def request_castle(self):
        if not self.device:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_connect_device")
            )
            return
        self.run_in_thread(self._request_castle)
        
    def _request_castle(self):
        self.log("[BOT] Requesting from castle...")
        request_castle(self.device)
        self.log("[BOT] Request complete")
        
    # Army Configuration Methods
    def refresh_troops_list(self):
        self.troops_listbox.delete(0, tk.END)
        troops = list_available_troops()
        for troop in troops:
            self.troops_listbox.insert(tk.END, troop)
        self.log(f"[ARMY] Loaded {len(troops)} available troops")
        
    def add_troop_to_army(self):
        selection = self.troops_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_select_troop")
            )
            return
            
        troop_name = self.troops_listbox.get(selection[0])
        quantity = int(self.quantity_var.get())
        
        # Verifica se já existe
        for item in self.army_tree.get_children():
            if self.army_tree.item(item, "values")[0] == troop_name:
                messagebox.showinfo(
                    t("gui.messages.success"), 
                    t("gui.messages.troop_already_in_army", troop_name)
                )
                return
                
        self.army_tree.insert("", tk.END, values=(troop_name, quantity))
        self.log(f"[ARMY] Added {quantity}x {troop_name}")
        
    def remove_troop_from_army(self):
        selection = self.army_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_select_troop_to_remove")
            )
            return
            
        for item in selection:
            values = self.army_tree.item(item, "values")
            self.army_tree.delete(item)
            self.log(f"[ARMY] Removed {values[0]}")
            
    def update_troop_quantity(self):
        selection = self.army_tree.selection()
        if not selection:
            messagebox.showwarning(
                t("gui.messages.warning"), 
                t("gui.messages.please_select_troop_to_update")
            )
            return
            
        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror(
                t("gui.messages.error"), 
                t("gui.messages.invalid_quantity")
            )
            return
            
        for item in selection:
            values = self.army_tree.item(item, "values")
            self.army_tree.item(item, values=(values[0], quantity))
            self.log(f"[ARMY] Updated {values[0]} quantity to {quantity}")
            
    def save_army_config(self):
        troops = []
        for item in self.army_tree.get_children():
            values = self.army_tree.item(item, "values")
            troops.append({
                "name": values[0],
                "quantity": int(values[1])
            })
            
        config = {
            "troops": troops,
            "spells": [],
            "notes": "Army configuration saved from GUI"
        }
        
        config_path = os.path.join("config", "army.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        self.log(f"[ARMY] Saved army configuration with {len(troops)} troop types")
        messagebox.showinfo(
            t("gui.messages.success"), 
            t("gui.messages.army_config_saved")
        )
        
    def load_army_config(self):
        config_path = os.path.join("config", "army.json")
        if not os.path.exists(config_path):
            self.log("[ARMY] No army configuration found")
            return
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # Limpa tree
        for item in self.army_tree.get_children():
            self.army_tree.delete(item)
            
        # Adiciona tropas
        for troop in config.get("troops", []):
            self.army_tree.insert("", tk.END, values=(
                troop.get("name", ""),
                troop.get("quantity", 1)
            ))
            
        self.log(f"[ARMY] Loaded army configuration with {len(config.get('troops', []))} troop types")
        
    def start_bot(self):
        """Start the bot using fixed global settings."""
        if self.is_running:
            messagebox.showwarning(
                t("gui.messages.warning"),
                "Bot is already running. Please wait for the current operation to complete."
            )
            return
        
        self.run_in_thread(self._start_bot)
    
    def _start_bot(self):
        """Internal method to start the bot in a separate thread."""
        try:
            from core.bot_controller import BotController
            from config.settings import Settings
            
            self.log("[BOT] Initializing bot controller...")
            
            # Use fixed global settings
            host = Settings.BLUESTACK_HOST
            port = str(Settings.BLUESTACK_PORT)
            
            # Initialize bot controller
            self.bot_controller = BotController(host=host, port=port)
            self.log("[BOT] Bot controller initialized")
            
            # Use default move values (fixed)
            move_right = 100
            move_down = -50
            
            # Initialize game
            self.log("[BOT] Initializing game...")
            success = self.bot_controller.initialize_game(move_right=move_right, move_down=move_down)
            
            if success:
                self.log("[BOT] Game initialized successfully")
                self.log("[BOT] Bot is ready! Use the buttons in the Bot Functions section to perform actions.")
            else:
                self.log("[BOT] Failed to initialize game")
                messagebox.showerror(
                    t("gui.messages.error"),
                    "Failed to initialize game. Please check your device connection."
                )
                
        except Exception as e:
            self.log(f"[BOT] Error starting bot: {str(e)}")
            messagebox.showerror(
                t("gui.messages.error"),
                f"Error starting bot: {str(e)}"
            )


def main():
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
