# INSTALLATION

# Activer l'environnement

python3 -m venv forensic_env

source forensic_env/bin/activate

# Installer les dépendances
pip install flask psutil

# Lancer le soft
sudo python3 app.py         



##
##

# Travailler en local : 

git --version

-> Si git version x.xx.x, c’est bon.

# Sinon, installer git :

* Linux : sudo apt install git

* MacOS : brew install git
  
* Windows : installe Git for Windows.

# Se déplacer dans le dossier où cloner le dépôt :

cd /chemin/vers/mon/dossier

# Le cloner

git clone https://github.com/bouya4a-commits/surveillance_reseau_local.git

# Vérifier le dossier cloné

cd surveillance_reseau_local

ls -la   # (ou dir sous Windows)



# Vérifier l’état du dépôt

Avant de faire un git pull, pour voir si le dépôt est à jour :

git status

Si “Your branch is up to date” → rien à faire.

Si modifications locales, il faudra soit les committer avant, soit les stocker temporairement (stash).

Si modifié des fichiers en local

# Pour sauvegarder les changements avant d’actualiser :

git add .
git commit -m "Mes modifs"
git pull


# Si besoin de mettre de côté les changements temporairement :

git stash
git pull
git stash pop
