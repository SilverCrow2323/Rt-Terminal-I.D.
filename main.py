#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
================================================================================
  Rt:Terminal I.D. v4.0 — SPDW FACTORY
  RSPDW Chou Henka Project — RetroFW 2.3 Terminal

  "Stampa lineare simmetrica. Salvataggio comandi JSON. Multi-sessione."
================================================================================
"""
import os
import sys
import json
import subprocess
import gc
import time

# --- RetroFW 2.3 Environment Setup ---
for var in ["SDL_VIDEODRIVER", "SDL_FBDEV"]:
    if var in os.environ:
        del os.environ[var]
os.environ["SDL_NOMOUSE"] = "1"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

W, H = 320, 240
FPS = 30

# --- Absolute Paths (RetroFW Protocol) ---
BASE_DIR = os.path.expanduser("~/.rspdw/rt_terminal")
FONT_DIR = os.path.join(BASE_DIR, "fonts")
USER_JSON = os.path.join(BASE_DIR, "rt_tid.json")

# Ensure directories exist
for path in [BASE_DIR, FONT_DIR]:
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            pass

# --- System Commands (Immutable) ---
SYS_ALMANACCO = [
    {"name": "Detailed File List", "cmd": "ls -la"},
    {"name": "SD Storage Space", "cmd": "df -h"},
    {"name": "Monitor CPU & RAM", "cmd": "top"},
    {"name": "Process Tree", "cmd": "ps w"},
    {"name": "Physical RAM State", "cmd": "free -m"},
    {"name": "Latest Kernel Logs", "cmd": "dmesg | tail -n 20"},
    {"name": "Kernel Hardware Info", "cmd": "uname -a"},
    {"name": "Network/USB Interfaces", "cmd": "ifconfig -a"},
    {"name": "Current Folder Size", "cmd": "du -sh ."},
    {"name": "Force Kill Python", "cmd": "killall -9 python"},
    {"name": "Peremptory Reboot", "cmd": "reboot"},
    {"name": "Safe Poweroff", "cmd": "poweroff"}
]

# --- Themes ---
THEMES = {
    "Cyan Neo":   {"bg": (3, 4, 8),    "panel": (12, 16, 28),   "primary": (0, 255, 204), "sec": (255, 0, 85),   "grid": (20, 35, 60),   "dim": (100, 110, 130)},
    "Matrix G":   {"bg": (2, 6, 2),    "panel": (5, 20, 5),     "primary": (0, 255, 68),  "sec": (0, 136, 34),   "grid": (10, 40, 10),   "dim": (80, 120, 80)},
    "Amber Box":  {"bg": (8, 4, 1),    "panel": (22, 10, 2),    "primary": (255, 136, 0), "sec": (190, 35, 0),   "grid": (50, 25, 0),    "dim": (140, 100, 60)},
    "Crimson G":  {"bg": (10, 2, 3),   "panel": (26, 5, 10),    "primary": (255, 0, 76),  "sec": (130, 0, 40),   "grid": (50, 12, 20),   "dim": (140, 80, 90)},
    "Void Blue":  {"bg": (2, 2, 10),   "panel": (8, 8, 24),     "primary": (100, 149, 237),"sec": (65, 105, 225), "grid": (15, 15, 50),   "dim": (80, 80, 120)},
    "Solarized":  {"bg": (0, 43, 54),  "panel": (7, 54, 66),    "primary": (42, 161, 152),"sec": (211, 54, 130), "grid": (20, 60, 70),   "dim": (100, 120, 120)}
}
THEME_KEYS = sorted(THEMES.keys())

# --- Localization ---
LANG_DICT = {
    "IT": {
        "title_opts": " [ OPZIONI DI SISTEMA SPDW ] ",
        "session": "Sessione",
        "new_session": "Nuova Sessione",
        "log_size": "Dimensione Log",
        "print_width": "Larghezza Area",
        "theme": "Tema Interfaccia",
        "lang": "Lingua",
        "alm": "Almanacco Comandi",
        "load_font": "Carica Font",
        "about": "Informazioni Core",
        "close_menu": "Chiudi Menu",
        "save_cmd": "Salva Comando",
        "alm_title": "=== ALMANACCO COMPLETO ===",
        "alm_help": "[A] Esegui | [B] Esci | [Y] Elimina",
        "shell_start": "--- Sessione Shell Iniziata ---",
        "shell_ready": "Pronto Root Privilegi (#)...",
        "device": "[FERRO]",
        "save_name": "Nome Comando:",
        "save_desc": "Descrizione:",
        "save_cmd_lbl": "Comando:",
        "save_confirm": "[A] Salva | [B] Annulla",
        "saved_ok": "Comando salvato in JSON!",
        "deleted_ok": "Comando eliminato!",
        "no_cmds": "Nessun comando utente",
        "edit_mode": "[MODIFICA COMANDO]",
        "cursor_blink": "_"
    },
    "EN": {
        "title_opts": " [ SPDW SYSTEM OPTIONS ] ",
        "session": "Session",
        "new_session": "New Session",
        "log_size": "Log Size",
        "print_width": "Print Width",
        "theme": "UI Theme",
        "lang": "Language",
        "alm": "Command Almanac",
        "load_font": "Load Font",
        "about": "About Core",
        "close_menu": "Close Menu",
        "save_cmd": "Save Command",
        "alm_title": "=== COMPLETE ALMANAC ===",
        "alm_help": "[A] Execute | [B] Exit | [Y] Delete",
        "shell_start": "--- Shell Session Started ---",
        "shell_ready": "Ready Root Privileges (#)...",
        "device": "[DEVICE]",
        "save_name": "Command Name:",
        "save_desc": "Description:",
        "save_cmd_lbl": "Command:",
        "save_confirm": "[A] Save | [B] Cancel",
        "saved_ok": "Command saved to JSON!",
        "deleted_ok": "Command deleted!",
        "no_cmds": "No user commands",
        "edit_mode": "[EDIT COMMAND]",
        "cursor_blink": "_"
    }
}

# --- Key Mappings (RetroFW Handheld) ---
K_A, K_A_ALT = pygame.K_LCTRL, pygame.K_z
K_B, K_B_ALT = pygame.K_LALT, pygame.K_x
K_Y, K_Y_ALT = pygame.K_LSHIFT, pygame.K_a
K_L, K_L_ALT = pygame.K_TAB, pygame.K_q
K_R, K_R_ALT = pygame.K_BACKSPACE, pygame.K_w
K_X, K_X_ALT = pygame.K_SPACE, pygame.K_s

# --- On-Screen Keyboard Layouts ---
LAYOUTS = [
    [
        ['q','w','e','r','t','y','u','i','o','p'],
        ['a','s','d','f','g','h','j','k','l','-'],
        ['z','x','c','v','b','n','m','.',',','/'],
        ['TAB', 'CTRL', 'ALT', 'ESC', 'BKSP', 'EXE', 'ls', 'cd..', 'clear', 'pwd']
    ],
    [
        ['Q','W','E','R','T','Y','U','I','O','P'],
        ['A','S','D','F','G','H','J','K','L','_'],
        ['Z','X','C','V','B','N','M',';',':','?'],
        ['HOME', 'END', 'CTRL', 'ALT', 'BKSP', 'EXE', 'ls -la', 'top', 'df', 'env']
    ],
    [
        ['1','2','3','4','5','6','7','8','9','0'],
        ['!','@','#','$','%','^','&','*','(',')'],
        ['=','+','{','}','[',']','<','>','\\','|'],
        ['`','~','"',"'", 'BKSP', 'EXE', '&&', '||', ' > ', 'pstree']
    ]
]
LAYOUT_NAMES = ["abc", "ABC", "sym"]


def get_cpu_ram():
    cpu, ram = "JZ4760B 528M", "128MB DDR2"
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line or "cpu model" in line:
                        cpu = line.split(":")[1].strip()[:14]
                        break
        except:
            pass
    if os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        ram = line.split(":")[1].strip().replace(" kB", "KB")
                        break
        except:
            pass
    return cpu, ram


def load_user_data():
    """Carica i dati utente dal JSON. Se non esiste, crea il file di default."""
    default_data = {
        "theme": "Cyan Neo",
        "font_size": 13,
        "language": "IT",
        "font_file": "default",
        "print_width": 308,
        "almanacco": []
    }
    if os.path.exists(USER_JSON):
        try:
            with open(USER_JSON, "r") as f:
                data = json.load(f)
            # Merge con default per sicurezza
            for key in default_data:
                if key not in data:
                    data[key] = default_data[key]
            return data
        except:
            return default_data
    else:
        # Crea il file di default
        try:
            with open(USER_JSON, "w") as f:
                json.dump(default_data, f, indent=4)
        except:
            pass
        return default_data


def save_user_data(data):
    """Salva i dati utente nel JSON."""
    try:
        with open(USER_JSON, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        return False


class TerminalSession(object):
    def __init__(self, session_id, lang):
        self.id = session_id
        self.current_dir = os.path.expanduser("~") if os.path.exists(os.path.expanduser("~")) else os.getcwd()
        self.cmd_buffer = ""
        self.output_history = [LANG_DICT[lang]["shell_start"], LANG_DICT[lang]["shell_ready"]]
        self.scroll_offset = 0
        self.last_cmd_time = 0

    def sanitize_and_process(self, text, max_pixels, font):
        """Pulisce le stringhe e calcola la lunghezza lineare."""
        lines = []
        raw_lines = text.replace('\r', '').split('\n')

        for raw_line in raw_lines:
            raw_line = raw_line.replace('\t', '    ')

            try:
                if not isinstance(raw_line, unicode):
                    raw_line = raw_line.decode('utf-8', 'ignore')
            except:
                raw_line = unicode(raw_line)

            if font.size(raw_line)[0] <= max_pixels:
                lines.append(raw_line)
            else:
                short_line = u""
                for char in raw_line:
                    test_str = short_line + char + u".."
                    if font.size(test_str)[0] <= max_pixels:
                        short_line += char
                    else:
                        break
                lines.append(short_line + u"..")
        return lines

    def execute_command(self, max_w, font):
        cmd = self.cmd_buffer.strip()
        if not cmd:
            return None

        display_cmd = cmd.decode('utf-8', 'ignore') if not isinstance(cmd, unicode) else cmd
        self.output_history.append(u"[root@retrofw]# %s" % display_cmd)
        self.last_cmd_time = time.time()

        if cmd == "clear":
            self.output_history = []
            self.cmd_buffer = ""
            self.scroll_offset = 0
            return cmd
        elif cmd == "cd..":
            try:
                os.chdir("..")
                self.current_dir = os.getcwd()
                self.output_history.append(u"DIR: %s" % self.current_dir.decode('utf-8', 'ignore') if not isinstance(self.current_dir, unicode) else u"DIR: %s" % self.current_dir)
            except Exception as e:
                self.output_history.extend(self.sanitize_and_process(str(e), max_w, font))
            self.cmd_buffer = ""
            return cmd
        elif cmd.startswith("cd "):
            target = cmd[3:].strip()
            try:
                os.chdir(target)
                self.current_dir = os.getcwd()
                self.output_history.append(u"DIR: %s" % self.current_dir.decode('utf-8', 'ignore') if not isinstance(self.current_dir, unicode) else u"DIR: %s" % self.current_dir)
            except Exception as e:
                self.output_history.extend(self.sanitize_and_process(str(e), max_w, font))
            self.cmd_buffer = ""
            return cmd

        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.current_dir)
            stdout, stderr = process.communicate()
            if stdout:
                self.output_history.extend(self.sanitize_and_process(stdout, max_w, font))
            if stderr:
                self.output_history.extend(self.sanitize_and_process("ERRORE: " + stderr, max_w, font))
        except Exception as e:
            self.output_history.extend(self.sanitize_and_process("Fallimento: " + str(e), max_w, font))

        self.cmd_buffer = ""
        return cmd


class AppCore(object):
    def __init__(self):
        # Carica configurazione dal JSON
        self.user_data = load_user_data()
        self.cfg = {
            "theme": self.user_data.get("theme", "Cyan Neo"),
            "font_size": self.user_data.get("font_size", 13),
            "print_width": self.user_data.get("print_width", 308),
            "language": self.user_data.get("language", "IT"),
            "font_file": self.user_data.get("font_file", "default")
        }

        self.sessions = [TerminalSession(1, self.cfg["language"])]
        self.current_idx = 0
        self.macro_ptr = -1

        self.kbd_row = 0
        self.kbd_col = 0
        self.layout_idx = 0
        self.kbd_visible = True

        self.menu_open = False
        self.about_open = False
        self.almanacco_open = False
        self.save_cmd_open = False
        self.edit_cmd_open = False
        self.edit_cmd_index = -1

        self.menu_sel = 0
        self.alm_sel = 0

        self.menu_keys = ["session", "new_session", "log_size", "print_width", "theme", "lang", "alm", "save_cmd", "load_font", "about", "close_menu"]
        self.y_held = False
        self.cursor_visible = True
        self.cursor_timer = 0

        self.available_fonts = ["default"]
        self.reload_fonts_list()
        self.build_almanacco()

        self.font_title = None
        self.font_log = None
        self.font_kbd = pygame.font.Font(None, 14)
        self.font_small = pygame.font.Font(None, 12)
        self.cache_fonts()

        # Save command form fields
        self.save_field = 0  # 0=name, 1=desc, 2=cmd
        self.save_name = ""
        self.save_desc = ""
        self.save_cmd_text = ""
        self.save_status_msg = ""
        self.save_status_timer = 0

    def reload_fonts_list(self):
        self.available_fonts = ["default"]
        if os.path.exists(FONT_DIR):
            try:
                for f in os.listdir(FONT_DIR):
                    if f.endswith(".ttf"):
                        self.available_fonts.append(f)
            except:
                pass

    def build_almanacco(self):
        self.full_almanacco = []
        u_list = self.user_data.get("almanacco", [])

        if u_list:
            self.full_almanacco.append({"type": "header", "name": "--- USER COMMANDS ---", "cmd": ""})
            for item in u_list:
                self.full_almanacco.append({
                    "type": "cmd",
                    "name": item.get("name", "Unnamed"),
                    "desc": item.get("description", ""),
                    "cmd": item.get("cmd", ""),
                    "editable": True
                })

        if len(self.full_almanacco) > 0:
            self.full_almanacco.append({"type": "header", "name": "--- SYSTEM COMMANDS ---", "cmd": ""})
        else:
            self.full_almanacco.append({"type": "header", "name": "--- COMMANDS ---", "cmd": ""})

        for item in SYS_ALMANACCO:
            self.full_almanacco.append({
                "type": "cmd",
                "name": item["name"],
                "desc": "",
                "cmd": item["cmd"],
                "editable": False
            })

    def save_config_to_json(self):
        """Salva la configurazione corrente nel JSON."""
        self.user_data["theme"] = self.cfg["theme"]
        self.user_data["font_size"] = self.cfg["font_size"]
        self.user_data["print_width"] = self.cfg["print_width"]
        self.user_data["language"] = self.cfg["language"]
        self.user_data["font_file"] = self.cfg["font_file"]
        save_user_data(self.user_data)

    def cache_fonts(self):
        f_file = self.cfg["font_file"]
        f_path = os.path.join(FONT_DIR, f_file) if f_file != "default" else None
        if f_path and not os.path.exists(f_path):
            f_path = None

        try:
            self.font_log = pygame.font.Font(f_path, self.cfg["font_size"])
            self.font_title = pygame.font.Font(f_path, 16)
            self.font_small = pygame.font.Font(f_path, 11)
        except:
            self.font_log = pygame.font.Font(None, self.cfg["font_size"])
            self.font_title = pygame.font.Font(None, 16)
            self.font_small = pygame.font.Font(None, 11)

    def get_save_form_y_positions(self):
        """Restituisce le Y per i campi del form di salvataggio."""
        return [70, 100, 130]

    def draw_save_cmd(self, surf):
        t = THEMES[self.cfg["theme"]]
        lng = self.cfg["language"]

        overlay = pygame.Surface((W, H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surf.blit(overlay, (0, 0))

        pygame.draw.rect(surf, t["bg"], (15, 40, 290, 160))
        pygame.draw.rect(surf, t["primary"], (15, 40, 290, 160), 2)

        title = LANG_DICT[lng]["save_cmd"] if not self.edit_cmd_open else LANG_DICT[lng]["edit_mode"]
        ts_title = self.font_title.render(title, True, t["primary"])
        surf.blit(ts_title, (25, 45))

        fields = [
            (LANG_DICT[lng]["save_name"], self.save_name),
            (LANG_DICT[lng]["save_desc"], self.save_desc),
            (LANG_DICT[lng]["save_cmd_lbl"], self.save_cmd_text)
        ]

        y_positions = self.get_save_form_y_positions()
        for idx, (label, value) in enumerate(fields):
            is_sel = (idx == self.save_field)
            color = t["primary"] if is_sel else t["dim"]

            ts_label = self.font_log.render(label, True, color)
            surf.blit(ts_label, (25, y_positions[idx]))

            # Input box
            box_color = t["primary"] if is_sel else t["grid"]
            pygame.draw.rect(surf, t["panel"], (25, y_positions[idx] + 14, 270, 16))
            pygame.draw.rect(surf, box_color, (25, y_positions[idx] + 14, 270, 16), 1)

            display_val = value
            if is_sel and self.cursor_visible:
                display_val += "_"

            ts_val = self.font_log.render(display_val[:40], True, (230, 235, 245))
            surf.blit(ts_val, (28, y_positions[idx] + 15))

        # Status message
        if self.save_status_msg and self.save_status_timer > 0:
            ts_status = self.font_log.render(self.save_status_msg, True, t["sec"])
            surf.blit(ts_status, (25, 185))

        ts_help = self.font_small.render(LANG_DICT[lng]["save_confirm"], True, t["grid"])
        surf.blit(ts_help, (25, 200))

    def draw_menu(self, surf):
        t = THEMES[self.cfg["theme"]]
        lng = self.cfg["language"]

        overlay = pygame.Surface((W, H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(170)
        surf.blit(overlay, (0, 0))

        pygame.draw.rect(surf, t["bg"], (20, 8, 280, 224))
        pygame.draw.rect(surf, t["primary"], (20, 8, 280, 224), 2)

        lbl_title = self.font_log.render(LANG_DICT[lng]["title_opts"], True, t["bg"], t["primary"])
        surf.blit(lbl_title, (30, 13))

        for idx, key in enumerate(self.menu_keys):
            is_sel = (idx == self.menu_sel)
            color = t["primary"] if is_sel else (170, 175, 190)

            item_name = LANG_DICT[lng][key]
            val_str = ""
            if key == "session":
                val_str = " < S%d / %d >" % (self.current_idx + 1, len(self.sessions))
            elif key == "log_size":
                val_str = " < %d pt >" % self.cfg["font_size"]
            elif key == "print_width":
                val_str = " < %d px >" % self.cfg["print_width"]
            elif key == "theme":
                val_str = " < %s >" % self.cfg["theme"]
            elif key == "lang":
                val_str = " < %s >" % self.cfg["language"]
            elif key == "load_font":
                val_str = " < %s >" % self.cfg["font_file"]

            disp_text = (" >> " if is_sel else "    ") + item_name + val_str
            if is_sel:
                pygame.draw.rect(surf, t["panel"], (24, 34 + (idx * 18), 272, 16))
            ts = self.font_log.render(disp_text, True, color)
            surf.blit(ts, (28, 36 + (idx * 18)))

    def draw_almanacco(self, surf):
        t = THEMES[self.cfg["theme"]]
        lng = self.cfg["language"]

        pygame.draw.rect(surf, t["bg"], (10, 10, 300, 220))
        pygame.draw.rect(surf, t["sec"], (10, 10, 300, 220), 2)

        ts_title = self.font_log.render(LANG_DICT[lng]["alm_title"], True, t["primary"])
        surf.blit(ts_title, (20, 15))

        max_items = 10
        start_view = max(0, min(self.alm_sel - max_items + 3, len(self.full_almanacco) - max_items))
        view_list = self.full_almanacco[start_view:start_view + max_items]

        for idx, item in enumerate(view_list):
            real_idx = start_view + idx
            is_sel = (real_idx == self.alm_sel)
            yy = 36 + (idx * 16)

            if item["type"] == "header":
                ts = self.font_log.render(item["name"], True, t["sec"])
                surf.blit(ts, (20, yy))
            else:
                if is_sel:
                    pygame.draw.rect(surf, t["panel"], (15, 34 + (idx * 16), 290, 15))

                color = t["primary"] if is_sel else (240, 240, 245)
                editable_mark = "*" if item.get("editable") else " "
                disp = "%s%s -> %s" % (editable_mark, item["name"], item["cmd"])
                if len(disp) > 42:
                    disp = disp[:39] + "..."
                ts = self.font_log.render(("> " if is_sel else "  ") + disp, True, color)
                surf.blit(ts, (18, yy))

                if is_sel and item.get("desc"):
                    desc_str = "[Info: %s]" % item["desc"]
                    if len(desc_str) > 44:
                        desc_str = desc_str[:41] + "..."
                    ts_desc = self.font_small.render(desc_str, True, (150, 160, 175))
                    surf.blit(ts_desc, (20, 200))

        ts_inf = self.font_small.render(LANG_DICT[lng]["alm_help"], True, t["grid"])
        surf.blit(ts_inf, (20, 215))

    def draw_about(self, surf):
        t = THEMES[self.cfg["theme"]]
        pygame.draw.rect(surf, (5, 5, 10), (20, 20, 280, 200))
        pygame.draw.rect(surf, t["primary"], (20, 20, 280, 200), 2)
        lines = [
            "  === Rt:Terminal I.D. Core ===",
            " Chou Henka Engine Module v4.0.0",
            " LAB: SPDW Factory (Sector K)",
            " Operator: sirpip**** w/Minoru7",
            " General LORE from: SPDW [Sir Pips Du Wilson] / Dual-Cluster-Crossmedial Project",
            " Basically Everything: I.R. Minoru7, Multi-JSON Dictat...ehm, Governor",
            "---------------------------------",
            " Features: JSON Save | Multi-Session",
            " Symmetric Print | 6 Themes | IT/EN",
            " User Commands | On-Screen Keyboard",
            "---------------------------------",
            " Press [B] to return / indietro."
        ]
        for idx, line in enumerate(lines):
            color = t["primary"] if "Operator" in line else (230, 230, 235)
            ts = self.font_log.render(line, True, color)
            surf.blit(ts, (26, 26 + (idx * 13)))

    def draw_main(self, surf):
        t = THEMES[self.cfg["theme"]]
        lng = self.cfg["language"]
        sess = self.sessions[self.current_idx]
        surf.fill(t["bg"])

        # Header
        ts_id = self.font_title.render("Rt:Terminal I.D.", True, t["sec"])
        surf.blit(ts_id, (8, 4))

        ts_fw = self.font_log.render("RetroFW 2.3", True, t["dim"])
        ts_proj = self.font_log.render("Chou Henka Proj.", True, t["primary"])
        surf.blit(ts_fw, (8, 22))
        surf.blit(ts_proj, (8, 34))

        # Info panel
        pygame.draw.rect(surf, t["panel"], (175, 4, 138, 46))
        pygame.draw.rect(surf, t["grid"], (175, 4, 138, 46), 1)

        lbl_dev = self.font_log.render(LANG_DICT[lng]["device"], True, t["sec"])
        cpu_str, ram_str = get_cpu_ram()
        ts_cpu = self.font_log.render(cpu_str, True, (200, 205, 220))
        ts_ram = self.font_log.render(ram_str, True, t["primary"])

        surf.blit(lbl_dev, (180, 6))
        surf.blit(ts_cpu, (180, 18))
        surf.blit(ts_ram, (180, 30))

        # Session indicator
        sess_info = "S%d/%d" % (self.current_idx + 1, len(self.sessions))
        ts_sess = self.font_small.render(sess_info, True, t["dim"])
        surf.blit(ts_sess, (W - 40, 4))

        pygame.draw.line(surf, t["grid"], (0, 54), (W, 54), 1)

        # Terminal area
        is_osk_visible = self.kbd_visible and not self.y_held
        kbd_y_start = H - 96 if is_osk_visible else H

        line_height = self.cfg["font_size"] + 2
        max_visible = (kbd_y_start - 54 - 16) // line_height

        start_x = (W - self.cfg["print_width"]) / 2

        visible_lines = sess.output_history[sess.scroll_offset : sess.scroll_offset + max_visible]
        for idx, line in enumerate(visible_lines):
            if line.startswith(u"[root"):
                color = t["primary"]
            elif line.startswith(u"ERRORE:") or line.startswith(u"Fallimento:"):
                color = t["sec"]
            elif line.startswith(u"DIR:"):
                color = t["dim"]
            else:
                color = (230, 235, 245)
            ts = self.font_log.render(line, True, color)
            surf.blit(ts, (start_x, 56 + (idx * line_height)))

        # Prompt bar
        short_dir = sess.current_dir if len(sess.current_dir) < 16 else "...%s" % sess.current_dir[-13:]
        cursor = "_" if self.cursor_visible else " "
        prompt_str = "[S%d:%s]# %s%s" % (sess.id, short_dir, sess.cmd_buffer, cursor)
        pygame.draw.rect(surf, (15, 16, 24), (0, kbd_y_start - 15, W, 14))
        ts_prompt = self.font_log.render(prompt_str, True, t["primary"])
        surf.blit(ts_prompt, (start_x, kbd_y_start - 14))

        # On-screen keyboard
        if is_osk_visible:
            ts_tag = self.font_log.render("[%s]" % LAYOUT_NAMES[self.layout_idx], True, t["sec"])
            surf.blit(ts_tag, (W - 45, kbd_y_start - 14))

            layout = LAYOUTS[self.layout_idx]
            key_w, key_h = 32, 24
            for r_idx, row in enumerate(layout):
                for c_idx, val in enumerate(row):
                    kx = c_idx * key_w
                    ky = kbd_y_start + (r_idx * key_h)

                    is_selected = (r_idx == self.kbd_row and c_idx == self.kbd_col)
                    bg_color = (45, 50, 70) if is_selected else (16, 18, 24)
                    border_color = t["primary"] if is_selected else (45, 48, 58)

                    pygame.draw.rect(surf, bg_color, (kx + 1, ky + 1, key_w - 2, key_h - 2))
                    pygame.draw.rect(surf, border_color, (kx, ky, key_w, key_h), 1)

                    ts_key = self.font_kbd.render(val, True, t["primary"] if is_selected else (235, 240, 250))
                    rect_key = ts_key.get_rect()
                    rect_key.center = (kx + (key_w / 2), ky + (key_h / 2))
                    surf.blit(ts_key, rect_key)

    def handle_save_cmd_input(self, event, keys):
        """Gestisce l'input per il form di salvataggio comando."""
        lng = self.cfg["language"]

        if event.key == pygame.K_UP:
            self.save_field = (self.save_field - 1) % 3
        elif event.key == pygame.K_DOWN:
            self.save_field = (self.save_field + 1) % 3
        elif event.key == pygame.K_LEFT:
            # Navigate within text (simplified: just move cursor not implemented, use backspace)
            pass
        elif event.key == pygame.K_RIGHT:
            pass
        elif event.key in [K_A, K_A_ALT]:
            # Save the command
            if self.save_name.strip() and self.save_cmd_text.strip():
                new_cmd = {
                    "name": self.save_name.strip(),
                    "description": self.save_desc.strip(),
                    "cmd": self.save_cmd_text.strip()
                }

                if self.edit_cmd_open and self.edit_cmd_index >= 0:
                    # Edit existing
                    user_cmds = self.user_data.get("almanacco", [])
                    if self.edit_cmd_index < len(user_cmds):
                        user_cmds[self.edit_cmd_index] = new_cmd
                else:
                    # Add new
                    if "almanacco" not in self.user_data:
                        self.user_data["almanacco"] = []
                    self.user_data["almanacco"].append(new_cmd)

                if save_user_data(self.user_data):
                    self.save_status_msg = LANG_DICT[lng]["saved_ok"]
                    self.save_status_timer = 90  # ~3 seconds at 30fps
                    self.build_almanacco()
                    # Reset form
                    self.save_name = ""
                    self.save_desc = ""
                    self.save_cmd_text = ""
                    self.save_field = 0
                    if not self.edit_cmd_open:
                        self.save_cmd_open = False
                    else:
                        self.edit_cmd_open = False
                        self.almanacco_open = True
                else:
                    self.save_status_msg = "ERROR: Save failed!"
                    self.save_status_timer = 90
            else:
                self.save_status_msg = "Name and Command required!"
                self.save_status_timer = 90
        elif event.key in [K_B, K_B_ALT]:
            self.save_cmd_open = False
            self.edit_cmd_open = False
            self.save_name = ""
            self.save_desc = ""
            self.save_cmd_text = ""
            self.save_field = 0
        elif event.key == pygame.K_BACKSPACE:
            if self.save_field == 0:
                self.save_name = self.save_name[:-1]
            elif self.save_field == 1:
                self.save_desc = self.save_desc[:-1]
            elif self.save_field == 2:
                self.save_cmd_text = self.save_cmd_text[:-1]
        else:
            # Add character
            char = event.unicode if hasattr(event, 'unicode') else ""
            if char and char.isprintable():
                if self.save_field == 0:
                    self.save_name += char
                elif self.save_field == 1:
                    self.save_desc += char
                elif self.save_field == 2:
                    self.save_cmd_text += char

    def delete_user_command(self):
        """Elimina il comando utente selezionato."""
        lng = self.cfg["language"]
        if self.alm_sel < len(self.full_almanacco):
            item = self.full_almanacco[self.alm_sel]
            if item.get("editable"):
                # Find in user_data and remove
                user_cmds = self.user_data.get("almanacco", [])
                for idx, cmd in enumerate(user_cmds):
                    if cmd.get("name") == item["name"] and cmd.get("cmd") == item["cmd"]:
                        user_cmds.pop(idx)
                        break

                if save_user_data(self.user_data):
                    self.save_status_msg = LANG_DICT[lng]["deleted_ok"]
                    self.save_status_timer = 90
                    self.build_almanacco()
                    # Adjust selection
                    self.alm_sel = max(0, self.alm_sel - 1)
                    while self.alm_sel < len(self.full_almanacco) and self.full_almanacco[self.alm_sel]["type"] == "header":
                        self.alm_sel += 1
                    if self.alm_sel >= len(self.full_almanacco):
                        self.alm_sel = 0

    def open_edit_command(self):
        """Apre il form di modifica per un comando utente esistente."""
        if self.alm_sel < len(self.full_almanacco):
            item = self.full_almanacco[self.alm_sel]
            if item.get("editable"):
                self.save_name = item["name"]
                self.save_desc = item.get("desc", "")
                self.save_cmd_text = item["cmd"]
                self.save_field = 0
                self.edit_cmd_open = True
                self.almanacco_open = False

                # Find index in user_data
                user_cmds = self.user_data.get("almanacco", [])
                for idx, cmd in enumerate(user_cmds):
                    if cmd.get("name") == item["name"] and cmd.get("cmd") == item["cmd"]:
                        self.edit_cmd_index = idx
                        break


def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((W, H), 0, 16)
    pygame.display.set_caption("Rt:Terminal I.D.")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()
    app = AppCore()
    running = True

    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] and (keys[pygame.K_SPACE] or keys[pygame.K_ESCAPE]):
            running = False

        sess = app.sessions[app.current_idx]
        is_osk_visible = app.kbd_visible and not app.y_held
        kbd_y_start = H - 96 if is_osk_visible else H
        line_height = app.cfg["font_size"] + 2
        max_visible = (kbd_y_start - 54 - 16) // line_height

        # Cursor blink
        app.cursor_timer += 1
        if app.cursor_timer >= 15:
            app.cursor_timer = 0
            app.cursor_visible = not app.cursor_visible

        # Status message timer
        if app.save_status_timer > 0:
            app.save_status_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --- Global combos ---
                is_a = (event.key in [K_A, K_A_ALT])
                is_b = (event.key in [K_B, K_B_ALT])
                if (is_a and (keys[K_B] or keys[K_B_ALT])) or (is_b and (keys[K_A] or keys[K_A_ALT])):
                    sess.cmd_buffer += " "
                    continue

                if event.key in [K_Y, K_Y_ALT]:
                    app.y_held = True

                # --- About screen ---
                if app.about_open:
                    if event.key in [K_B, K_B_ALT]:
                        app.about_open = False
                    continue

                # --- Save Command form ---
                if app.save_cmd_open or app.edit_cmd_open:
                    app.handle_save_cmd_input(event, keys)
                    continue

                # --- Almanacco ---
                if app.almanacco_open:
                    if event.key == pygame.K_UP:
                        while True:
                            app.alm_sel = (app.alm_sel - 1) % len(app.full_almanacco)
                            if app.full_almanacco[app.alm_sel]["type"] != "header":
                                break
                    elif event.key == pygame.K_DOWN:
                        while True:
                            app.alm_sel = (app.alm_sel + 1) % len(app.full_almanacco)
                            if app.full_almanacco[app.alm_sel]["type"] != "header":
                                break
                    elif event.key in [K_A, K_A_ALT]:
                        selected_item = app.full_almanacco[app.alm_sel]
                        if selected_item["type"] == "cmd":
                            sess.cmd_buffer = selected_item["cmd"]
                            if sess.execute_command(app.cfg["print_width"], app.font_log) and len(sess.output_history) > max_visible:
                                sess.scroll_offset = len(sess.output_history) - max_visible
                            app.almanacco_open = False
                            app.menu_open = False
                    elif event.key in [K_B, K_B_ALT]:
                        app.almanacco_open = False
                    elif event.key in [K_Y, K_Y_ALT]:
                        # Delete user command
                        app.delete_user_command()
                    elif event.key in [K_X, K_X_ALT]:
                        # Edit user command
                        app.open_edit_command()
                    continue

                # --- Menu ---
                if app.menu_open:
                    active_key = app.menu_keys[app.menu_sel]

                    if event.key == pygame.K_UP:
                        app.menu_sel = (app.menu_sel - 1) % len(app.menu_keys)
                    elif event.key == pygame.K_DOWN:
                        app.menu_sel = (app.menu_sel + 1) % len(app.menu_keys)
                    elif event.key == pygame.K_LEFT:
                        if active_key == "session":
                            app.current_idx = (app.current_idx - 1) % len(app.sessions)
                            gc.collect()
                        elif active_key == "log_size":
                            app.cfg["font_size"] = max(11, app.cfg["font_size"] - 1)
                            app.cache_fonts()
                            app.save_config_to_json()
                        elif active_key == "print_width":
                            app.cfg["print_width"] = max(150, app.cfg["print_width"] - 4)
                            app.save_config_to_json()
                        elif active_key == "theme":
                            c_idx = THEME_KEYS.index(app.cfg["theme"])
                            app.cfg["theme"] = THEME_KEYS[(c_idx - 1) % len(THEME_KEYS)]
                            app.save_config_to_json()
                        elif active_key == "lang":
                            app.cfg["language"] = "EN" if app.cfg["language"] == "IT" else "IT"
                            app.save_config_to_json()
                        elif active_key == "load_font":
                            f_idx = app.available_fonts.index(app.cfg["font_file"])
                            app.cfg["font_file"] = app.available_fonts[(f_idx - 1) % len(app.available_fonts)]
                            app.cache_fonts()
                            app.save_config_to_json()
                    elif event.key == pygame.K_RIGHT:
                        if active_key == "session":
                            app.current_idx = (app.current_idx + 1) % len(app.sessions)
                            gc.collect()
                        elif active_key == "log_size":
                            app.cfg["font_size"] = min(15, app.cfg["font_size"] + 1)
                            app.cache_fonts()
                            app.save_config_to_json()
                        elif active_key == "print_width":
                            app.cfg["print_width"] = min(316, app.cfg["print_width"] + 4)
                            app.save_config_to_json()
                        elif active_key == "theme":
                            c_idx = THEME_KEYS.index(app.cfg["theme"])
                            app.cfg["theme"] = THEME_KEYS[(c_idx + 1) % len(THEME_KEYS)]
                            app.save_config_to_json()
                        elif active_key == "lang":
                            app.cfg["language"] = "EN" if app.cfg["language"] == "IT" else "IT"
                            app.save_config_to_json()
                        elif active_key == "load_font":
                            f_idx = app.available_fonts.index(app.cfg["font_file"])
                            app.cfg["font_file"] = app.available_fonts[(f_idx + 1) % len(app.available_fonts)]
                            app.cache_fonts()
                            app.save_config_to_json()
                    elif event.key in [K_A, K_A_ALT]:
                        if active_key == "new_session":
                            app.sessions.append(TerminalSession(len(app.sessions) + 1, app.cfg["language"]))
                            app.current_idx = len(app.sessions) - 1
                            app.menu_open = False
                        elif active_key == "alm":
                            app.build_almanacco()
                            app.alm_sel = 0
                            while app.alm_sel < len(app.full_almanacco) and app.full_almanacco[app.alm_sel]["type"] == "header":
                                app.alm_sel += 1
                            if app.alm_sel >= len(app.full_almanacco):
                                app.alm_sel = 0
                            app.almanacco_open = True
                        elif active_key == "save_cmd":
                            app.save_cmd_text = sess.cmd_buffer
                            app.save_name = ""
                            app.save_desc = ""
                            app.save_field = 0
                            app.save_cmd_open = True
                        elif active_key == "about":
                            app.about_open = True
                        elif active_key == "close_menu":
                            app.menu_open = False
                    elif event.key in [pygame.K_SPACE, pygame.K_ESCAPE, K_B, K_B_ALT]:
                        app.menu_open = False
                    continue

                # --- Y-held scroll mode ---
                if app.y_held:
                    if event.key == pygame.K_UP:
                        sess.scroll_offset = max(0, sess.scroll_offset - 1)
                    elif event.key == pygame.K_DOWN:
                        if len(sess.output_history) > max_visible:
                            sess.scroll_offset = min(len(sess.output_history) - max_visible, sess.scroll_offset + 1)
                else:
                    # Normal keyboard navigation
                    if event.key == pygame.K_UP:
                        app.kbd_row = (app.kbd_row - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        app.kbd_row = (app.kbd_row + 1) % 4
                    elif event.key == pygame.K_LEFT:
                        app.kbd_col = (app.kbd_col - 1) % 10
                    elif event.key == pygame.K_RIGHT:
                        app.kbd_col = (app.kbd_col + 1) % 10

                # --- Special keys ---
                if event.key in [K_R, K_R_ALT]:
                    app.layout_idx = (app.layout_idx + 1) % 3
                elif event.key in [K_L, K_L_ALT]:
                    valid_cmds = [item for item in app.full_almanacco if item["type"] == "cmd"]
                    if valid_cmds:
                        app.macro_ptr = (app.macro_ptr + 1) % len(valid_cmds)
                        sess.cmd_buffer = valid_cmds[app.macro_ptr]["cmd"]

                elif event.key in [K_A, K_A_ALT]:
                    if is_osk_visible:
                        val = LAYOUTS[app.layout_idx][app.kbd_row][app.kbd_col]
                        if val == "TAB":
                            sess.cmd_buffer += "    "
                        elif val in ["CTRL", "ALT", "ESC", "HOME", "END", "&&", "||"]:
                            sess.cmd_buffer += val
                        elif val == "BKSP":
                            sess.cmd_buffer = sess.cmd_buffer[:-1]
                        elif val == "EXE":
                            if sess.execute_command(app.cfg["print_width"], app.font_log) and len(sess.output_history) > max_visible:
                                sess.scroll_offset = len(sess.output_history) - max_visible
                        elif val in ["ls", "cd..", "clear", "pwd", "ls -la", "top", "df", "env", "pstree"]:
                            sess.cmd_buffer += "ls " if val == "ls" else val
                        else:
                            sess.cmd_buffer += val
                elif event.key in [K_B, K_B_ALT]:
                    sess.cmd_buffer = sess.cmd_buffer[:-1]
                elif event.key == pygame.K_RETURN:
                    if sess.execute_command(app.cfg["print_width"], app.font_log) and len(sess.output_history) > max_visible:
                        sess.scroll_offset = len(sess.output_history) - max_visible
                elif event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                    app.menu_open = True

            elif event.type == pygame.KEYUP:
                if event.key in [K_Y, K_Y_ALT]:
                    app.y_held = False
                    if not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                        app.kbd_visible = not app.kbd_visible

        # --- Drawing ---
        app.draw_main(screen)
        if app.menu_open:
            app.draw_menu(screen)
        if app.almanacco_open:
            app.draw_almanacco(screen)
        if app.about_open:
            app.draw_about(screen)
        if app.save_cmd_open or app.edit_cmd_open:
            app.draw_save_cmd(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # Save config on exit
    app.save_config_to_json()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
