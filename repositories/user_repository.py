from models import User, db, UserCredentials

class UserRepository:

    def get_all(self):
        return User.query.all()

    def create(self, data):
        new_user = User(**data)
        db.session.add(new_user)
        db.session.flush()
        return new_user

    def get_by_id(self, id):
        return User.query.get(id)

    def update(self, user, data):
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    def delete(self, user):
        db.session.delete(user)
        db.session.commit()

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def create_credentials(self, user_id, password_hash, role):
        creds = UserCredentials(
            user_id=user_id,
            password_hash=password_hash,
            role=role
        )
        db.session.add(creds)
        db.session.commit()
        return creds
    
    def commit(self):
        db.session.commit()
