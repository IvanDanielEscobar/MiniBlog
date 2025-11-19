from repositories.post_repository import PostRepository
from models import Post

repo = PostRepository()

class PostService:
    def __init__(self):
        self.repo = PostRepository()

    # -------- listar --------
    def list_posts(self):
        posts = self.repo.get_all_active()

        result = []
        for post in posts:
            result.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author.name,
                "user_id": post.user_id,
                "genres": [g.name for g in post.genres],
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
                "comments": [
                    {
                        "id": c.id,
                        "content": c.content,
                        "user_id": c.user_id,
                        "author": c.author.name,
                        "created_at": c.created_at
                    } 
                    for c in post.comments if c.is_visible
                ]
            })
        return result

    # -------- crear --------
    def create_post(self, user_id, data):
        if not data.get("title") or not data.get("content"):
            raise ValueError("title y content son obligatorios")

        post = self.repo.create({
            "title": data["title"],
            "content": data["content"],
            "user_id": user_id
        })

        try:
            self.repo.commit()
        except:
            self.repo.rollback()
            raise ValueError("Error al crear el post")

        return post
    
    def update_post(self, post, data):
        return repo.update(post, data.get("title"), data.get("content"))

    def delete_post(self, post):
        repo.logical_delete(post)