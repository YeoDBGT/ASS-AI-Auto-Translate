#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'extraction de sous-titres ASS depuis des fichiers MKV
Permet de sélectionner un fichier MKV et d'extraire les sous-titres intégrés
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json
import os
from pathlib import Path


class SubtitleExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 MKV ASS Extractor")
        self.root.geometry("850x700")
        self.root.minsize(750, 600)
        
        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass
            
        self.selected_file = None
        self.subtitle_tracks = []
        self.selected_tracks_for_extraction = []

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
        width = 850
        height = 700
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
        
        container = tk.Frame(section_frame,
                             bg=self.colors['bg_secondary'],
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
        
        icon_title_frame = tk.Frame(header_frame,
                                   bg=self.colors['bg_secondary'])
        icon_title_frame.pack(anchor=tk.W)
        
        tk.Label(icon_title_frame, text=icon, font=("Segoe UI", 16),
                 fg=self.colors['accent'],
                 bg=self.colors['bg_secondary']).pack(side=tk.LEFT)
        
        tk.Label(icon_title_frame, text=title,
                 font=("Segoe UI", 11, "bold"),
                 fg=self.colors['text_primary'],
                 bg=self.colors['bg_secondary']).pack(side=tk.LEFT,
                                                       padx=(8, 0))
        
        tk.Label(header_frame, text=description, 
                font=("Segoe UI", 9),
                fg=self.colors['text_secondary'], 
                bg=self.colors['bg_secondary']).pack(anchor=tk.W, pady=(2, 0))
        
        controls_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=0, pady=(5, 15))
        
        return controls_frame

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
                              text="🎯 ASS Subtitle Extractor",
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Extrayez facilement les sous-titres de vos fichiers MKV",
                                 font=("Segoe UI", 11),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack(pady=(5, 0))

        file_section = self.create_modern_section(main_frame, "📁 Fichier source")
        file_card = self.create_file_card(file_section, "Fichier vidéo MKV", "🎬",
                                         "Sélectionnez votre fichier MKV contenant des sous-titres")
        
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

        info_section = self.create_modern_section(main_frame, "📋 Informations et logs")
        
        text_container = tk.Frame(info_section, bg=self.colors['bg_tertiary'])
        text_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        self.info_text = tk.Text(text_container, 
                                height=12, 
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
        
        info_scroll = tk.Scrollbar(text_container, 
                                  orient=tk.VERTICAL,
                                  command=self.info_text.yview,
                                  bg=self.colors['bg_tertiary'],
                                  troughcolor=self.colors['bg_tertiary'],
                                  activebackground=self.colors['accent'])
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        actions_section = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        actions_section.pack(fill=tk.X, pady=(10, 0))
        
        button_container = tk.Frame(actions_section, bg=self.colors['bg_primary'])
        button_container.pack(anchor=tk.CENTER, pady=(0, 20))
        
        extract_btn = ttk.Button(button_container, 
                                text="🚀 Extraire les sous-titres",
                                style="Discord.TButton",
                                command=self.extract_subtitles)
        extract_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        analyze_btn = ttk.Button(button_container, 
                                text="📊 Analyser le fichier",
                                style="DiscordSecondary.TButton",
                                 command=self.analyze_subtitles)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.select_btn = ttk.Button(button_container, 
                                    text="🎯 Sélectionner les pistes",
                                    style="DiscordSecondary.TButton",
                                    command=self.show_track_selection)
        
        quit_btn = ttk.Button(button_container, 
                             text="❌ Quitter",
                             style="DiscordSecondary.TButton",
                             command=self.root.quit)
        quit_btn.pack(side=tk.LEFT)

        progress_container = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_container, 
                                       mode='indeterminate',
                                       style='Discord.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, padx=20)

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
        
        self.init_button_states()
    
    def init_button_states(self):
        """Initialiser l'état des boutons"""
        try:
            self.select_btn.pack_forget()
        except Exception:
            pass

    def log_message(self, message):
        """Ajouter un message dans la zone d'information"""
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)
        self.root.update_idletasks()

    def select_file(self):
        """Ouvrir le sélecteur de fichier pour choisir un fichier MKV"""
        filetypes = [
            ("Fichiers MKV", "*.mkv"),
            ("Tous les fichiers", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier MKV",
            filetypes=filetypes
        )

        if filename:
            self.selected_file = filename
            self.file_var.set(filename)
            self.subtitle_tracks = []
            self.selected_tracks_for_extraction = []
            try:
                self.select_btn.pack_forget()
            except Exception:
                pass
            
            self.log_message(f"✅ Fichier sélectionné: {os.path.basename(filename)}")
            self.log_message(f"📍 Chemin: {filename}")
            self.log_message("💡 Utilisez maintenant 'Analyser le fichier' pour détecter les sous-titres")

    def check_ffmpeg(self):
        """Vérifier que ffmpeg et ffprobe sont disponibles"""
        try:
            subprocess.run(["ffprobe", "-version"], capture_output=True,
                           check=True)
            subprocess.run(["ffmpeg", "-version"], capture_output=True,
                           check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror(
                "❌ FFmpeg requis",
                "❌ FFmpeg n'est pas installé ou n'est pas dans le PATH.\n\n"
                "📥 INSTALLATION:\n"
                "• Windows: Téléchargez depuis https://ffmpeg.org/download.html\n"
                "• Ou utilisez: winget install FFmpeg\n"
                "• Ou avec Chocolatey: choco install ffmpeg\n\n"
                "🔧 Assurez-vous que ffmpeg.exe est dans votre PATH."
            )
            return False

    def analyze_subtitles(self):
        """Analyser le fichier MKV pour détecter les sous-titres"""
        if not self.selected_file:
            messagebox.showwarning("⚠️ Fichier requis",
                                   "⚠️ Veuillez d'abord sélectionner un fichier MKV\n\n"
                                   "📁 Utilisez le bouton 'Parcourir' pour choisir votre fichier.")
            return

        if not self.check_ffmpeg():
            return


        self.selected_tracks_for_extraction = []
        try:
            self.select_btn.pack_forget()  # Cacher le bouton au début
        except Exception:
            pass  # Le bouton peut ne pas être encore affiché

        self.progress.start()
        self.log_message("🔍 Analyse du fichier en cours...")
        self.log_message("⚙️ Utilisation de ffprobe pour détecter les pistes...")

        try:

            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                self.selected_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            data = json.loads(result.stdout)


            subtitle_streams = []
            for i, stream in enumerate(data.get("streams", [])):
                if stream.get("codec_type") == "subtitle":
                    codec_name = stream.get("codec_name", "inconnu")
                    language = stream.get("tags", {}).get("language",
                                                          "inconnu")
                    title = stream.get("tags", {}).get("title", "")

                    subtitle_streams.append({
                        "index": i,
                        "codec": codec_name,
                        "language": language,
                        "title": title,
                        "stream_index": stream.get("index")
                    })

            self.subtitle_tracks = subtitle_streams

            if not subtitle_streams:
                self.log_message("❌ Aucun sous-titre trouvé dans ce fichier.")

                try:
                    self.select_btn.pack_forget()
                except Exception:
                    pass
                messagebox.showinfo("Information",
                                    "❌ Aucun sous-titre trouvé dans ce fichier.\n\n"
                                    "💡 Vérifiez que le fichier MKV contient bien "
                                    "des pistes de sous-titres intégrées.")
            else:
                self.log_message(f"✅ Trouvé {len(subtitle_streams)} piste(s) de sous-titres:")
                self.log_message("📋 Détails des pistes détectées:")
                for i, track in enumerate(subtitle_streams):
                    lang_display = track['language'] if track['language'] != 'inconnu' else '❓ Inconnue'
                    title_display = track['title'] if track['title'] else '📝 Sans titre'
                    self.log_message(
                        f"   🎯 Piste {i+1}: {track['codec'].upper()} • "
                        f"🌍 {lang_display} • 🏷️ {title_display}"
                    )
                

                compatible_tracks = [track for track in subtitle_streams
                                   if track['codec'] in ['ass', 'ssa', 'subrip']]
                
                if compatible_tracks:
                    self.log_message(f"🎯 {len(compatible_tracks)} piste(s) compatible(s) pour l'extraction")
                    self.log_message("💡 Utilisez 'Sélectionner les pistes' pour choisir quoi extraire")

                    self.select_btn.pack(side=tk.LEFT, padx=(0, 10))
                else:
                    self.log_message("❌ Aucune piste compatible (ASS/SSA/SRT) trouvée")
    
                    try:
                        self.select_btn.pack_forget()
                    except Exception:
                        pass

        except subprocess.CalledProcessError as e:
            self.log_message(f"❌ Erreur ffprobe: {e}")

            try:
                self.select_btn.pack_forget()
            except Exception:
                pass
            messagebox.showerror("❌ Erreur d'analyse",
                                 f"❌ Erreur lors de l'analyse du fichier:\n\n{e}\n\n"
                                 f"💡 Vérifiez que le fichier n'est pas corrompu.")
        except json.JSONDecodeError:
            self.log_message("❌ Erreur: Données JSON corrompues de ffprobe")

            try:
                self.select_btn.pack_forget()
            except Exception:
                pass
            messagebox.showerror("❌ Erreur de données",
                                 "❌ Erreur lors de l'analyse des données du fichier\n\n"
                                 "💡 Le fichier pourrait être corrompu ou dans un format non supporté.")
        finally:
            self.progress.stop()

    def show_track_selection(self):
        """Afficher l'interface de sélection des pistes"""
        if not self.subtitle_tracks:
            messagebox.showwarning("⚠️ Analyse requise",
                                   "⚠️ Veuillez d'abord analyser le fichier\n\n"
                                   "🔍 Utilisez le bouton 'Analyser le fichier' pour détecter "
                                   "les pistes de sous-titres.")
            return
        

        compatible_tracks = [track for track in self.subtitle_tracks
                           if track['codec'] in ['ass', 'ssa', 'subrip']]
        
        if not compatible_tracks:
            messagebox.showinfo("Information",
                               "❌ Aucune piste compatible (ASS/SSA/SRT) trouvée\n\n"
                               "💡 Les formats supportés sont:\n"
                               "• ASS (Advanced SubStation Alpha)\n"
                               "• SSA (SubStation Alpha)\n"
                               "• SRT (SubRip)")
            return
        

        self.log_message("🎛️ Ouverture du sélecteur de pistes...")
        selected_tracks = self.select_subtitle_tracks(compatible_tracks)
        
        if selected_tracks:
            self.selected_tracks_for_extraction = selected_tracks
            self.log_message(f"✅ {len(selected_tracks)} piste(s) sélectionnée(s) pour l'extraction:")
            for track in selected_tracks:
                lang_info = f" ({track['language']})" if track['language'] != 'inconnu' else ""
                self.log_message(f"   🎯 Piste {track['stream_index']}: {track['codec'].upper()}{lang_info}")
            self.log_message("💡 Utilisez maintenant 'Extraire les sous-titres' pour lancer l'extraction")
        else:
            self.log_message("❌ Aucune piste sélectionnée")

    def extract_subtitles(self):
        """Extraire les sous-titres sélectionnés"""
        if not self.selected_file:
            messagebox.showwarning("⚠️ Fichier requis",
                                   "⚠️ Veuillez d'abord sélectionner un fichier MKV\n\n"
                                   "📁 Utilisez le bouton 'Parcourir' pour choisir votre fichier.")
            return

        if not self.subtitle_tracks:
            messagebox.showwarning("⚠️ Analyse requise",
                                   "⚠️ Veuillez d'abord analyser le fichier\n\n"
                                   "🔍 Utilisez le bouton 'Analyser le fichier' pour détecter "
                                   "les pistes de sous-titres.")
            return

        # Vérifier si des pistes ont déjà été sélectionnées via le bouton
        if self.selected_tracks_for_extraction:
            self.log_message("🎯 Utilisation des pistes précédemment sélectionnées")
            selected_tracks = self.selected_tracks_for_extraction
        else:

            ass_tracks = [track for track in self.subtitle_tracks
                          if track['codec'] in ['ass', 'ssa', 'subrip']]

            if not ass_tracks:
                self.log_message("❌ Aucun sous-titre compatible trouvé pour l'extraction.")
                messagebox.showinfo("Information",
                                        "❌ Aucun sous-titre compatible (ASS/SSA/SRT) trouvé\n\n"
                                        "💡 Les formats supportés sont:\n"
                                        "• ASS (Advanced SubStation Alpha)\n"
                                        "• SSA (SubStation Alpha)\n"
                                        "• SRT (SubRip)\n\n"
                                        "🔍 Astuce: Analysez d'abord le fichier, puis utilisez "
                                        "'Sélectionner les pistes' pour choisir.")
                return
            
            self.log_message(f"🎯 {len(ass_tracks)} piste(s) compatible(s) trouvée(s) pour l'extraction")


            selected_tracks = []
            if len(ass_tracks) == 1:
                selected_tracks = ass_tracks
                self.log_message("📋 Une seule piste compatible trouvée, sélection automatique")
            else:
                self.log_message(f"🎛️ Plusieurs pistes trouvées ({len(ass_tracks)}), ouverture du sélecteur...")
                selected_tracks = self.select_subtitle_tracks(ass_tracks)

            if not selected_tracks:
                self.log_message("❌ Aucune piste sélectionnée pour l'extraction")
                return


        self.log_message(f"🚀 Début de l'extraction de {len(selected_tracks)} piste(s)")
        self.progress.start()
        base_name = Path(self.selected_file).stem
        output_dir = Path(self.selected_file).parent
        self.log_message(f"📁 Dossier de sortie: {output_dir}")

        try:
            for track in selected_tracks:

                if track['codec'] in ['ass', 'ssa']:
                    ext = '.ass'
                elif track['codec'] == 'subrip':
                    ext = '.srt'
                else:
                    ext = '.sub'


                lang_suffix = (f"_{track['language']}"
                               if track['language'] != 'inconnu' else "")
                title_suffix = f"_{track['title']}" if track['title'] else ""
                output_file = (output_dir /
                               f"{base_name}{lang_suffix}{title_suffix}{ext}")


                cmd = [
                    "ffmpeg",
                    "-i", self.selected_file,
                    "-map", f"0:{track['stream_index']}",
                    "-c", "copy",
                    "-y",
                    str(output_file)
                ]

                lang_info = f" ({track['language']})" if track['language'] != 'inconnu' else ""
                self.log_message(f"⚙️ Extraction de la piste {track['stream_index']}: "
                                f"{track['codec'].upper()}{lang_info}...")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    self.log_message(f"✅ Succès: {output_file.name}")
                else:
                    self.log_message(f"❌ Échec pour la piste {track['stream_index']}: {result.stderr}")

            self.log_message("🎉 Extraction terminée avec succès !")
            self.log_message("💡 Vous pouvez faire une nouvelle sélection si besoin")
            

            self.selected_tracks_for_extraction = []
            
            messagebox.showinfo("Terminé", 
                               f"🎉 Extraction terminée !\n\n"
                               f"📁 {len(selected_tracks)} fichier(s) créé(s) dans:\n"
                               f"{output_dir}\n\n"
                               f"💡 Les fichiers sont prêts à être utilisés.\n\n"
                               f"🔄 Vous pouvez maintenant faire une nouvelle sélection si besoin.")

        except Exception as e:
            self.log_message(f"💥 Erreur critique: {e}")
            messagebox.showerror("Erreur",
                                 f"💥 Erreur lors de l'extraction:\n\n{e}\n\n"
                                 f"📋 Vérifiez les logs pour plus d'informations.")
        finally:
            self.progress.stop()

    def select_subtitle_tracks(self, tracks):
        """Interface moderne pour sélectionner les pistes de sous-titres à extraire"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🎯 Sélection des sous-titres")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()


        dialog_width = 600
        dialog_height = 650
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (dialog_width // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


        main_canvas = tk.Canvas(dialog, bg=self.colors['bg_primary'], highlightthickness=0)
        main_scrollbar = tk.Scrollbar(dialog, orient="vertical", command=main_canvas.yview,
                                     bg=self.colors['bg_secondary'],
                                     troughcolor=self.colors['bg_primary'],
                                     activebackground=self.colors['accent'])
        main_scrollable_frame = tk.Frame(main_canvas, bg=self.colors['bg_primary'])

        main_scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)


        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")


        def _on_mousewheel_dialog(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_mousewheel_dialog(event):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel_dialog)

        def _unbind_mousewheel_dialog(event):
            main_canvas.unbind_all("<MouseWheel>")

        main_canvas.bind('<Enter>', _bind_mousewheel_dialog)
        main_canvas.bind('<Leave>', _unbind_mousewheel_dialog)


        header_frame = tk.Frame(main_scrollable_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(header_frame, 
                text="🎯 Sélection des sous-titres",
                font=("Segoe UI", 16, "bold"),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_primary']).pack()
        
        tk.Label(header_frame,
                text="Choisissez les pistes de sous-titres à extraire",
                font=("Segoe UI", 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary']).pack(pady=(5, 0))
        
        tk.Label(header_frame,
                text="💡 Utilisez la molette ou la barre de défilement pour naviguer",
                font=("Segoe UI", 9),
                fg=self.colors['warning'],
                bg=self.colors['bg_primary']).pack(pady=(5, 0))


        content_frame = tk.Frame(main_scrollable_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=20, pady=10)


        check_vars = []
        for i, track in enumerate(tracks):
            var = tk.BooleanVar(value=True)  # Tout sélectionné par défaut
            check_vars.append(var)


            track_frame = tk.Frame(content_frame, bg=self.colors['bg_tertiary'])
            track_frame.pack(fill=tk.X, padx=10, pady=5)
            

            track_content = tk.Frame(track_frame, bg=self.colors['bg_tertiary'])
            track_content.pack(fill=tk.X, padx=15, pady=10)
            

            check_frame = tk.Frame(track_content, bg=self.colors['bg_tertiary'])
            check_frame.pack(fill=tk.X)
            
            checkbox = tk.Checkbutton(check_frame, 
                                     variable=var,
                                     bg=self.colors['bg_tertiary'],
                                     fg=self.colors['text_primary'],
                                     activebackground=self.colors['bg_tertiary'],
                                     activeforeground=self.colors['accent'],
                                     selectcolor=self.colors['bg_tertiary'],
                                     font=("Segoe UI", 10))
            checkbox.pack(side=tk.LEFT)
            

            info_frame = tk.Frame(check_frame, bg=self.colors['bg_tertiary'])
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            

            title_text = f"📝 Piste {track['stream_index']}: {track['codec'].upper()}"
            tk.Label(info_frame, text=title_text,
                    font=("Segoe UI", 10, "bold"),
                    fg=self.colors['text_primary'],
                    bg=self.colors['bg_tertiary']).pack(anchor=tk.W)
            

            details = []
            if track['language'] != 'inconnu':
                details.append(f"🌍 {track['language']}")
            if track['title']:
                details.append(f"🏷️ {track['title']}")
            
            if details:
                details_text = " • ".join(details)
                tk.Label(info_frame, text=details_text,
                        font=("Segoe UI", 9),
                        fg=self.colors['text_secondary'],
                        bg=self.colors['bg_tertiary']).pack(anchor=tk.W)


        button_frame = tk.Frame(main_scrollable_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill=tk.X, padx=20, pady=(20, 30))
        
        button_container = tk.Frame(button_frame, bg=self.colors['bg_primary'])
        button_container.pack(anchor=tk.CENTER)

        selected_tracks = []

        def on_ok():
            for i, var in enumerate(check_vars):
                if var.get():
                    selected_tracks.append(tracks[i])

            main_canvas.unbind_all("<MouseWheel>")
            dialog.destroy()

        def on_cancel():

            main_canvas.unbind_all("<MouseWheel>")
            dialog.destroy()


        ok_btn = tk.Button(button_container, text="✅ Extraire sélectionnés",
                          command=on_ok,
                          bg=self.colors['accent'],
                          fg='white',
                          font=("Segoe UI", 11, "bold"),
                          relief='flat',
                          bd=0,
                          padx=25, pady=12,
                          activebackground=self.colors['accent_hover'],
                          cursor='hand2')
        ok_btn.pack(side=tk.LEFT, padx=(0, 15), pady=10)
        
        cancel_btn = tk.Button(button_container, text="❌ Annuler",
                              command=on_cancel,
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'],
                              font=("Segoe UI", 11),
                              relief='flat',
                              bd=0,
                              padx=25, pady=12,
                              activebackground=self.colors['bg_secondary'],
                              cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, pady=10)


        def on_closing():
            main_canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_closing)


        dialog.wait_window()

        return selected_tracks

    def run(self):
        """Lancer l'application"""
        self.setup_ui()
        self.log_message("🎯 MKV ASS Extractor démarré avec succès !")
        self.log_message("📁 Étape 1: Sélectionnez un fichier MKV avec le bouton 'Parcourir'")
        self.log_message("🔍 Étape 2: Analysez le fichier pour détecter les pistes de sous-titres")
        self.log_message("🎛️ Étape 3: Utilisez 'Sélectionner les pistes' pour choisir quoi extraire")
        self.log_message("🚀 Étape 4: Lancez l'extraction avec 'Extraire les sous-titres'")
        self.log_message("")
        self.log_message("💡 Le bouton 'Sélectionner les pistes' apparaîtra après l'analyse")
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    try:
        app = SubtitleExtractor()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrompue par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        input("Appuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()