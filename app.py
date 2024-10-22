import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import data_giants  # Ici nous importons les fonctions de gestion de la base de données depuis data_giants.py


################ ################ ################ ################ ################ ################ ################ ################ ################ ################ ################ 


app = Flask(__name__)

# Configuration de la clé secrète
app.config['SECRET_KEY'] = os.urandom(24)  # Génère une clé aléatoire à chaque exécution

# Configuration de la base de données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_giants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    
    # Relation vers le personnage (pas besoin de backref ici, il est déjà dans Character)
    character = db.relationship('Character')





class Skill(db.Model):
    __tablename__ = 'skills'  # Assurez-vous que le nom de la table est 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    
    # Relation inverse avec Character
    character = db.relationship('Character', backref=db.backref('skills', lazy=True))

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile = db.Column(db.String(100))
    experience_level = db.Column(db.String(50))
    character_class = db.Column(db.String(50))  
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Relation vers les projets
    projects = db.relationship('Project', backref='character', lazy=True)

    # Utilisez un backref unique comme 'character_comments'
    comments = db.relationship('Comment', backref='character_comments', cascade='all, delete-orphan', lazy=True)





class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)

@app.route('/character/<int:character_id>', methods=['GET'])
def view_character(character_id):
    character = Character.query.get_or_404(character_id)
    
    # Accéder aux compétences et projets via les relations définies
    skills = character.skills
    projects = character.projects
    
    return render_template('view_character.html', character=character, skills=skills, projects=projects)





@app.route('/add_comment/<int:character_id>', methods=['POST'])
def add_comment(character_id):
    comment_text = request.form['comment']
    new_comment = Comment(character_id=character_id, text=comment_text)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_character', character_id=character_id))


# Page d'accueil
@app.route('/')
def index():
    characters = Character.query.all()  # Utilisation de SQLAlchemy pour récupérer tous les personnages
    return render_template('index.html', characters=characters)

# Formulaire pour ajouter un personnage
@app.route('/add_character', methods=['GET', 'POST'])
def add_character():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        bio = request.form['bio']
        profile = request.form['profile']
        experience_level = request.form['experience_level']
        class_name = request.form['class']
        
        # Utilisation de SQLAlchemy pour ajouter un personnage
        new_character = Character(
            first_name=first_name, 
            last_name=last_name, 
            phone_number=phone_number, 
            email=email, 
            bio=bio, 
            profile=profile, 
            experience_level=experience_level, 
            character_class=class_name
        )
        
        db.session.add(new_character)
        db.session.commit()  # Assurez-vous que les changements sont bien enregistrés dans la base de données
        
        flash(f'Personnage {first_name} ajouté avec succès!', 'success')
        return redirect('/')
    
    return render_template('add_character.html')



@app.route('/edit_character/<int:character_id>', methods=['GET', 'POST'])
def edit_character(character_id):
    character = Character.query.get_or_404(character_id)
    
    if request.method == 'POST':
        # Récupérer les nouvelles données du formulaire
        character.first_name = request.form['first_name']
        character.last_name = request.form['last_name']
        character.phone_number = request.form.get('phone_number')
        character.email = request.form.get('email')
        character.bio = request.form.get('bio')
        character.profile = request.form.get('profile')
        character.experience_level = request.form.get('experience_level')
        character.character_class = request.form.get('class')
        
        # Enregistrer les modifications dans la base de données
        db.session.commit()
        
        # Afficher un message de confirmation et rediriger vers la page d'accueil
        flash('Personnage mis à jour avec succès!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_character.html', character=character)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    
    # Rechercher dans la base de données par prénom ou nom
    characters = Character.query.filter(
        (Character.first_name.ilike(f"%{query}%")) | (Character.last_name.ilike(f"%{query}%"))
    ).all()
    
    return render_template('index.html', characters=characters)


@app.route('/filter', methods=['GET'])
def filter_characters():
    query = request.args.get('query')
    experience_level = request.args.get('experience_level')
    
    # Commencer avec une requête vide
    characters = Character.query
    
    # Appliquer le filtre par nom/prénom si présent
    if query:
        characters = characters.filter(
            (Character.first_name.ilike(f"%{query}%")) | (Character.last_name.ilike(f"%{query}%"))
        )
    
    # Appliquer le filtre par niveau d'expérience si présent
    if experience_level:
        characters = characters.filter(Character.experience_level == experience_level)
    
    characters = characters.all()  # Exécuter la requête
    
    return render_template('index.html', characters=characters)

@app.route('/delete_character/<int:character_id>', methods=['POST'])
def delete_character(character_id):
    # Mot de passe à valider (vous pouvez le stocker de manière sécurisée)
    correct_password = "admin_password"
    
    # Récupérer le mot de passe soumis par l'utilisateur
    entered_password = request.form['password']
    
    if entered_password == correct_password:
        # Rechercher le personnage dans la base de données
        character = Character.query.get_or_404(character_id)
        
        # Supprimer le personnage de la base de données
        db.session.delete(character)
        db.session.commit()
        
        flash(f"Le personnage {character.first_name} {character.last_name} a été supprimé avec succès.", "success")
        return redirect(url_for('index'))
    else:
        flash("Mot de passe incorrect. La suppression a échoué.", "danger")
        return redirect(url_for('index'))




# pour tester...
@app.route('/list_all_characters', methods=['GET'])
def list_all_characters():
    characters = Character.query.all()
    return f"Nombre de personnages dans la base de données : {len(characters)}"




# Lancer l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
