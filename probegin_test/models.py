from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save_profile_update(sender, instance, created, *args, **kwargs):
    """Automatically creating profile for all newly created users.
    All users has to have at least one blog. Here we creating its
    first 'default' user blog.
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)


class BlogCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='blogs')
    title = models.CharField(max_length=254)
    description = models.TextField(max_length=1056, default='', blank=True)
    categories = models.ManyToManyField('BlogCategory', related_name='blogs')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog-detail', kwargs={'pk': self.pk})


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,
                             related_name='posts')
    title = models.CharField('Set the title of the post', max_length=254)
    content = models.TextField(max_length=1056)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog-post-list', kwargs={'blog_pk': self.blog.pk})


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    content = models.TextField(max_length=254)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'comment on post {}, created: {}'.format(self.post, self.created)

    def get_absolute_url(self):
        return reverse('post-comments', kwargs={'post_pk': self.post.pk})
