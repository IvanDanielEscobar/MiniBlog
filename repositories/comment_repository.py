from models import Comment, Post, User, db

class CommentRepository:

    def get_post_or_404(self, post_id):
        return Post.query.get_or_404(post_id)

    def get_comment_or_404(self, comment_id):
        return Comment.query.get_or_404(comment_id)

    def list_visible_by_post(self, post):
        return [
            c for c in post.comments if c.is_visible
        ]

    def create(self, content, user_id, post_id):
        comment = Comment(
            content=content,
            user_id=user_id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    def update(self, comment, content):
        comment.content = content
        db.session.commit()
        return comment

    def logical_delete(self, comment):
        comment.is_visible = False
        db.session.commit()
