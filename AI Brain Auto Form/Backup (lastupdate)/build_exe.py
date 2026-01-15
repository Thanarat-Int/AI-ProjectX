import PyInstaller.__main__
import os
import shutil

# Make sure output dirs exist
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

print("🚀 Building AI Brain Standalone Executable...")

PyInstaller.__main__.run([
    'main.py',                       # Entry point
    '--name=AIBrain_Genius',         # Name of the exe
    '--onefile',                     # Single exe file
    '--noconsole',                   # Hide console (GUI app)
    '--add-data=personas.json;.',    # Include Data
    '--add-data=config.json;.',      # Include Config
    '--add-data=assets;assets',      # Include Assets folders
    '--hidden-import=PIL',           # Ensure Pillow is valid
    '--hidden-import=customtkinter', 
    '--icon=assets/icon.ico',        # (Optional) Icon if you have one
    '--clean',
])

print("\n✅ Build Complete! Check the 'dist' folder.")
