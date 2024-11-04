from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy
# Create your views here.

User = get_user_model()


class Index(ListView):
    model = Post
    paginate_by = 10
    queryset = Post.objects.select_related(
        'location', 'category', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    template_name = 'blog/index.html'


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'location', 'category', 'author'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        if self.request.user == self.object.author:
            post = get_object_or_404(
                self.get_queryset(),
                pk=pk
            )
        else:
            post = get_object_or_404(
                self.get_queryset(),
                pk=pk,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        comments = Comment.objects.filter(post=post)
        comment_count = comments.count()
        context['form'] = CommentForm()
        context['post'] = post
        context['comment_count'] = comment_count
        context['comments'] = comments
        return context


class CategoryPosts(ListView):
    model = Post  # изменить модель на Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.objects.select_related(
            'category', 'location'
        ).filter(
            category=category.pk,
            is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileDetail(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        posts = Post.objects.select_related(
            'category', 'location', 'author'
        ).filter(author=user)
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['profile'] = user
        return context


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    slug_field = 'username'
    slug_url_kwarg = 'username'
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object:
            return redirect('blog:profile', username=self.object.username)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=(self.object.username,))


def redirect_to_profile_update(request):
    username = request.user.username
    if not username:
        return redirect('login')
    redirect_url = reverse_lazy('blog:update-profile', args=(username,))
    return redirect(redirect_url)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        id = self.kwargs.get('pk')
        return reverse_lazy('blog:post_detail', args=(id,))


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=(self.request.user.username,))


class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=(self.kwargs.get('pk'),))


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=(self.kwargs.get('pk'),))

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=(self.kwargs.get('pk'),))

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=comment.post.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=(self.request.user.username,))

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)
