from app import app, db
from models import Category

categorias_iniciales = ["Noticias", "Tecnología", "Deportes", "Entretenimiento", "Programacion", "Internacionales"]

with app.app_context():
    for nombre in categorias_iniciales:
        if not Category.query.filter_by(name=nombre).first():
            db.session.add(Category(name=nombre))

    db.session.commit()
    print("Categorías iniciales creadas correctamente")
