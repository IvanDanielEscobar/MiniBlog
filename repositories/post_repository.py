from models import Post, db

class PostRepository:
    def get_all_active(self):
        return Post.query.filter_by(is_active=True).order_by(Post.id.desc()).all()

    def create(self, data):
        post = Post(**data)
        db.session.add(post)
        db.session.flush()
        return post

    def get_by_id(self, id):
        return Post.query.get(id)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def update(self, post, title=None, content=None):
        if title:
            post.title = title
        if content:
            post.content = content
        db.session.commit()
        return post

    def logical_delete(self, post):
        post.is_active = False
        db.session.commit()