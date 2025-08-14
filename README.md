# ASS Auto Translate - Outils de Traduction de Sous-titres

Ce projet contient trois outils Python pour extraire, traduire et insérer des sous-titres ASS dans des fichiers MKV.

## 🛠️ Outils Disponibles

1. **ASS MKV Extractor** - Extrait les sous-titres ASS des fichiers MKV
2. **ASS Auto Translator** - Traduit automatiquement les sous-titres ASS
3. **ASS MKV Inserter** - Réinsère les sous-titres traduits dans les fichiers MKV

## 📋 Prérequis

### FFmpeg
FFmpeg est requis pour l'extraction et l'insertion des sous-titres.

**Windows :**
- Téléchargez FFmpeg depuis [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Extrayez le contenu dans un dossier (ex: `C:\ffmpeg`)
- Ajoutez `C:\ffmpeg\bin` à votre variable d'environnement PATH

**Vérification :**
```bash
ffmpeg -version
```

### Python
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. **Clonez le repository :**
```bash
git clone [https://github.com/YeoDBGT/ASS-Auto-Translate]
cd ASS-Auto-Translate
```

2. **Installez les dépendances Python :**
```bash
pip install -r requirements.txt
```

3. **Configurez l'API OpenAI (pour la traduction) :**
   - Copiez `config_example.ini` vers `translator_config.ini`
   - Ajoutez votre clé API OpenAI dans `translator_config.ini`

## 📖 Utilisation

### 1. Extraction des Sous-titres
```bash
python "ASS MKV Extractor.py"
```

### 2. Traduction des Sous-titres
```bash
python "ASS Auto translator.py"
```

### 3. Insertion des Sous-titres Traduits
```bash
python "ASS MKV Inserter.py"
```

## ⚠️ Notes Importantes

- Assurez-vous que FFmpeg est accessible via la ligne de commande
- Pour la traduction, une clé API OpenAI valide est requise
- Sauvegardez vos fichiers originaux avant traitement
- Les fichiers MKV doivent contenir des pistes de sous-titres ASS

## 🔧 Résolution de Problèmes

**FFmpeg non trouvé :**
- Vérifiez que FFmpeg est installé et dans le PATH
- Redémarrez votre terminal après modification du PATH

**Erreur de traduction :**
- Vérifiez votre clé API OpenAI dans `translator_config.ini`
- Assurez-vous d'avoir des crédits disponibles sur votre compte OpenAI

## 📝 Structure des Fichiers

```
ASS-Auto-Translate/
├── ASS MKV Extractor.py      # Extracteur de sous-titres
├── ASS Auto translator.py     # Traducteur automatique
├── ASS MKV Inserter.py       # Insertion des sous-titres
├── requirements.txt           # Dépendances Python
├── translator_config.ini      # Configuration de l'API
└── config_example.ini        # Exemple de configuration
```
