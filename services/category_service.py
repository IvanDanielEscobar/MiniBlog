from repositories.category_repository import CategoryRepository

class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    def list_categories(self):
        return self.repo.get_all()

    def create_category(self, name):
        if not name or name.strip() == "":
            raise ValueError("El nombre es obligatorio")
        return self.repo.create(name)

    def update_category(self, id, name):
        category = self.repo.get_by_id(id)

        if not name or name.strip() == "":
            raise ValueError("El nombre no puede estar vacío")

        return self.repo.update(category, name)

    def delete_category(self, id):
        category = self.repo.get_by_id(id)
        self.repo.delete(category)
        return True
