from models import Category, db

class CategoryRepository:

    def get_all(self):
        return Category.query.all()

    def get_by_id(self, id):
        return Category.query.get_or_404(id)

    def create(self, name):
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category, name):
        category.name = name
        db.session.commit()
        return category

    def delete(self, category):
        db.session.delete(category)
        db.session.commit()
