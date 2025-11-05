# IMPORTACIONS
from django.core.management.base import BaseCommand        # Per crear ordres personalitzades (python manage.py ...)
from django.contrib.auth.models import Group               # Model de grups (rols d'usuari)
from django.db import transaction                          # Permet agrupar operacions dins d'una transacció atòmica
from faker import Faker                                   # Generador de dades falses (noms, correus, etc.)
from django.contrib.auth import get_user_model            # Obté el model d'usuari actiu (personalitzat o per defecte)
from django.contrib.auth.hashers import make_password      # Per encriptar contrasenyes
import unicodedata, re                                    # Mòduls per netejar i normalitzar noms

# Guardem el model d'usuari a la variable User
User = get_user_model()


# CLASSE PRINCIPAL
class Command(BaseCommand):
    # Text d'ajuda que apareix quan s'executa "python manage.py <ordre> --help"
    help = "Genera usuaris de prova amb dades realistes per a StreamEvents"

    # ARGUMENTS
    def add_arguments(self, parser):
        # Argument --users: nombre d’usuaris a crear (per defecte 10)
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Nombre d'usuaris de prova a crear (default: 10)"
        )

        # Argument --clear: si s'afegeix, elimina els usuaris existents (excepte els superusuaris)
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina tots els usuaris existents excepte els superusuaris"
        )

        # Argument --with-follows: opció per a futures relacions de seguiment
        parser.add_argument(
            "--with-follows",
            action="store_true",
            help="Crea relacions de seguiment aleatòries entre usuaris"
        )


    # FUNCIÓ PRINCIPAL
    def handle(self, *args, **options):
        # Nombre d'usuaris que es crearan
        num_users = options["users"]

        # Si s'ha passat l'argument --clear, elimina tots els usuaris normals
        if options['clear']:
            self.stdout.write("🗑️  Eliminant usuaris existents...")
            count = 0
            for user in User.objects.all():
                if not user.is_superuser:  # No elimina el superusuari
                    user.delete()
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Eliminats {count} usuaris"))  # Mostra el nombre d'usuaris eliminats

        # Utilitzem una transacció per assegurar que tot es crea correctament
        with transaction.atomic():
            # Crear els grups (rols)
            groups = self.create_groups()
            # Crear el superusuari admin si no existeix
            self.create_admin(groups["Organitzadors"])
            # Crear usuaris falsos
            users_created = self.create_users(num_users, groups)

        # Missatge de confirmació final que indica el nombre d'usuaris creats
        self.stdout.write(self.style.SUCCESS(f"🎉 {num_users} usuaris creats correctament!"))
        
        # Missatge si s'ha inclòs l'opció --with-follows (encara pendent)
        if options["with_follows"]:
            self.stdout.write("👉 Funcionalitat de 'follows' pendent d'implementar")


    # FUNCIÓ PER CREAR ELS GRUPS
    def create_groups(self):
        group_names = ["Organitzadors", "Participants", "Moderadors"]  # Noms dels grups
        groups = {}  

        # Recorre els noms i crea els grups si no existeixen
        for name in group_names:
            group, _ = Group.objects.get_or_create(name=name)
            groups[name] = group

        return groups  # Retorna un diccionari amb els grups creats


    # FUNCIÓ PER CREAR EL SUPERUSUARI ADMIN
    def create_admin(self, org_group):
        # Si l'usuari "admin" no existeix, el crea
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create(
                username="admin",
                email="admin@streamevents.com",
                password=make_password("admin123"),  # Encriptem la contrasenya
                first_name="Admin",
                last_name="System",
                is_staff=True,        # Té accés al panell d'administració
                is_superuser=True,    # És superusuari
                is_active=True,       # Està actiu
                display_name="🔧 Administrador",
                bio="Superusuari principal",
                avatar="admin.png"
            )
            # Afegeix l'admin al grup d'Organitzadors
            admin.groups.add(org_group)
            self.stdout.write(self.style.SUCCESS("✔ Superusuari admin creat"))
        else:
            self.stdout.write("ℹ️ El superusuari admin ja existeix")


    # FUNCIÓ PER CREAR USUARIS FALSOS
    def create_users(self, num_users, groups):
        fake = Faker("es_ES")  # Generador amb dades en castellà (noms, correus…)

        for i in range(1, num_users + 1):
            # Genera noms falsos
            first_name = fake.first_name()
            last_name = fake.last_name()

            # Neteja i genera el nom d'usuari (sense accents, en minúscules, amb número)
            username = self.clean_username(f"{first_name}.{last_name}", i)
            email = f"{username}@streamevents.com"

            # Crea l'usuari
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password("password123"),
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_superuser=False,
                is_active=True,
                display_name=f"{first_name} {last_name}",
                bio=fake.sentence(),          # Frase aleatòria com a biografia
                avatar="default.png"          # Imatge de perfil per defecte
            )

            # Assigna el grup corresponent
            self.assign_group(user, i, groups)

            # Mostra un missatge de confirmació per consola
            self.stdout.write(self.style.SUCCESS(f"✔ Creat usuari: {username}"))


    # FUNCIÓ PER ASSIGNAR GRUPS SEGONS L’ÍNDEX
    def assign_group(self, user, index, groups):
        # Cada 5è usuari serà Organitzador
        if index % 5 == 0:
            user.groups.add(groups["Organitzadors"])
            user.display_name += " 🎯"
        # Cada 3r usuari serà Moderador
        elif index % 3 == 0:
            user.groups.add(groups["Moderadors"])
            user.display_name += " 🛡️"
        # La resta seran Participants
        else:
            user.groups.add(groups["Participants"])
            

    # --- FUNCIÓ PER NETEJAR I NORMALITZAR ELS NOM D'USUARI ---
    def clean_username(self, name: str, index: int) -> str:
        # Treu accents i caràcters especials (José → Jose)
        name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
        # Converteix tot a minúscules
        name = name.lower()
        # Substitueix tot el que no sigui lletra o número per punts
        name = re.sub(r'[^a-z0-9]+', '.', name).strip(".")
        # Afegeix un número per evitar duplicats (ex: maria.lopez1)
        return f"{name}{index}"