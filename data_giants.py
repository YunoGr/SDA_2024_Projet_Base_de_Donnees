import sqlite3

# Connexion à la base de données SQLite
def create_connection():
    conn = sqlite3.connect("data_giants.db")
    return conn

# Création des tables characters, skills et projects
def create_tables(conn):
    # Table des personnages
    create_characters_table = """
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT,
        email TEXT,
        bio TEXT,
        profile TEXT,
        experience_level TEXT,
        class TEXT
    );"""
    
    # Table des compétences
    create_skills_table = """
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        level TEXT NOT NULL,
        character_id INTEGER,
        FOREIGN KEY (character_id) REFERENCES characters (id)
    );"""
    
    # Table des projets
    create_projects_table = """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        character_id INTEGER,
        FOREIGN KEY (character_id) REFERENCES characters (id)
    );"""
    
    conn.execute(create_characters_table)
    conn.execute(create_skills_table)
    conn.execute(create_projects_table)
    print("Tables créées avec succès")



# Ajout d'un personnage
def add_character(conn, first_name, last_name, phone_number, email, bio, profile, experience_level, class_name):
    sql = '''INSERT INTO characters (first_name, last_name, phone_number, email, bio, profile, experience_level, class)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (first_name, last_name, phone_number, email, bio, profile, experience_level, class_name))
    conn.commit()
    print(f"Personnage {first_name} {last_name} ajouté avec succès")


# Liste de tous les personnages
def list_characters(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters")
    rows = cur.fetchall()
    return rows  # Retourner les lignes récupérées



def add_skill(conn, character_id, skill_name, skill_level):
    sql = '''INSERT INTO skills (name, level, character_id)
             VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (skill_name, skill_level, character_id))
    conn.commit()
    print(f"Compétence {skill_name} ajoutée pour le personnage avec l'ID {character_id}")



def list_skills(conn, character_id):
    cur = conn.cursor()
    cur.execute("SELECT name, level FROM skills WHERE character_id = ?", (character_id,))
    rows = cur.fetchall()
    print(f"Compétences du personnage {character_id}:")
    for row in rows:
        print(f"Compétence: {row[0]}, Niveau: {row[1]}")


def add_project(conn, character_id, project_name, project_description):
    sql = '''INSERT INTO projects (name, description, character_id)
             VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (project_name, project_description, character_id))
    conn.commit()
    print(f"Projet {project_name} ajouté pour le personnage avec l'ID {character_id}")


def list_projects(conn, character_id):
    cur = conn.cursor()
    cur.execute("SELECT name, description FROM projects WHERE character_id = ?", (character_id,))
    rows = cur.fetchall()
    print(f"Projets du personnage {character_id}:")
    for row in rows:
        print(f"Projet: {row[0]}, Description: {row[1]}")


def search_characters(conn, query):
    cur = conn.cursor()
    # Requête pour rechercher par prénom ou nom
    cur.execute("SELECT * FROM characters WHERE first_name LIKE ? OR last_name LIKE ?", ('%' + query + '%', '%' + query + '%'))
    rows = cur.fetchall()
    return rows



def filter_characters(conn, query, experience_level):
    cur = conn.cursor()
    # Requête pour rechercher par prénom, nom et filtrer par niveau d'expérience
    sql = "SELECT * FROM characters WHERE (first_name LIKE ? OR last_name LIKE ?)"
    params = ['%' + query + '%', '%' + query + '%']
    
    if experience_level:
        sql += " AND experience_level = ?"
        params.append(experience_level)
    
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    return rows



# Test de connexion et création des tables
if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)
    add_character(conn, "John", "Doe", "+123456789", "john.doe@example.com", "Bio de John", "Développeur", "Intermédiaire", "Ingénieur logiciel")



    # Fermeture de la connexion a la base de donnees
    conn.close()


