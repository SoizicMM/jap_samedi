from flask import Flask, render_template, request, url_for, redirect, session

import pymongo
import os

# Pour gérer les ObjectId
from bson.objectid import ObjectId

# Pour crypter les mots de passe
import bcrypt 



app = Flask("Le Japon")


# Connexion à la BDD
mongo = pymongo.MongoClient("mongodb+srv://soizicb17:tfSNaKo736TOG5T0@cluster0.amaeedj.mongodb.net/?retryWrites=true&w=majority")

# Cookie de session utilisateur
app.secret_key = os.urandom(24)



##############
### FRONT ####
##############

## Gestion de l'accueil ##

@app.route('/')
def index():
  db_lieux = mongo.db.lieux
  lieux = db_lieux.find({})
  db_cafes = mongo.db.cafes
  cafes = db_cafes.find({})
  db_evenements = mongo.db.evenements
  evenements = db_evenements.find({})
  return render_template('index.html', lieux=lieux, cafes=cafes, evenements=evenements)

## Gestion des pages annexes ##

# route des lieux 
@app.route('/lieux')
def lieux():
  db_lieux = mongo.db.lieux
  lieux = db_lieux.find({})
  return render_template('front/lieux.html', lieux=lieux)

# route des cafés 
@app.route('/cafes')
def cafes():
  db_cafes = mongo.db.cafes
  cafes = db_cafes.find({})
  return render_template('front/cafes.html', cafes=cafes)
  
# route des évènements
@app.route('/evenements')
def evenements():
  db_evenements = mongo.db.evenements
  evenements = db_evenements.find({})
  return render_template('front/evenements.html', evenements=evenements)
  
# route d'un lieu
@app.route("/lieux/<id_post>")
def lieu(id_post):
  db_lieux = mongo.db.lieux
  lieu = db_lieux.find_one({"_id": ObjectId(id_post)})
  return render_template("front/lieu.html", lieu=lieu)

# route d'un café
@app.route("/cafes/<id_post>")
def cafe(id_post):
  db_cafes = mongo.db.cafes
  cafe = db_cafes.find_one({"_id": ObjectId(id_post)})
  return render_template("front/cafe.html", cafe=cafe)
  
# route d'un evenement
@app.route("/evenements/<id_post>")
def evenement(id_post):
  db_evenements = mongo.db.evenements
  evenement = db_evenements.find_one({"_id": ObjectId(id_post)})
  return render_template("front/evenement.html", evenement=evenement)

# Route pour créer un nouveau lieu
@app.route('/nouveau_lieu', methods=['POST', 'GET'])
def nouveau_lieu():
  # Si on essaye d'envoyer le formulaire
  if request.method == 'POST':
    # On appelle la table "annonces" de la bdd
    db_lieux = mongo.db.lieux
    titre = request.form['titre']
    img = request.form['image']
    intro = request.form['introduction']
    description = request.form['description']
    # On insère ces nouvelles données dans la bdd
    db_lieux.insert_one({
      'titre': titre,
      'img' : img,
      "intro" : intro,
      'description': description
    })
    return render_template("front/nouveau_lieu.html",
                           erreur="Votre annonce a bien été soumise")
  else:
    return render_template(
      "front/nouveau_lieu.html",
      erreur="Veuillez saisir un titre et une description")
    
# Route pour modifier un lieu
@app.route('/update_lieu/<id_post>', methods=['POST', 'GET'])
def update_lieu(id_post):
  db_lieux = mongo.db.lieux
  lieu = db_lieux.find_one({"_id": ObjectId(id_post)})
  #Si l'on est en méthode GET
  if request.method == 'GET':
    return render_template("front/modif_lieu.html", lieu=lieu)
  # Sinon on est en POST et on effectue les modifs
  else:
    titre = request.form['titre']
    img = request.form['image']
    intro = request.form['introduction']
    description = request.form['description']
    db_lieux.update_one({"_id": ObjectId(id_post)},
                        {"$set": {
                          "titre": titre,
                          "img": img,
                          "intro": intro,
                          "description": description
                        }})
    return redirect(url_for("admin_lieux"))

# Route pour supprimer un lieu
@app.route('/delete_lieu/<id_post>')
def delete_lieu(id_post):
  db_lieux = mongo.db.lieux
  lieu = db_lieux.delete_one( { "_id": ObjectId(id_post) } )
  return redirect(url_for("admin_lieux", lieu=lieu, erreur="votre annonce est bien supprimée"))

##############################
## Gestion des utilisateurs ##
##############################

# Route pour créer un nouvel utilisateur
@app.route('/register', methods=['POST','GET'])
def register():
  # Si on essaye de soumettre un formulaire
  if request.method == 'POST':
    # On verifie qu'un utilisateur du meme nom n'existe pas 
    db_utils = mongo.db.utilisateurs
    # Si l'utilisateur existe déja on demande de re-remplir le formulaire
    if (db_utils.find_one({'nom' : request.form['utilisateur']})):
      return render_template('register.html', erreur="Le nom d'utilisateur existe deja")
    # Sinon on créé l'utilisateur
    else :
      if (request.form['mot_de_passe']==request.form['verif_mot_de_passe']):
        # On crypte le mot de passe
        mdp_encrypte = bcrypt.hashpw(request.form['mot_de_passe'].encode('utf-8'),bcrypt.gensalt())
        # On ajoute l'utilisateur
        db_utils.insert_one({'nom': request.form['utilisateur'], 
                             'mdp' : mdp_encrypte,
                             'role': "abonné"  # Ajouter le rôle ici
                            })
        # On le connecte
        session['util'] = request.form['utilisateur']  
        # On retourne à la page d'accueil
        return redirect(url_for('index'))
      # Sinon on renvoie le template vide et met un message d'erreur
      else:
        return render_template('front/register.html',
                               erreur="Les mots de passe doivent être identiques")
  else:
    return render_template('front/register.html')
    

# route de connexion (si l'on a déjà un compte)
@app.route('/login', methods=['POST','GET'])
def login():
  # Si on essaye de se connecter
  if request.method == 'POST':
    db_utils = mongo.db.utilisateurs
    # On appelle la table utilisateurs de la bdd
    util = db_utils.find_one({'nom' : request.form['utilisateur']})
    # Si l'utilisateur existe
    if util :
      # on vérifie si le mot de passe est bon
      if bcrypt.checkpw(request.form['mot_de_passe'].encode('utf-8'), util['mdp']):
        # Créer une session "role" pour la garder mémorisée
        session['role']= util['role']
        session['util']= request.form['utilisateur']
        return redirect(url_for("index"))
      # Sinon on envoie un message d'erreur du mot de passe incorrect
      else:
        return render_template('front/login.html',
                               erreur="Le mot de passe est incorrect")
    # Sinon on envoie un message que l'utilisateur n'existe pas
    else : 
      return render_template('front/login.html', 
                             erreur="Le nom d'utilisateur n'existe pas")
  else:
    return render_template('front/login.html')

# Exemple d'utilisation du champ 'role' stocké dans la session
@app.route('/dashboard')
def dashboard():
    if 'role' in session:
        role = session['role']
        return f'Vous êtes connecté en tant que {role}'
    else:
        return 'Veuillez vous connecter d\'abord.'

# Route de déconnexion
@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for("index"))



###########################
### BARRE DE RECHERCHE ####
###########################
@app.route('/recherche', methods=['POST'])
def recherche():
  query = request.form['query']
  db_cafes = mongo.db.cafes
  cafes = db_cafes.aggregate([{
    "$match": {
      'titre': {
        '$regex': query,
        '$options': 'i'
      },
    }
  }])
  return render_template('front/resultats.html', 
                         query=query, 
                         cafes=list(cafes))

##############
### ADMIN ####
##############
@app.route('/admin')
def admin():
  if 'util' in session and session['role'] == 'admin':
    db_lieux = mongo.db.lieux
    lieux = db_lieux.find({})
    return render_template('admin/back_accueil.html', lieux=lieux)
  else:
    return 'Accès refusé. Vous devez être connecté en tant qu\'administrateur.'

@app.route('/admin/back_lieux')
def admin_lieux():
  db_lieux = mongo.db.lieux
  lieux = db_lieux.find({})
  return render_template('admin/back_lieux.html', lieux=lieux)

#################
### PAGE 404 ####
#################

@app.route('/erreur-404')
def error_404():
    # Déclenche volontairement une erreur 404
    return render_template('front/erreur_404.html'), 404


@app.errorhandler(404)
def page_not_found(error):
    return render_template('front/erreur_404.html'), 404

app.run(host='0.0.0.0', port=5000)




