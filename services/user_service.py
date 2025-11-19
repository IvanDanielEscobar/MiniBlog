from repositories.user_repository import UserRepository
from flask_jwt_extended import create_access_token, create_refresh_token
from passlib.hash import bcrypt
from models import User

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def list_users(self):
        return self.repo.get_all()

    # ------------ crear ------------
    def create_user(self, data):
        # Validar email 
        if self.repo.get_by_email(data["email"]):
            raise ValueError("El email ya está registrado")

        # crear usuario 
        new_user = self.repo.create(data)

        # commit final
        self.repo.commit()

        return new_user

    # ------------ traer ------------
    def get_user(self, id):
        user = self.repo.get_by_id(id)
        if not user:
            raise ValueError("Usuario no encontrado")
        return user

    # ------------ actualizar ------------
    def update_user(self, id, data):
        user = self.get_user(id)

        # Verificar email en uso
        if "email" in data:
            email_exist = User.query.filter(
                User.email == data["email"],
                User.id != id
            ).first()
            if email_exist:
                raise ValueError("El email ya está en uso por otro usuario")

        # actualizar en el repo
        updated_user = self.repo.update(user, data)
        return updated_user

    # ------------ eliminar ------------
    def delete_user(self, id):
        user = self.get_user(id)
        self.repo.delete(user)
        return True
    
class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def register(self, data):
        if self.repo.get_by_email(data["email"]):
            raise ValueError("Email en uso")

        role = data.get("role", "user")

        # Crear usuario
        new_user = self.repo.create({
            "name": data["name"],
            "email": data["email"]
        })

        password_hash = bcrypt.hash(data["password"])

        # Crear credenciales 
        self.repo.create_credentials(
            user_id=new_user.id,
            password_hash=password_hash,
            role=role
        )

        # Commit 
        self.repo.commit()
        return new_user

    # -------- login --------
    def login(self, email, password):
        user = self.repo.get_by_email(email)

        if not user or not user.credential:
            raise ValueError("Credenciales inválidas")

        if not bcrypt.verify(password, user.credential.password_hash):
            raise ValueError("Credenciales inválidas")

        identity = str(user.id)
        claims = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.credential.role
        }

        access_token = create_access_token(identity=identity, additional_claims=claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=claims)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": claims
        }