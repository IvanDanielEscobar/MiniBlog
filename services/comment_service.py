from repositories.comment_repository import CommentRepository

repo = CommentRepository()

class CommentService:

    def list_comments(self, post_id):
        post = repo.get_post_or_404(post_id)
        comments = repo.list_visible_by_post(post)

        return [
            {
                "id": c.id,
                "content": c.content,
                "author": c.author.name,
                "user_id": c.user_id,
                "created_at": c.created_at
            }
            for c in comments
        ]

    def create_comment(self, post_id, user_id, content):
        comment = repo.create(content, user_id, post_id)

        return {
            "id": comment.id,
            "content": comment.content,
            "author": comment.author.name,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "created_at": comment.created_at
        }

    def update_comment(self, comment_id, new_content):
        comment = repo.get_comment_or_404(comment_id)
        return repo.update(comment, new_content)

    def delete_comment(self, comment_id):
        comment = repo.get_comment_or_404(comment_id)
        repo.logical_delete(comment)
        return comment
