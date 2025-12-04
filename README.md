# StreamEvents

Aplicació Django per gestionar esdeveniments i usuaris (extensible): base educativa amb bones pràctiques (entorns, estructura, separació de templates/static, etc.). Opcionalment es pot integrar MongoDB (via djongo) més endavant.

## ✨ Objectius
- Practicar un projecte Django modular.
- Treballar amb un usuari personalitzat (app users).
- Organitzar templates, estàtics i media correctament.
- Introduir fitxers d'entorn (.env) i bones pràctiques Git.
- Preparar el terreny per a futures funcionalitats (API, auth avançada, etc.).

## 🧱 Stack Principal
- Python 3.11+ (recomanat)
- Django (versió segons requirements.txt)
- SQLite (inicialment) / opcional: MongoDB + djongo
- HTML / CSS / JS bàsic (templates)
- (Opcional futur) DRF, WebSockets, Redis...

## 📂 Estructura Simplificada
streamevents/
manage.py
config/               # Configuració global del projecte
users/                # App per a la gestió d'usuaris
templates/            # Plantilles HTML globals
static/               # Recursos estàtics (css, js, img)
media/                # Fitxers pujats per usuaris (NO va a Git)
fixtures/             # Dades d'exemple (json)
seeds/                # Scripts Python per crear dades (opcional)
requirements.txt
env.example
.env                  # (privat, no versionar)
README.md
.gitignore


## ✅ Requisits previs
- Python instal·lat
- pip i virtualenv (o equivalent)
- (Opcional) MongoDB en marxa si canvies de SQLite

## 🚀 Instal·lació ràpida
git clone <REPO_URL>
cd streamevents
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env             # Edita SECRET_KEY i altres valors
python manage.py migrate
python manage.py runserver

Obre: http://127.0.0.1:8000/

## 🔐 Variables d'entorn (env.example)
SECRET_KEY=canvia-aixo
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URL=mongodb://localhost:27017
DB_NAME=streamevents_db

Si no uses Mongo encara, deixa igual i segueix amb SQLite.

## 🧪 Tests
Si afegeixes tests:
python manage.py test

(O si uses pytest: `pytest`)

## 👤 Superusuari
python manage.py createsuperuser

Panell admin: /admin/

## 🗃️ Migrar a MongoDB (opcional futur)
1. Instala djongo o motor triat:
   pip install djongo pymongo
2. Edita config/settings.py:
DATABASES = {
"default": {
"ENGINE": "djongo",
"NAME": "streamevents_db",
"CLIENT": {
"host": os.environ.get("MONGO_URL")
}
}
}
3. Executa migracions (pot donar warnings segons versions).

(Recomanació: primer consolidar el flux amb SQLite.)

## 🛠️ Comandes útils
python manage.py makemigrations
python manage.py migrate
python manage.py shell
python manage.py collectstatic   # (en producció)


## 💾 Fixtures (exemple)
Carregar dades inicials:
python manage.py loaddata fixtures/groups.json


## 🌱 Seeds (exemple d'script)
python seeds/seed_basic.py

(Executa dins entorn virtual.)

## 🌍 Preparar per producció (resum)
- DEBUG=0
- Afegir domini a ALLOWED_HOSTS
- Generar SECRET_KEY segura
- Configurar servidor web (nginx/gunicorn)
- Executar collectstatic
- Afegir CORS / seguretat (SECURE_* headers) si cal

## 📌 Roadmap suggerit
1. Model usuari + formulari registre / login
2. Pàgina base + navbar dinàmica (auth)
3. Gestió esdeveniments (app events/)
4. API REST (Django REST Framework)
5. Tests + cobertura
6. Deploy (Railway / Render / Docker)
7. WebSockets (chat / inscripcions en temps real)

## 🤝 Contribució
Branques:
- main (estable)
- feature/<nom>
- fix/<issue>

Commit prefix recomanat: feat, fix, docs, chore, test, refactor.

## 🧾 Llicència
(Indica la llicència aquí: MIT / Apache-2.0 / propietari)

## 🙋 Suport
Obre una issue o pregunta a l'equip docent.

---
Bon desenvolupament! 