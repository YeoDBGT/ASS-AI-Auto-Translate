#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traducteur de sous-titres ASS utilisant l'API ChatGPT
Interface graphique pour traduire intelligemment les fichiers .ass
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
from pathlib import Path
import openai
from typing import List, Dict
import configparser
import threading
import time


class AssTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 ASS AI Translator")
        self.root.geometry("950x800")
        self.root.minsize(850, 700)
        
        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass

        self.selected_file = None
        self.output_file = None
        self.api_key = tk.StringVar()
        self.source_lang = tk.StringVar(value="Anglais")
        self.target_lang = tk.StringVar(value="Français")
        self.model_choice = tk.StringVar(value="gpt-3.5-turbo")
        self.batch_size_var = tk.IntVar(value=10)
        self.subtitle_lines = []
        self.translated_lines = []

        self.config_file = "translator_config.ini"
        self.load_config()

        self.languages = [
            "Français", "Anglais", "Espagnol", "Italien", "Allemand",
            "Portugais", "Russe", "Japonais", "Chinois", "Coréen",
            "Arabe", "Hindi", "Néerlandais", "Suédois", "Norvégien",
            "Danois", "Finnois", "Polonais", "Tchèque", "Hongrois"
        ]

        self.colors = {
            'bg_primary': '#2f3136',
            'bg_secondary': '#36393f',
            'bg_tertiary': '#40444b',
            'accent': '#5865f2',
            'accent_hover': '#4752c4',
            'text_primary': '#ffffff',
            'text_secondary': '#b9bbbe',
            'success': '#3ba55d',
            'warning': '#faa81a',
            'danger': '#ed4245'
        }

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = 950
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def configure_discord_styles(self, style):
        """Configure les styles Discord modernes"""
        style.configure('Discord.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Discord.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('DiscordTitle.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Discord.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat',
                       font=('Segoe UI', 10))
        
        style.configure('Discord.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       padding=(15, 8))
        
        style.map('Discord.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent_hover'])])
        
        style.configure('DiscordSecondary.TButton',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       relief='flat',
                       padding=(15, 8))
        
        style.configure('Discord.TCheckbutton',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10),
                       focuscolor='none')
        
        style.configure('Discord.TCombobox',
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0,
                       relief='flat',
                       font=('Segoe UI', 10))
        
        style.configure('Discord.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])

    def create_modern_section(self, parent, title):
        """Crée une section moderne avec titre"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(section_frame, text=title, 
                              font=("Segoe UI", 14, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        container = tk.Frame(section_frame, bg=self.colors['bg_secondary'], 
                            relief='flat', bd=0)
        container.pack(fill=tk.X)
        
        inner_frame = tk.Frame(container, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill=tk.X, padx=1, pady=1)
        
        return inner_frame
    
    def create_config_card(self, parent, title, icon, description):
        """Crée une carte pour configuration"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        card_frame.pack(fill=tk.X, padx=20, pady=15)
        
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(15, 10))
        
        icon_title_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        icon_title_frame.pack(anchor=tk.W)
        
        tk.Label(icon_title_frame, text=icon, font=("Segoe UI", 16),
                fg=self.colors['accent'], bg=self.colors['bg_secondary']).pack(side=tk.LEFT)
        
        tk.Label(icon_title_frame, text=title, 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=(8, 0))
        

        if description:
            tk.Label(header_frame, text=description, 
                    font=("Segoe UI", 9),
                    fg=self.colors['text_secondary'], 
                    bg=self.colors['bg_secondary']).pack(anchor=tk.W, pady=(2, 0))
        

        controls_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=0, pady=(5, 15))
        
        return controls_frame

    def load_config(self):
        """Charger la configuration depuis le fichier INI"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            if 'API' in config:
                if 'openai_key' in config['API']:
                    self.api_key.set(config['API']['openai_key'])
            if 'SETTINGS' in config:
                if 'model' in config['SETTINGS']:
                    self.model_choice.set(config['SETTINGS']['model'])
                if 'batch_size' in config['SETTINGS']:
                    batch_val = int(config['SETTINGS']['batch_size'])
                    self.batch_size_var.set(batch_val)

    def save_config(self):
        """Sauvegarder la configuration dans le fichier INI"""
        config = configparser.ConfigParser()
        config['API'] = {'openai_key': self.api_key.get()}
        config['SETTINGS'] = {
            'model': self.model_choice.get(),
            'batch_size': str(self.batch_size_var.get())
        }
        with open(self.config_file, 'w') as f:
            config.write(f)

    def setup_ui(self):
        """Configuration de l'interface utilisateur moderne style Discord"""

        self.root.configure(bg=self.colors['bg_primary'])
        

        style = ttk.Style()
        style.theme_use('clam')


        self.configure_discord_styles(style)


        main_canvas = tk.Canvas(self.root, bg=self.colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview,
                                bg=self.colors['bg_secondary'], 
                                troughcolor=self.colors['bg_primary'],
                                activebackground=self.colors['accent'])
        

        scrollable_frame = tk.Frame(main_canvas, bg=self.colors['bg_primary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)


        main_frame = tk.Frame(scrollable_frame, bg=self.colors['bg_primary'], padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)


        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(header_frame,
                              text="🤖 ASS AI Translator",
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Traduisez intelligemment vos sous-titres avec l'IA",
                                 font=("Segoe UI", 11),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))


        api_section = self.create_modern_section(main_frame, "🔑 Configuration API")
        api_card = self.create_config_card(api_section, "Clé OpenAI", "🤖", 
                                          "Configurez votre clé API pour accéder aux modèles IA")
        

        api_input_frame = tk.Frame(api_card, bg=self.colors['bg_secondary'])
        api_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(api_input_frame, text="Clé API OpenAI", 
                font=("Segoe UI", 10, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        api_entry = ttk.Entry(api_input_frame, textvariable=self.api_key,
                             style="Discord.TEntry", width=50, show="*")
        api_entry.pack(fill=tk.X, pady=(5, 0))
        

        save_api_btn = ttk.Button(api_card, text="💾 Sauvegarder la clé",
                                 style="DiscordSecondary.TButton",
                                  command=self.save_config)
        save_api_btn.pack(anchor=tk.E)


        file_section = self.create_modern_section(main_frame, "📁 Fichier source")
        file_card = self.create_config_card(file_section, "Fichier ASS", "📝",
                                           "Sélectionnez votre fichier de sous-titres à traduire")

        self.file_var = tk.StringVar()
        file_input_frame = tk.Frame(file_card, bg=self.colors['bg_secondary'])
        file_input_frame.pack(fill=tk.X)
        
        file_entry = ttk.Entry(file_input_frame, textvariable=self.file_var,
                              style="Discord.TEntry", width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(file_input_frame, text="📂 Parcourir",
                               style="DiscordSecondary.TButton",
                                command=self.select_file)
        browse_btn.pack(side=tk.RIGHT)


        config_section = self.create_modern_section(main_frame, "⚙️ Configuration de traduction")
        

        config_container = tk.Frame(config_section, bg=self.colors['bg_secondary'])
        config_container.pack(fill=tk.X, padx=20, pady=15)
        

        config_grid = tk.Frame(config_container, bg=self.colors['bg_secondary'])
        config_grid.pack(fill=tk.X)
        

        source_frame = tk.Frame(config_grid, bg=self.colors['bg_secondary'])
        source_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(source_frame, text="🌍 Langue source", 
                font=("Segoe UI", 10, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        source_combo = ttk.Combobox(source_frame, textvariable=self.source_lang,
                                    values=self.languages, state="readonly",
                                   style="Discord.TCombobox", width=20)
        source_combo.pack(anchor=tk.W, pady=(5, 15))
        

        target_frame = tk.Frame(config_grid, bg=self.colors['bg_secondary'])
        target_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(target_frame, text="🎯 Langue cible", 
                font=("Segoe UI", 10, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        target_combo = ttk.Combobox(target_frame, textvariable=self.target_lang,
                                    values=self.languages, state="readonly",
                                   style="Discord.TCombobox", width=20)
        target_combo.pack(anchor=tk.W, pady=(5, 15))
        

        advanced_frame = tk.Frame(config_container, bg=self.colors['bg_secondary'])
        advanced_frame.pack(fill=tk.X, pady=(10, 0))
        

        model_frame = tk.Frame(advanced_frame, bg=self.colors['bg_secondary'])
        model_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(model_frame, text="🧠 Modèle IA", 
                font=("Segoe UI", 10, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_choice,
                                   values=["gpt-3.5-turbo", "gpt-4"],
                                  state="readonly", style="Discord.TCombobox", width=20)
        model_combo.pack(anchor=tk.W, pady=(5, 0))
        

        batch_frame = tk.Frame(advanced_frame, bg=self.colors['bg_secondary'])
        batch_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(batch_frame, text="📦 Lignes par lot", 
                font=("Segoe UI", 10, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        batch_spin = ttk.Spinbox(batch_frame, from_=3, to=20,
                                 textvariable=self.batch_size_var,
                                width=8, state="readonly",
                                font=("Segoe UI", 10))
        batch_spin.pack(anchor=tk.W, pady=(5, 0))
        

        cost_info_frame = tk.Frame(config_container, bg=self.colors['bg_secondary'])
        cost_info_frame.pack(fill=tk.X, pady=(15, 0))
        
        cost_info = tk.Label(cost_info_frame,
                            text="💡 GPT-3.5-turbo est ~10x moins cher que GPT-4",
                            font=("Segoe UI", 9, "italic"),
                            fg=self.colors['warning'],
                            bg=self.colors['bg_secondary'])
        cost_info.pack(anchor=tk.W)


        preview_section = self.create_modern_section(main_frame, "👁️ Aperçu des traductions")
        

        preview_container = tk.Frame(preview_section, bg=self.colors['bg_secondary'])
        preview_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        

        original_column = tk.Frame(preview_container, bg=self.colors['bg_secondary'])
        original_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(original_column, text="📄 Texte original", 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, pady=(15, 5))
        

        orig_text_container = tk.Frame(original_column, bg=self.colors['bg_tertiary'])
        orig_text_container.pack(fill=tk.BOTH, expand=True)
        
        self.original_text = tk.Text(orig_text_container, 
                                    height=15, wrap=tk.WORD,
                                    font=("Consolas", 9),
                                    bg=self.colors['bg_tertiary'],
                                    fg=self.colors['text_primary'],
                                    insertbackground=self.colors['text_primary'],
                                    selectbackground=self.colors['accent'],
                                    relief='flat', bd=0,
                                    padx=15, pady=15)
        
        orig_scroll = tk.Scrollbar(orig_text_container, 
                                  orient=tk.VERTICAL,
                                  command=self.original_text.yview,
                                  bg=self.colors['bg_tertiary'],
                                  troughcolor=self.colors['bg_tertiary'],
                                  activebackground=self.colors['accent'])
        self.original_text.configure(yscrollcommand=orig_scroll.set)

        self.original_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        orig_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        translated_column = tk.Frame(preview_container, bg=self.colors['bg_secondary'])
        translated_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(translated_column, text="🌐 Texte traduit", 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, pady=(15, 5))
        

        trans_text_container = tk.Frame(translated_column, bg=self.colors['bg_tertiary'])
        trans_text_container.pack(fill=tk.BOTH, expand=True)
        
        self.translated_text = tk.Text(trans_text_container, 
                                      height=15, wrap=tk.WORD,
                                      font=("Consolas", 9),
                                      bg=self.colors['bg_tertiary'],
                                      fg=self.colors['text_primary'],
                                      insertbackground=self.colors['text_primary'],
                                      selectbackground=self.colors['accent'],
                                      relief='flat', bd=0,
                                      padx=15, pady=15)
        
        trans_scroll = tk.Scrollbar(trans_text_container, 
                                   orient=tk.VERTICAL,
                                   command=self.translated_text.yview,
                                   bg=self.colors['bg_tertiary'],
                                   troughcolor=self.colors['bg_tertiary'],
                                   activebackground=self.colors['accent'])
        self.translated_text.configure(yscrollcommand=trans_scroll.set)

        self.translated_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        actions_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        actions_section.pack(fill=tk.X, pady=(10, 0))
        

        button_container = tk.Frame(actions_section, bg=self.colors['bg_primary'])
        button_container.pack(anchor=tk.CENTER, pady=(0, 20))
        

        translate_btn = ttk.Button(button_container, 
                                  text="🚀 Traduire avec IA",
                                  style="Discord.TButton",
                                   command=self.start_translation)
        translate_btn.pack(side=tk.LEFT, padx=(0, 15))
        

        analyze_btn = ttk.Button(button_container, 
                                text="📖 Analyser le fichier",
                                style="DiscordSecondary.TButton",
                                command=self.analyze_file)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = ttk.Button(button_container, 
                             text="💾 Sauvegarder",
                             style="DiscordSecondary.TButton",
                              command=self.save_translation)
        save_btn.pack(side=tk.LEFT)


        progress_container = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_container, 
                                       mode='determinate',
                                       style='Discord.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, padx=20)


        status_container = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        status_container.pack(fill=tk.X)
        
        self.progress_label = tk.Label(status_container, 
                                      text="🟢 Prêt à traduire vos sous-titres",
                                      font=("Segoe UI", 10),
                                      fg=self.colors['success'],
                                      bg=self.colors['bg_primary'])
        self.progress_label.pack(pady=(0, 10))


        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def _unbind_mousewheel(event):
            main_canvas.unbind_all("<MouseWheel>")
            
        main_canvas.bind('<Enter>', _bind_mousewheel)
        main_canvas.bind('<Leave>', _unbind_mousewheel)
        

        self.root.after(100, self.center_window)

    def select_file(self):
        """Sélectionner un fichier ASS"""
        filetypes = [
            ("Fichiers ASS", "*.ass"),
            ("Fichiers SSA", "*.ssa"),
            ("Tous les fichiers", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier de sous-titres",
            filetypes=filetypes
        )

        if filename:
            self.selected_file = filename
            self.file_var.set(filename)

            path = Path(filename)
            target_lang = self.target_lang.get().lower()
            output_name = f"{path.stem}_{target_lang}{path.suffix}"
            self.output_file = path.parent / output_name

    def parse_ass_file(self, filename: str) -> List[Dict]:
        """Parser un fichier ASS et extraire les dialogues"""
        dialogues = []

        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(filename, 'r', encoding='latin-1') as f:
                content = f.read()

        lines = content.split('\n')
        in_events_section = False
        format_line = None

        for line in lines:
            line = line.strip()

            if line == '[Events]':
                in_events_section = True
                continue

            if line.startswith('[') and line != '[Events]':
                in_events_section = False
                continue

            if in_events_section:
                if line.startswith('Format:'):
                    format_line = line[7:].strip()
                    continue

                if line.startswith('Dialogue:') and format_line:

                    dialogue_data = line[9:].strip()
                    fields = [f.strip() for f in format_line.split(',')]
                    values = dialogue_data.split(',', len(fields) - 1)

                    if len(values) >= len(fields):
                        dialogue_dict = dict(zip(fields, values))
                        if 'Text' in dialogue_dict:

                            text = self.clean_ass_text(dialogue_dict['Text'])
                            if text.strip():
                                dialogues.append({
                                    'original_line': line,
                                    'text': text,
                                    'start': dialogue_dict.get('Start', ''),
                                    'end': dialogue_dict.get('End', ''),
                                    'style': dialogue_dict.get('Style', ''),
                                    'dialogue_dict': dialogue_dict
                                })

        return dialogues

    def clean_ass_text(self, text: str) -> str:
        """Nettoyer le texte ASS des balises de formatage"""

        text = re.sub(r'\{[^}]*\}', '', text)

        text = text.replace('\\N', ' ')

        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def analyze_file(self):
        """Analyser le fichier sélectionné"""
        if not self.selected_file:
            messagebox.showwarning("Attention",
                                   "Veuillez sélectionner un fichier ASS")
            return

        try:
            self.subtitle_lines = self.parse_ass_file(self.selected_file)

            if not self.subtitle_lines:
                messagebox.showinfo("Information",
                                    "Aucun dialogue trouvé dans ce fichier")
                return


            preview_lines = []
            for i, line in enumerate(self.subtitle_lines):
                text = line['text']
                if len(text) > 120:
                    text = text[:120] + '...'
                preview_lines.append(f"[{i+1:03d}] {text}")

            preview_text = "\n".join(preview_lines)


            total_chars = sum(len(line['text']) 
                             for line in self.subtitle_lines)
            estimated_tokens = total_chars // 3
            if self.model_choice.get() == "gpt-4":
                cost_estimate = estimated_tokens * 0.00003
            else:
                cost_estimate = estimated_tokens * 0.000002

            preview_text += (f"\n\n📊 Total: {len(self.subtitle_lines)} lignes "
                             f"({estimated_tokens} tokens estimés)\n"
                             f"💰 Coût estimé: ${cost_estimate:.4f} "
                             f"avec {self.model_choice.get()}")

            self.original_text.delete(1.0, tk.END)
            self.original_text.insert(1.0, preview_text)

            count = len(self.subtitle_lines)
            self.progress_label.config(
                text=f"Analysé: {count} lignes de dialogue")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {e}")

    def get_translation_prompt(self, source_lang: str,
                               target_lang: str) -> str:
        """Créer le prompt professionnel pour ChatGPT"""
        return f"""Traduis du {source_lang} vers le {target_lang}.

RÈGLES:
- Garde l'anglais approprié (noms, marques, expressions)
- Style naturel, pas robotique
- Adapte le registre au contexte
- Conserve le ton émotionnel

Réponds seulement les traductions numérotées."""

    def translate_batch(self, texts: List[str]) -> List[str]:
        """Traduire un lot de textes via ChatGPT"""
        if not self.api_key.get():
            raise ValueError("Clé API OpenAI manquante")

        client = openai.OpenAI(api_key=self.api_key.get())
        translations = []
        batch_size = self.batch_size_var.get()


        filtered_texts = []
        text_indices = []
        for i, text in enumerate(texts):
            if text.strip() and len(text.strip()) > 2:
                filtered_texts.append(text)
                text_indices.append(i)


        for i in range(0, len(filtered_texts), batch_size):
            batch = filtered_texts[i:i + batch_size]


            numbered_texts = "\n".join([f"{j+1}. {text}"
                                        for j, text in enumerate(batch)])

            prompt = self.get_translation_prompt(self.source_lang.get(),
                                                 self.target_lang.get())

            try:
                response = client.chat.completions.create(
                    model=self.model_choice.get(),
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": numbered_texts}
                    ],
                    temperature=0.1,
                    max_tokens=min(len(numbered_texts) * 2, 1500)
                )


                result = response.choices[0].message.content.strip()


                batch_translations = []
                for line in result.split('\n'):
                    if re.match(r'^\d+\.', line):

                        translation = re.sub(r'^\d+\.\s*', '', line).strip()
                        batch_translations.append(translation)


                if len(batch_translations) != len(batch):

                    lines = [line.strip() for line in result.split('\n')
                             if line.strip()]
                    batch_translations = lines[:len(batch)]
                    if len(batch_translations) < len(batch):
                        missing_count = len(batch) - len(batch_translations)
                        batch_translations.extend(batch[-missing_count:])

                translations.extend(batch_translations)


                is_gpt35 = self.model_choice.get() == "gpt-3.5-turbo"
                delay = 0.5 if is_gpt35 else 1
                time.sleep(delay)

            except Exception as e:

                translations.extend(batch)
                print(f"Erreur de traduction pour le lot "
                      f"{i//batch_size + 1}: {e}")


        final_translations = texts.copy()
        for i, filtered_index in enumerate(text_indices):
            if i < len(translations):
                final_translations[filtered_index] = translations[i]

        return final_translations

    def start_translation(self):
        """Démarrer la traduction en arrière-plan"""
        if not self.subtitle_lines:
            messagebox.showwarning("Attention",
                                   "Veuillez d'abord analyser un fichier")
            return

        if not self.api_key.get():
            messagebox.showwarning("Attention",
                                   "Veuillez configurer votre clé API OpenAI")
            return


        thread = threading.Thread(target=self.translate_file)
        thread.daemon = True
        thread.start()

    def translate_file(self):
        """Traduire le fichier complet"""
        try:

            self.progress.config(maximum=len(self.subtitle_lines))
            self.progress_label.config(text="Traduction en cours...")


            texts_to_translate = [line['text'] for line in self.subtitle_lines]


            self.progress_label.config(text="Traduction en cours...")
            all_translations = self.translate_batch(texts_to_translate)


            total = len(texts_to_translate)
            self.progress['value'] = total
            self.progress_label.config(text=f"Traduit {total}/{total} lignes")

            self.translated_lines = all_translations


            preview_lines = []
            for i, translation in enumerate(all_translations):
                text = translation
                if len(text) > 120:
                    text = text[:120] + '...'
                preview_lines.append(f"[{i+1:03d}] {text}")

            preview_text = "\n".join(preview_lines)


            preview_text += (f"\n\n✅ Traduction terminée: "
                             f"{len(all_translations)} lignes traduites")

            self.translated_text.delete(1.0, tk.END)
            self.translated_text.insert(1.0, preview_text)

            self.progress['value'] = len(texts_to_translate)
            self.progress_label.config(text="Traduction terminée !")

            messagebox.showinfo("Terminé", "Traduction terminée avec succès !")

        except Exception as e:
            messagebox.showerror("Erreur",
                                 f"Erreur lors de la traduction: {e}")
            self.progress_label.config(text="Erreur de traduction")

    def save_translation(self):
        """Sauvegarder le fichier traduit"""
        if not self.translated_lines:
            messagebox.showwarning("Attention",
                                   "Aucune traduction à sauvegarder")
            return


        filetypes = [("Fichiers ASS", "*.ass"), ("Tous les fichiers", "*.*")]
        initial_name = (self.output_file.name if self.output_file
                        else "traduit.ass")

        output_file = filedialog.asksaveasfilename(
            title="Sauvegarder la traduction",
            defaultextension=".ass",
            filetypes=filetypes,
            initialfile=initial_name
        )

        if not output_file:
            return

        try:

            with open(self.selected_file, 'r', encoding='utf-8-sig') as f:
                original_content = f.read()


            lines = original_content.split('\n')
            translation_index = 0

            for i, line in enumerate(lines):
                if (line.strip().startswith('Dialogue:') and
                        translation_index < len(self.translated_lines)):

                    dialogue_data = self.subtitle_lines[translation_index]
                    new_dialogue = dialogue_data['dialogue_dict'].copy()
                    new_dialogue['Text'] = self.translated_lines[
                        translation_index]


                    dialogue_parts = [
                        new_dialogue.get(field, '') for field in
                        dialogue_data['dialogue_dict'].keys()
                    ]
                    lines[i] = f"Dialogue: {','.join(dialogue_parts)}"
                    translation_index += 1


            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(lines))

            messagebox.showinfo("Succès", f"Fichier sauvegardé: {output_file}")

        except Exception as e:
            messagebox.showerror("Erreur",
                                 f"Erreur lors de la sauvegarde: {e}")

    def run(self):
        """Lancer l'application"""
        self.setup_ui()
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = AssTranslator()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrompue par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        messagebox.showerror("Erreur", f"Erreur inattendue: {e}")


if __name__ == "__main__":
    main()
