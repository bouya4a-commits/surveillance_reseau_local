
# Activer l'environnement (si nécessaire)
python3 -m venv forensic_env
source forensic_env/bin/activate

# Installer les dépendances
pip install flask psutil

# Lancer le soft
sudo python3 app.py         
