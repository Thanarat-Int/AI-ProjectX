import PyInstaller.__main__
import os
import shutil
import customtkinter

# Helper to get CTk data path
ctk_path = os.path.dirname(customtkinter.__file__)

# Cleanup (Ignore errors if file is locked)
if os.path.exists("dist"): shutil.rmtree("dist", ignore_errors=True)
if os.path.exists("build"): shutil.rmtree("build", ignore_errors=True)

print("🚀 Building AI Brain Standalone Executable...")

PyInstaller.__main__.run([
    'main.py',                       
    '--name=AIBrain_Genius',         
    '--onefile',                     
    '--noconsole',                   # HIDE Console for Final Production Build
    '--icon=assets/icon.ico',        # App Icon
    '--add-data=personas.json;.',    
    '--add-data=config.json;.',      
    '--add-data=groups.json;.',      
    '--add-data=assets;assets',      
    f'--add-data={ctk_path};customtkinter', # FORCE include CTk assets
    '--hidden-import=PIL',           
    '--hidden-import=customtkinter', 
    '--hidden-import=sklearn.utils._cython_blas',
    '--hidden-import=sklearn.neighbors.typedefs',
    '--hidden-import=sklearn.neighbors.quad_tree',
    '--hidden-import=sklearn.tree',
    '--hidden-import=sklearn.tree._utils',
    '--clean',
])

print("📦 Copying default data files to dist folder...")
# We copy these so the user has editable files next to the exe
if not os.path.exists("dist"): os.makedirs("dist")
try:
    shutil.copy("personas.json", "dist/personas.json")
    shutil.copy("config.json", "dist/config.json")
except: pass

print("\n✅ Build Complete! Please check 'dist/AIBrain_Genius.exe'")
