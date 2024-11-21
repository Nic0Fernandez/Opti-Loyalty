import subprocess
import os

# Obtenez le chemin absolu du répertoire contenant train_models.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Chemin du répertoire contenant les autres scripts
scripts_dir = os.path.join(current_dir)

# Liste des scripts à exécuter
scripts_to_run = [
    "collaborative_model.py",
    "gradient_boosting.py",
    "random_forest.py",
    "recommandation_ingredient.py",
    "tf_idf.py"
]

# Fonction pour exécuter un script Python
def run_script(script_name):
    script_path = os.path.join(scripts_dir, script_name)
    if os.path.exists(script_path):
        print(f"Exécution de {script_name} à partir de {script_path}...")
        try:
            subprocess.run(["python", script_path], check=True)
            print(f"{script_name} exécuté avec succès.\n")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de {script_name}: {e}\n")
    else:
        print(f"Script {script_name} introuvable dans {scripts_dir}.\n")

# Exécuter tous les scripts
if __name__ == "__main__":
    for script in scripts_to_run:
        run_script(script)
