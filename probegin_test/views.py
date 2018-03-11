from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import prefetch_related_objects
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string, get_template
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse

from django_ajax.mixin import AJAXMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView
)

from probegin_test.forms import SignUpForm, CommentForm
from probegin_test.models import (
    User,
    Blog,
    BlogCategory,
    Post,
    Comment
)


class SignUp(FormView):
    template_name = 'probegin_test/sign_up.html'
    form_class = SignUpForm
    success_url = '/account_activation_sent/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        activation_link = self.send_activation_email(user)
        self.request.session['link'] = activation_link
        return super().form_valid(form)

    def send_activation_email(self, user):
        site = get_current_site(self.request)
        use_https = True if self.request.is_secure() else False

        context = {
            'domain': site.domain,
            'site_name': site.name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }

        subject = 'Account activation link for ProBegin test'
        template = get_template('probegin_test/account_activation_email.html')
        html_context = template.render(context)
        from_email = 'admin@probegin-test.com'
        msg = EmailMessage(subject, html_context, from_email, [user.email, ])
        msg.content_subtype = 'html'
        try:
            msg.send()
            # user.email_user(subject, message)
        except Exception as why:
            print(str(why))
            print('activation message: \n{}'.format(html_context))
        return '{}://{}/activate/{}/{}/'.format(
            context['protocol'], context['domain'],
            context['uid'], context['token'])


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as why:
        user, error = None, str(why)

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'account_activation_invalid.html', {'error': error})


class BlogDetail(DetailView):
    model = Blog
    context_object_name = 'blog'
    template_name = 'probegin_test/blog/blog_detail.html'

    def get_queryset(self):
        self.blog = get_object_or_404(Blog, id=self.kwargs.get('pk'))
        return Blog.objects.filter(id=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': self.blog.categories.all(),
            'posts': self.blog.posts.all(),
        })
        return context


class BlogList(ListView):
    model = Blog
    context_object_name = 'blog_list'
    queryset = Blog.objects.order_by('-created')
    template_name = 'probegin_test/blog/blog_list.html'


class UserBlogList(LoginRequiredMixin, ListView):
    model = Blog
    context_object_name = 'blog_list'
    queryset = Blog.objects.order_by('-created')
    template_name = 'probegin_test/blog/blog_list.html'

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user).order_by('-created')


class AuthorBlogList(ListView):
    model = Blog
    context_object_name = 'blog_list'
    queryset = Blog.objects.order_by('-created')
    template_name = 'probegin_test/blog/blog_list.html'

    def get_queryset(self):
        return Blog.objects.filter(author=self.kwargs.get('author_id')).order_by('-created')


class BlogCreate(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'description', 'categories']
    template_name = 'probegin_test/blog/blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdate(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['title', 'description', 'categories']
    template_name = 'probegin_test/blog/blog_form.html'

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this blog to change it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)


class BlogDelete(LoginRequiredMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog-list')
    template_name = 'probegin_test/blog/blog_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'back_url': self.request.META.get('HTTP_REFERER', '/'),
        })
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this blog to delete it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)


class BlogCategories(ListView):
    model = BlogCategory
    context_object_name = 'category_list'
    queryset = BlogCategory.objects.all()
    template_name = 'probegin_test/blog/blog_categories_list.html'


class BlogCategoryList(ListView):
    model = Blog
    context_object_name = 'blog_list'
    queryset = Blog.objects.order_by('-created')
    template_name = 'probegin_test/blog/blog_list.html'

    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, id=self.kwargs.get('category_pk'))
        return self.category.blogs.all()


class UserPostList(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'post_list'
    queryset = Post.objects.order_by('-blog', '-created')
    template_name = 'probegin_test/post/post_list.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class BlogPostList(ListView):
    model = Post
    context_object_name = 'post_list'
    queryset = Post.objects.order_by('-created')
    template_name = 'probegin_test/post/post_list.html'

    def get_queryset(self):
        self.blog = get_object_or_404(Blog, id=self.kwargs.get('blog_pk'))
        return self.blog.posts.all()

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'blog': self.blog,
        })
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['blog', 'title', 'content']
    template_name = 'probegin_test/post/post_form.html'

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields['blog'].queryset = Blog.objects.filter(author=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['blog', 'title', 'content']
    template_name = 'probegin_test/post/change_form.html'

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields['blog'].queryset = Blog.objects.filter(author=self.request.user)
        return form

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this post to change it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    context_object_name = 'post'
    success_url = reverse_lazy('post-list')
    template_name = 'probegin_test/post/post_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'back_url': self.request.META.get('HTTP_REFERER', '/'),
        })
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this post to delete it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)


class PostCommentsList(ListView):
    model = Comment
    context_object_name = 'comments_list'
    queryset = Comment.objects.all().order_by('-created')
    template_name = 'probegin_test/comment/comment_list.html'

    def get_queryset(self):
        self.post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))
        return self.post.comments.all().order_by('-created')

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'post': self.post,
            'form': CommentForm(),
        })
        return context


class CommentCreate(LoginRequiredMixin, AJAXMixin, TemplateView):

    def post(self, request):
        post = get_object_or_404(Post, id=request.POST.get('post_id'))
        comment = Comment(
            author=request.user, post=post,
            content=request.POST.get('content'))
        comment.save()
        return {
            'append-fragments': {
                '#comments': render(
                    request, 'probegin_test/comment/comment.html',
                    {'comment': comment}).content.decode().replace('\n', ''),
            },
        }


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['content']
    context_object_name = 'comment'
    template_name = 'probegin_test/comment/change_form.html'

    def get_context_data(self, **kwargs):
        self.post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))
        context = super().get_context_data(**kwargs)
        context.update({
            'post': self.post
        })
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this comment to change it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    context_object_name = 'comment'
    success_url = reverse_lazy('post-comments')
    template_name = 'probegin_test/comment/comment_confirm_delete.html.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'back_url': self.request.META.get('HTTP_REFERER', '/'),
        })
        return context

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            context = {
                'message': 'your are not the author of this post to delete it!'
            }
            return render(request, 'probegin_test/access_forbidden.html', context)
        else:
            return super().get(request, *args, **kwargs)
