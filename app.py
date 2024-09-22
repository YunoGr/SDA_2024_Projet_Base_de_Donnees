import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import data_giants  # Importe les fonctions de gestion de la base de données depuis data_giants.py

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
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    character = db.relationship('Character', backref=db.backref('comments', lazy=True))

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    bio = db.Column(db.Text)
    profile = db.Column(db.String(100))
    experience_level = db.Column(db.String(50))
    character_class = db.Column(db.String(50))  # Notez le changement de nom pour éviter les conflits avec le mot-clé Python
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

@app.route('/character/<int:character_id>', methods=['GET'])
def view_character(character_id):
    character = Character.query.get(character_id)
    
    if character is None:
        return "Personnage non trouvé", 404
    
    skills = [(skill.name, skill.level) for skill in character.skills]
    projects = [(project.name, project.description) for project in character.projects]
    
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
    conn = data_giants.create_connection()
    characters = data_giants.list_characters(conn)  # Récupère tous les personnages 
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
        
        conn = data_giants.create_connection()
        data_giants.add_character(conn, first_name, last_name, phone_number, email, bio, profile, experience_level, class_name)
        
        flash(f'Personnage {first_name} ajouté avec succès!', 'sucess')

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
    conn = data_giants.create_connection()
    characters = data_giants.search_characters(conn, query)
    return render_template('index.html', characters=characters)



# Lancer l'application Flask
if __name__ == "__main__":
    app.run(debug=True)
