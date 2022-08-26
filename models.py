from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=150)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    likers = models.ManyToManyField("User", related_name="liked_posts")

    class Meta:
        ordering = ('-timestamp',)

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": self.likers.count(),
            "likers": [u.username for u in self.likers.all()]
        }


class Follow(models.Model):
    # The user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='follower')
    # Who they are following
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='following')

    class Meta:
        unique_together = ('user', 'following')