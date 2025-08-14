#!/usr/bin/env python3
"""
Inserteur de sous-titres ASS dans fichiers MKV
Interface graphique pour insérer facilement des sous-titres dans des vidéos
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
from pathlib import Path
import threading


class SubtitleInserter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 ASS MKV Inserter")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        

        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass

        self.mkv_file = None
        self.ass_file = None
        self.output_file = None
        self.existing_tracks = []

        self.subtitle_language = tk.StringVar(value="fra")
        self.subtitle_title = tk.StringVar(value="Français")
        self.subtitle_default = tk.BooleanVar(value=True)
        self.subtitle_forced = tk.BooleanVar(value=False)

        self.languages = {
            "Français": "fra",
            "Anglais": "eng",
            "Espagnol": "spa",
            "Italien": "ita",
            "Allemand": "ger",
            "Portugais": "por",
            "Russe": "rus",
            "Japonais": "jpn",
            "Chinois": "chi",
            "Coréen": "kor",
            "Arabe": "ara"
        }

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = 900
        height = 750
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
    
    def create_file_card(self, parent, title, icon, description):
        """Crée une carte pour sélection de fichier"""
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        card_frame.pack(fill=tk.X, padx=20, pady=10)
        
        header_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(15, 5))
        
        icon_title_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        icon_title_frame.pack(anchor=tk.W)
        
        tk.Label(icon_title_frame, text=icon, font=("Segoe UI", 16),
                fg=self.colors['accent'], bg=self.colors['bg_secondary']).pack(side=tk.LEFT)
        
        tk.Label(icon_title_frame, text=title, 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(side=tk.LEFT, padx=(8, 0))
        
        tk.Label(header_frame, text=description, 
                font=("Segoe UI", 9),
                fg=self.colors['text_secondary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, pady=(2, 0))
        
        controls_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=0, pady=(5, 15))
        
        return controls_frame

    def setup_ui(self):
        """Configuration de l'interface utilisateur moderne style Discord"""
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
                              text="🎬 ASS MKV Inserter",
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Insérez facilement vos sous-titres dans des fichiers MKV",
                                 font=("Segoe UI", 11),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))


        files_section = self.create_modern_section(main_frame, "📁 Fichiers source")
        

        mkv_card = self.create_file_card(files_section, "Fichier vidéo MKV", 
                                        "🎬", "Sélectionnez votre fichier vidéo")
        self.mkv_var = tk.StringVar()
        mkv_entry = ttk.Entry(mkv_card, textvariable=self.mkv_var, 
                             style="Discord.TEntry", width=50)
        mkv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        mkv_btn = ttk.Button(mkv_card, text="📂 Parcourir", 
                            style="DiscordSecondary.TButton",
                             command=self.select_mkv_file)
        mkv_btn.pack(side=tk.RIGHT)


        ass_card = self.create_file_card(files_section, "Fichier sous-titres ASS", 
                                        "📝", "Sélectionnez vos sous-titres")
        self.ass_var = tk.StringVar()
        ass_entry = ttk.Entry(ass_card, textvariable=self.ass_var, 
                             style="Discord.TEntry", width=50)
        ass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ass_btn = ttk.Button(ass_card, text="📂 Parcourir", 
                            style="DiscordSecondary.TButton",
                             command=self.select_ass_file)
        ass_btn.pack(side=tk.RIGHT)


        config_section = self.create_modern_section(main_frame, "⚙️ Configuration")
        

        config_grid = tk.Frame(config_section, bg=self.colors['bg_secondary'])
        config_grid.pack(fill=tk.X, padx=20, pady=15)


        lang_frame = tk.Frame(config_grid, bg=self.colors['bg_secondary'])
        lang_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(lang_frame, text="🌍 Langue", 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        lang_combo = ttk.Combobox(lang_frame, values=list(self.languages.keys()),
                                 state="readonly", style="Discord.TCombobox", width=25)
        lang_combo.set("Français")
        lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        lang_combo.pack(anchor=tk.W, pady=(5, 0))
        self.lang_combo = lang_combo


        title_frame = tk.Frame(config_grid, bg=self.colors['bg_secondary'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(title_frame, text="🏷️ Titre", 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        title_entry = ttk.Entry(title_frame, textvariable=self.subtitle_title,
                               style="Discord.TEntry", width=30)
        title_entry.pack(anchor=tk.W, pady=(5, 0))
        

        options_frame = tk.Frame(config_grid, bg=self.colors['bg_secondary'])
        options_frame.pack(fill=tk.X)
        
        tk.Label(options_frame, text="🎯 Options", 
                font=("Segoe UI", 11, "bold"),
                fg=self.colors['text_primary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W)
        
        check_frame = tk.Frame(options_frame, bg=self.colors['bg_secondary'])
        check_frame.pack(anchor=tk.W, pady=(5, 0))
        
        default_check = ttk.Checkbutton(check_frame, text="Piste par défaut",
                                       variable=self.subtitle_default,
                                       style="Discord.TCheckbutton")
        default_check.pack(side=tk.LEFT, padx=(0, 20))

        forced_check = ttk.Checkbutton(check_frame, text="Sous-titres forcés",
                                      variable=self.subtitle_forced,
                                      style="Discord.TCheckbutton")
        forced_check.pack(side=tk.LEFT)


        tracks_section = self.create_modern_section(main_frame, "📊 Aperçu des pistes")
        

        text_container = tk.Frame(tracks_section, bg=self.colors['bg_tertiary'])
        text_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        

        self.tracks_text = tk.Text(text_container, 
                                  height=8, 
                                  wrap=tk.WORD,
                                  font=("Consolas", 9),
                                  bg=self.colors['bg_tertiary'],
                                  fg=self.colors['text_primary'],
                                  insertbackground=self.colors['text_primary'],
                                  selectbackground=self.colors['accent'],
                                  relief='flat',
                                  bd=0,
                                  padx=15,
                                  pady=15)
        
        tracks_scroll = tk.Scrollbar(text_container, 
                                   orient=tk.VERTICAL,
                                   command=self.tracks_text.yview,
                                   bg=self.colors['bg_tertiary'],
                                   troughcolor=self.colors['bg_tertiary'],
                                   activebackground=self.colors['accent'])
        self.tracks_text.configure(yscrollcommand=tracks_scroll.set)

        self.tracks_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tracks_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        actions_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        actions_section.pack(fill=tk.X, pady=(10, 0))
        

        button_container = tk.Frame(actions_section, bg=self.colors['bg_primary'])
        button_container.pack(anchor=tk.CENTER, pady=(0, 20))
        

        insert_btn = ttk.Button(button_container, 
                               text="🚀 Insérer les sous-titres",
                               style="Discord.TButton",
                                command=self.start_insertion)
        insert_btn.pack(side=tk.LEFT, padx=(0, 15))
        

        analyze_btn = ttk.Button(button_container, 
                                text="📊 Analyser MKV",
                                style="DiscordSecondary.TButton",
                                command=self.analyze_mkv)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        debug_btn = ttk.Button(button_container, 
                              text="🔍 Diagnostiquer",
                              style="DiscordSecondary.TButton",
                               command=self.diagnose_file)
        debug_btn.pack(side=tk.LEFT)


        progress_container = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_container, 
                                       mode='indeterminate',
                                       style='Discord.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, padx=20)


        status_container = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        status_container.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_container, 
                                    text="🟢 Prêt à insérer vos sous-titres",
                                    font=("Segoe UI", 10),
                                    fg=self.colors['success'],
                                    bg=self.colors['bg_primary'])
        self.status_label.pack(pady=(0, 10))


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

    def on_language_change(self, event=None):
        """Callback quand la langue change"""
        selected_lang = self.lang_combo.get()
        if selected_lang in self.languages:
            self.subtitle_language.set(self.languages[selected_lang])
            self.subtitle_title.set(selected_lang)

    def select_mkv_file(self):
        """Sélectionner le fichier MKV source"""
        filetypes = [
            ("Fichiers MKV", "*.mkv"),
            ("Tous les fichiers", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier MKV",
            filetypes=filetypes
        )

        if filename:
            self.mkv_file = filename
            self.mkv_var.set(filename)

            path = Path(filename)
            output_name = f"{path.stem}_with_subs{path.suffix}"
            self.output_file = path.parent / output_name
            self.status_label.config(text=f"MKV sélectionné: {path.name}")

    def select_ass_file(self):
        """Sélectionner le fichier ASS à insérer"""
        filetypes = [
            ("Fichiers ASS", "*.ass"),
            ("Fichiers SSA", "*.ssa"),
            ("Fichiers SRT", "*.srt"),
            ("Tous les fichiers", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier de sous-titres",
            filetypes=filetypes
        )

        if filename:
            self.ass_file = filename
            self.ass_var.set(filename)
            path = Path(filename)
            self.status_label.config(
                text=f"Sous-titres sélectionnés: {path.name}")

    def check_ffmpeg(self):
        """Vérifier que FFmpeg est disponible"""
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                    capture_output=True, check=True, text=True)

            version_line = (result.stdout.split('\n')[0] 
                            if result.stdout else "")
            print(f"✅ FFmpeg détecté: {version_line}")
            return True
        except FileNotFoundError:
            messagebox.showerror(
                "FFmpeg introuvable",
                "❌ FFmpeg n'est pas installé ou n'est pas dans le PATH.\n\n"
                "📥 INSTALLATION:\n"
                "• Windows: Téléchargez depuis "
                "https://ffmpeg.org/download.html\n"
                "• Ou utilisez: winget install FFmpeg\n"
                "• Ou avec Chocolatey: choco install ffmpeg\n\n"
                "🔧 Assurez-vous que ffmpeg.exe est dans votre PATH."
            )
            return False
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Erreur FFmpeg",
                f"❌ Erreur lors de la vérification FFmpeg:\n\n"
                f"Code d'erreur: {e.returncode}\n"
                f"Détails: {e.stderr if e.stderr else 'Erreur inconnue'}\n\n"
                f"💡 Essayez de réinstaller FFmpeg."
            )
            return False

    def analyze_mkv(self):
        """Analyser le fichier MKV pour voir les pistes existantes"""
        if not self.mkv_file:
            messagebox.showwarning("Attention",
                                   "Veuillez sélectionner un fichier MKV")
            return

        if not self.check_ffmpeg():
            return

        self.progress.start()
        self.status_label.config(text="Analyse en cours...")

        try:

            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                self.mkv_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            data = json.loads(result.stdout)


            video_tracks = []
            audio_tracks = []
            subtitle_tracks = []

            for i, stream in enumerate(data.get("streams", [])):
                codec_type = stream.get("codec_type")
                codec_name = stream.get("codec_name", "inconnu")
                language = stream.get("tags", {}).get("language", "und")
                title = stream.get("tags", {}).get("title", "")

                track_info = {
                    "index": i,
                    "codec": codec_name,
                    "language": language,
                    "title": title
                }

                if codec_type == "video":
                    width = stream.get('width', '?')
                    height = stream.get('height', '?')
                    resolution = f"{width}x{height}"
                    fps = stream.get("r_frame_rate", "?")
                    track_info["resolution"] = resolution
                    track_info["fps"] = fps
                    video_tracks.append(track_info)
                elif codec_type == "audio":
                    channels = stream.get("channels", "?")
                    sample_rate = stream.get("sample_rate", "?")
                    track_info["channels"] = channels
                    track_info["sample_rate"] = sample_rate
                    audio_tracks.append(track_info)
                elif codec_type == "subtitle":
                    subtitle_tracks.append(track_info)


            self.display_tracks_info(video_tracks, audio_tracks,
                                     subtitle_tracks)
            self.existing_tracks = data.get("streams", [])

            self.status_label.config(text="Analyse terminée")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {e}")
            self.status_label.config(text="Erreur d'analyse")
        except json.JSONDecodeError:
            messagebox.showerror("Erreur",
                                 "Erreur lors de l'analyse des données")
        finally:
            self.progress.stop()

    def display_tracks_info(self, video_tracks, audio_tracks,
                            subtitle_tracks):
        """Afficher les informations des pistes dans l'interface"""
        self.tracks_text.delete(1.0, tk.END)

        info_text = "📹 PISTES VIDÉO:\n"
        for track in video_tracks:
            info_text += (f"  [{track['index']}] {track['codec']} - "
                          f"{track['resolution']} @ {track['fps']} fps\n")

        info_text += "\n🔊 PISTES AUDIO:\n"
        for track in audio_tracks:
            info_text += (f"  [{track['index']}] {track['codec']} - "
                          f"{track['language']} - {track['channels']} ch")
            if track['title']:
                info_text += f" - {track['title']}"
            info_text += "\n"

        info_text += "\n📝 PISTES SOUS-TITRES:\n"
        if subtitle_tracks:
            for track in subtitle_tracks:
                info_text += (f"  [{track['index']}] {track['codec']} - "
                              f"{track['language']}")
                if track['title']:
                    info_text += f" - {track['title']}"
                info_text += "\n"
        else:
            info_text += "  Aucune piste de sous-titres trouvée\n"

        info_text += "\n📊 RÉSUMÉ:\n"
        info_text += f"  • {len(video_tracks)} piste(s) vidéo\n"
        info_text += f"  • {len(audio_tracks)} piste(s) audio\n"
        info_text += f"  • {len(subtitle_tracks)} piste(s) sous-titres\n"

        self.tracks_text.insert(1.0, info_text)

    def start_insertion(self):
        """Démarrer l'insertion en arrière-plan"""
        if not self.mkv_file:
            messagebox.showwarning("Attention",
                                   "Veuillez sélectionner un fichier MKV")
            return

        if not self.ass_file:
            messagebox.showwarning("Attention",
                                   "Veuillez sélectionner un fichier ASS")
            return


        if not Path(self.mkv_file).exists():
            messagebox.showerror("Erreur", 
                                 f"❌ Fichier MKV introuvable:\n{self.mkv_file}")
            return
            
        if not Path(self.ass_file).exists():
            messagebox.showerror("Erreur", 
                                 f"❌ Fichier sous-titres introuvable:\n"
                                 f"{self.ass_file}")
            return

        if not self.check_ffmpeg():
            return


        if not self.existing_tracks:
            result = messagebox.askyesno(
                "Analyse recommandée",
                "⚠️ Vous n'avez pas analysé le fichier MKV.\n\n"
                "Il est recommandé d'analyser d'abord le fichier pour "
                "voir les pistes existantes.\n\n"
                "Voulez-vous continuer sans analyser ?"
            )
            if not result:
                return


        initial_name = (self.output_file.name if self.output_file
                        else "video_with_subs.mkv")

        output_file = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier MKV avec sous-titres",
            defaultextension=".mkv",
            filetypes=[("Fichiers MKV", "*.mkv"),
                       ("Tous les fichiers", "*.*")],
            initialfile=initial_name
        )

        if not output_file:
            return


        self.output_file = Path(output_file)
        thread = threading.Thread(target=self.insert_subtitles,
                                  args=(output_file,))
        thread.daemon = True
        thread.start()

    def insert_subtitles(self, output_file):
        """Insérer les sous-titres dans le fichier MKV"""
        try:
            self.progress.start()
            self.status_label.config(text="Insertion des sous-titres...")


            existing_subtitle_count = sum(
                1 for track in self.existing_tracks
                if track.get("codec_type") == "subtitle"
            )
            print(f"📊 Pistes ST existantes à supprimer: {existing_subtitle_count}")


            subtitle_path = Path(self.ass_file)
            subtitle_ext = subtitle_path.suffix.lower()
            if subtitle_ext == '.ass':
                subtitle_codec = 'ass'
            elif subtitle_ext == '.ssa':
                subtitle_codec = 'ssa'
            elif subtitle_ext == '.srt':
                subtitle_codec = 'subrip'
            else:
                subtitle_codec = 'ass'


            selected_language = self.subtitle_language.get()
            
            print(f"🎬 Type de sous-titres détecté: {subtitle_ext} -> "
                  f"codec: {subtitle_codec}")
            print(f"🌍 Langue configurée: {selected_language}")



            cmd = [
                "ffmpeg",
                "-i", self.mkv_file,         
                "-i", self.ass_file,         

                "-map", "0:v",               
                "-map", "0:a",                 
                "-map", "1:0",               
                "-c", "copy",                
                "-c:s:0", subtitle_codec,    
                "-y",                        
                output_file
            ]

            print("🗑️ SUPPRESSION de toutes les anciennes pistes de sous-titres")
            print(f"✨ Conservation seulement de la nouvelle piste: "
                  f"{selected_language}")




            subtitle_title = self.subtitle_title.get().strip()
            if not subtitle_title:
                subtitle_title = "Français"
            
            print(f"🏷️ Préparation: langue={selected_language}, "
                  f"titre={subtitle_title}")
            

            print("🎯 Version finale: SEULEMENT métadonnée titre")
            
            cmd = [
                "ffmpeg",
                "-i", self.mkv_file,         
                "-i", self.ass_file,         
                
                "-map", "0:v",               
                "-map", "0:a",                
                "-map", "1:0",               
                
                "-c", "copy",                
                "-c:s:0", subtitle_codec,    # Codec pour piste ST
                
                "-metadata:s:s:0", f"title={subtitle_title}",
                
                "-y", output_file
            ]
            
            print(f"📋 Métadonnée appliquée: titre='{subtitle_title}'")
            print("⚠️ Pas de langue ni disposition pour éviter 'invalid argument'")


            cmd_str = " ".join([f'"{item}"' if ' ' in item else item 
                                for item in cmd])
            print("\n🔧 Commande FFmpeg générée:")
            print(f"{cmd_str}\n")


            self.status_label.config(text="Multiplexage en cours...")

            result = subprocess.run(cmd, capture_output=True, text=True)


            if result.stdout:
                print(f"📝 Sortie FFmpeg:\n{result.stdout}")
            if result.stderr:
                print("⚠️ Erreurs/Avertissements FFmpeg:\n"
                      f"{result.stderr}")

            if result.returncode == 0:
                print("✅ FFmpeg terminé avec succès")
                
                self.verify_insertion(output_file)
            else:
                error_msg = result.stderr or "Erreur inconnue"
                self.status_label.config(text="❌ Erreur d'insertion")
                print(f"❌ FFmpeg a échoué avec le code: "
                      f"{result.returncode}")
                messagebox.showerror(
                    "Erreur",
                                     f"Erreur lors de l'insertion:\n"
                    f"Code de retour: {result.returncode}\n\n"
                    f"Détails:\n{error_msg}\n\n"
                    f"Commande exécutée:\n{cmd_str}"
                )

        except Exception as e:
            self.status_label.config(text="❌ Erreur")
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
        finally:
            self.progress.stop()

    def verify_insertion(self, output_file):
        """Vérifier que les sous-titres ont bien été insérés"""
        try:
            self.status_label.config(text="Vérification...")
            
            
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            
            subtitle_count = sum(
                1 for stream in data.get("streams", [])
                if stream.get("codec_type") == "subtitle"
            )
            
            original_subtitle_count = sum(
                1 for track in self.existing_tracks
                if track.get("codec_type") == "subtitle"
            )
            
             : on s'attend à exactement 1 piste de sous-titres
            expected_subtitle_count = 1
            
            if subtitle_count == expected_subtitle_count:
                self.status_label.config(text="✅ Insertion vérifiée !")
                
                 (devrait être unique)
                subtitle_stream = None
                for stream in data.get("streams", []):
                    if stream.get("codec_type") == "subtitle":
                        subtitle_stream = stream
                        break
                
                if subtitle_stream:
                    index = subtitle_stream.get("index", "?")
                    codec = subtitle_stream.get("codec_name", "?")
                    tags = subtitle_stream.get("tags", {})
                    language = tags.get("language", "und")
                    title = tags.get("title", "Sans titre")
                    
                    
                    disposition = subtitle_stream.get("disposition", {})
                    is_default = disposition.get("default", 0) == 1
                    is_forced = disposition.get("forced", 0) == 1
                    
                    new_subtitle = {
                        "position": 0,  
                        "index": index,
                        "codec": codec,
                        "language": language,
                        "title": title,
                        "default": is_default,
                        "forced": is_forced
                    }
                else:
                    new_subtitle = None
                
                success_msg = (
                    f"✅ Sous-titres insérés avec succès !\n\n"
                    f"📁 Fichier créé: {Path(output_file).name}\n"
                    f"🗑️ Suppression: {original_subtitle_count} anciennes piste(s)\n"
                    f"✨ Conservation: 1 nouvelle piste uniquement\n\n"
                )
                

                if new_subtitle:
                    success_msg += "🎯 PISTE DE SOUS-TITRES UNIQUE:\n"
                    success_msg += f"   • Index: {new_subtitle['index']}\n"
                    success_msg += f"   • Codec: {new_subtitle['codec']}\n"
                    success_msg += f"   • Langue: {new_subtitle['language']}\n"
                    success_msg += f"   • Titre: {new_subtitle['title']}\n"
                    success_msg += f"   • Par défaut: {'✅' if new_subtitle['default'] else '❌'}\n"
                    success_msg += f"   • Forcé: {'✅' if new_subtitle['forced'] else '❌'}\n\n"
                    

                    expected_lang = self.subtitle_language.get()
                    expected_title = self.subtitle_title.get().strip() or "Français"
                    

                    if new_subtitle['language'] == expected_lang:
                        success_msg += f"✅ Langue correctement définie: {expected_lang}\n"
                    else:
                        success_msg += f"❌ PROBLÈME LANGUE: attendue '{expected_lang}', détectée '{new_subtitle['language']}'\n"
                    
  
                    if new_subtitle['title'] == expected_title:
                        success_msg += f"✅ Titre correctement défini: {expected_title}\n"
                    else:
                        success_msg += f"❌ PROBLÈME TITRE: attendu '{expected_title}', détecté '{new_subtitle['title']}'\n"
                    

                    if new_subtitle['default']:
                        success_msg += "✅ Piste définie par défaut\n"
                    else:
                        success_msg += "⚠️ Piste non définie par défaut\n"
                
                success_msg += (
                    "\n\n💡 CONSEIL:\n"
                    "Si les sous-titres ne s'affichent pas:\n"
                    "• Activez-les manuellement dans votre lecteur\n"
                    "• Vérifiez les paramètres de sous-titres\n"
                    "• Testez avec VLC Media Player"
                )
                
                messagebox.showinfo("Succès", success_msg)
            else:
                self.status_label.config(text="⚠️ Insertion douteuse")
                messagebox.showwarning(
                    "Attention",
                    f"L'insertion semble avoir échoué.\n\n"
                    f"Pistes de sous-titres détectées: {subtitle_count}\n"
                    f"Attendu: {expected_subtitle_count} (piste unique)\n\n"
                    f"RAPPEL: Avec la nouvelle méthode, toutes les anciennes "
                    f"pistes de sous-titres sont supprimées.\n"
                    f"Le fichier ne devrait contenir qu'UNE seule piste."
                )
                
        except Exception as e:
            self.status_label.config(text="✅ Insertion terminée (non vérifiée)")
            messagebox.showinfo(
                "Terminé",
                f"Insertion terminée !\n\n"
                f"📁 Fichier créé: {Path(output_file).name}\n"
                f"🌍 Langue: {self.lang_combo.get()}\n"
                f"🏷️ Titre: {self.subtitle_title.get()}\n"
                f"🗑️ Suppression: Toutes anciennes pistes ST\n"
                f"✨ Conservation: 1 piste unique\n\n"
                f"⚠️ Impossible de vérifier l'insertion: {e}\n\n"
                f"💡 Testez le fichier dans votre lecteur vidéo.\n"
                f"La nouvelle piste devrait être la seule disponible."
            )

    def diagnose_file(self):
        """Diagnostiquer un fichier MKV pour comprendre les 
        problèmes de sous-titres"""

        filetypes = [
            ("Fichiers MKV", "*.mkv"),
            ("Tous les fichiers", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Sélectionner le fichier MKV à diagnostiquer",
            filetypes=filetypes
        )
        
        if not filename:
            return
            
        if not self.check_ffmpeg():
            return
            
        self.progress.start()
        self.status_label.config(text="Diagnostic en cours...")
        
        try:

            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                filename
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            

            streams = data.get("streams", [])
            subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]
            

            report = f"🔍 DIAGNOSTIC COMPLET - {Path(filename).name}\n"
            report += "=" * 60 + "\n\n"
            

            format_info = data.get("format", {})
            duration = format_info.get("duration", "Inconnue")
            size = format_info.get("size", "Inconnue")
            
            if duration != "Inconnue":
                duration = f"{float(duration)/3600:.1f}h"
            if size != "Inconnue":
                size = f"{int(size)/(1024**3):.1f} GB"
                
            report += "📊 FICHIER:\n"
            report += f"  • Durée: {duration}\n"
            report += f"  • Taille: {size}\n"
            report += f"  • Format: {format_info.get('format_long_name', 'Inconnu')}\n\n"
            

            report += f"📝 SOUS-TITRES ({len(subtitle_streams)} piste(s)):\n"
            
            if not subtitle_streams:
                report += "  ❌ AUCUNE piste de sous-titres trouvée !\n"
                report += "  💡 Cause probable: Le fichier ne contient pas de sous-titres.\n\n"
            else:
                for i, sub in enumerate(subtitle_streams):
                    index = sub.get("index", "?")
                    codec = sub.get("codec_name", "inconnu")
                    lang = sub.get("tags", {}).get("language", "und")
                    title = sub.get("tags", {}).get("title", "Sans titre")
                    
                    
                    disposition = sub.get("disposition", {})
                    is_default = disposition.get("default", 0) == 1
                    is_forced = disposition.get("forced", 0) == 1
                    
                    report += f"\n  [{index}] Piste {i+1}:\n"
                    report += f"    • Codec: {codec.upper()}\n"
                    report += f"    • Langue: {lang}\n"
                    report += f"    • Titre: {title}\n"
                    report += f"    • Par défaut: {'✅ OUI' if is_default else '❌ NON'}\n"
                    report += f"    • Forcés: {'✅ OUI' if is_forced else '❌ NON'}\n"
                    

                    if not is_default and i == 0:
                        report += "    ⚠️ Cette piste n'est pas définie par défaut\n"
                    if codec not in ['ass', 'ssa', 'subrip', 'srt']:
                        report += (f"    ⚠️ Codec {codec} peut ne pas être "
                                   f"supporté par tous les lecteurs\n")
            

            report += "\n" + "=" * 60 + "\n"
            report += "💡 SOLUTIONS SI LES SOUS-TITRES NE S'AFFICHENT PAS:\n\n"
            
            if not subtitle_streams:
                report += "1. ❌ Le fichier ne contient aucun sous-titre\n"
                report += "   → Utilisez l'inserteur pour en ajouter\n\n"
            else:
                report += "1. 🎛️ DANS VOTRE LECTEUR VIDÉO:\n"
                report += "   • Clic droit → Sous-titres → Sélectionner la piste\n"
                report += "   • Vérifier les raccourcis clavier (souvent 'S' ou 'V')\n"
                report += "   • Aller dans Préférences → Sous-titres\n\n"
                
                report += "2. 📱 LECTEURS RECOMMANDÉS:\n"
                report += "   • VLC Media Player (excellent support)\n"
                report += "   • MPC-HC (Windows)\n"
                report += "   • Kodi (multiplateforme)\n\n"
                
                default_subs = [s for s in subtitle_streams if s.get("disposition", {}).get("default", 0) == 1]
                if not default_subs:
                    report += "3. ⚠️ AUCUNE PISTE PAR DÉFAUT:\n"
                    report += "   • Les sous-titres ne s'activeront pas automatiquement\n"
                    report += "   • Activez-les manuellement dans votre lecteur\n\n"
                

                for sub in subtitle_streams:
                    codec = sub.get("codec_name", "")
                    if codec == "hdmv_pgs_subtitle":
                        report += "4. 🎨 SOUS-TITRES GRAPHIQUES (PGS) détectés:\n"
                        report += "   • Ces sous-titres sont des images, pas du texte\n"
                        report += "   • Impossible de les modifier ou personnaliser\n\n"
                        break
            

            self.show_diagnostic_report(report, Path(filename).name)
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erreur", f"Erreur lors du diagnostic: {e}")
        except json.JSONDecodeError:
            messagebox.showerror("Erreur", "Erreur lors de l'analyse des données")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
        finally:
            self.progress.stop()
            self.status_label.config(text="Diagnostic terminé")

    def show_diagnostic_report(self, report, filename):
        """Afficher le rapport de diagnostic dans une nouvelle fenêtre"""

        diag_window = tk.Toplevel(self.root)
        diag_window.title(f"Diagnostic - {filename}")
        diag_window.geometry("700x600")
        diag_window.transient(self.root)
        

        main_frame = ttk.Frame(diag_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        report_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=report_text.yview)
        report_text.configure(yscrollcommand=scrollbar.set)
        
        report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        

        report_text.insert(1.0, report)
        report_text.config(state=tk.DISABLED)
        

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def copy_to_clipboard():
            diag_window.clipboard_clear()
            diag_window.clipboard_append(report)
            messagebox.showinfo("Copié", "Rapport copié dans le presse-papiers")
        
        copy_btn = ttk.Button(button_frame, text="📋 Copier", command=copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT)
        
        close_btn = ttk.Button(button_frame, text="Fermer", command=diag_window.destroy)
        close_btn.pack(side=tk.RIGHT)

    def run(self):
        """Lancer l'application"""
        self.setup_ui()
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = SubtitleInserter()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrompue par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        messagebox.showerror("Erreur", f"Erreur inattendue: {e}")


if __name__ == "__main__":
    main()