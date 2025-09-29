# Vérifier ta version de git 

git --version

-> Si tu obtiens une version (par ex. git version 2.39.3), c’est bon.

# Sinon, il faut installer git :

* Linux (Debian/Ubuntu) : sudo apt install git

* MacOS : brew install git (si tu as Homebrew)

* Windows : installe Git for Windows.

# Déplace-toi dans le dossier où tu veux cloner le dépôt :

cd /chemin/vers/mon/dossier

# Cloner le dépôt

Exécute :

git clone https://github.com/bouya4a-commits/surveillance_reseau_local.git

# Vérifier le dossier cloné

cd surveillance_reseau_local

ls -la   # (ou dir sous Windows)

# Activer l'environnement

python3 -m venv forensic_env

source forensic_env/bin/activate

# Installer les dépendances
pip install flask psutil

# Lancer le soft
sudo python3 app.py         
