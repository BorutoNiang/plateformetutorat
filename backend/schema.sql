-- ============================================================
--  UniTutor — Schéma MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS unitutor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE unitutor;

CREATE TABLE IF NOT EXISTS utilisateurs (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nom          VARCHAR(100)  NOT NULL,
    prenom       VARCHAR(100)  NOT NULL,
    email        VARCHAR(255)  NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255)  NOT NULL,
    role         ENUM('etudiant','tuteur') NOT NULL DEFAULT 'etudiant',
    universite   VARCHAR(200),
    niveau       VARCHAR(100),
    bio          TEXT,
    photo        VARCHAR(255),
    note_moy     DECIMAL(3,2)  DEFAULT 0.00,
    nb_sessions  INT           DEFAULT 0,
    actif        TINYINT(1)    DEFAULT 1,
    cree_le      DATETIME      DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role  (role),
    INDEX idx_email (email)
);

CREATE TABLE IF NOT EXISTS matieres (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    nom     VARCHAR(150) NOT NULL UNIQUE,
    domaine VARCHAR(100)
);

INSERT IGNORE INTO matieres (nom, domaine) VALUES
('Analyse mathématique','Mathématiques'),
('Algèbre linéaire','Mathématiques'),
('Probabilités & Stats','Mathématiques'),
('Algorithmique','Informatique'),
('Python','Informatique'),
('Bases de données','Informatique'),
('Physique mécanique','Physique'),
('Thermodynamique','Physique'),
('Microéconomie','Économie'),
('Macroéconomie','Économie');

CREATE TABLE IF NOT EXISTS tuteur_matieres (
    tuteur_id  INT NOT NULL,
    matiere_id INT NOT NULL,
    PRIMARY KEY (tuteur_id, matiere_id),
    FOREIGN KEY (tuteur_id)  REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id) REFERENCES matieres(id)     ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sessions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT      NOT NULL,
    tuteur_id   INT      NOT NULL,
    matiere_id  INT,
    date_heure  DATETIME NOT NULL,
    duree_min   INT      DEFAULT 60,
    statut      ENUM('en_attente','confirmee','terminee','annulee') DEFAULT 'en_attente',
    notes       TEXT,
    cree_le     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (tuteur_id)   REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id)  REFERENCES matieres(id)     ON DELETE SET NULL,
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_tuteur   (tuteur_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    expediteur_id   INT  NOT NULL,
    destinataire_id INT  NOT NULL,
    contenu         TEXT NOT NULL,
    lu              TINYINT(1) DEFAULT 0,
    envoye_le       DATETIME   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expediteur_id)   REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (destinataire_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_conv (expediteur_id, destinataire_id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    session_id  INT     NOT NULL UNIQUE,
    auteur_id   INT     NOT NULL,
    note        TINYINT NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire TEXT,
    cree_le     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)     ON DELETE CASCADE,
    FOREIGN KEY (auteur_id)  REFERENCES utilisateurs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progression (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT     NOT NULL,
    matiere_id  INT     NOT NULL,
    pourcentage TINYINT DEFAULT 0,
    maj_le      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_prog (etudiant_id, matiere_id),
    FOREIGN KEY (etudiant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (matiere_id)  REFERENCES matieres(id)     ON DELETE CASCADE
);

-- ============================================================
--  Données de démo (mots de passe : Demo1234!)
--  Hash généré avec werkzeug.security.generate_password_hash
-- ============================================================
INSERT IGNORE INTO utilisateurs (nom, prenom, email, mot_de_passe, role, universite, niveau, bio) VALUES
('Mbaye',  'Amara',  'amara@demo.com',  'scrypt:32768:8:1$placeholder$hash', 'tuteur',   'UCAD', 'Master 2 Mathématiques',   'Passionné par l analyse et l algèbre.'),
('Diallo', 'Karim',  'karim@demo.com',  'scrypt:32768:8:1$placeholder$hash', 'tuteur',   'ESP',  'Doctorant Informatique',    'Spécialiste algorithmique et Python.'),
('Ndiaye', 'Fatou',  'fatou@demo.com',  'scrypt:32768:8:1$placeholder$hash', 'tuteur',   'UGB',  'Master 1 Physique',         'Passionnée par la physique théorique.'),
('Sarr',   'Sophie', 'sophie@demo.com', 'scrypt:32768:8:1$placeholder$hash', 'etudiant', 'UCAD', 'Licence 3 Informatique',    NULL);

INSERT IGNORE INTO tuteur_matieres (tuteur_id, matiere_id) VALUES
(1,1),(1,2),(1,3),(2,4),(2,5),(2,6),(3,7),(3,8);
