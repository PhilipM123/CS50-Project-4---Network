import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Follow, User, Post




def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj" : page_obj
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj" : page_obj
    })


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url='/login')
def newpost(request):

    new_post = Post.objects.create(
        content = request.POST['post-content'],
        user = request.user,
        timestamp = datetime.now()
        )
    new_post.save()

    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj" : page_obj
    })

def profile(request, id):
    target = User.objects.filter(id=id).first()
    followbutton = False
    followers = len(Follow.objects.filter(following = target))
    following = len(Follow.objects.filter(user = target))
    if request.user.is_authenticated:
        if Follow.objects.filter(user = request.user, following = target).first():
            followbutton = False
        else:
            followbutton = True

    posts = Post.objects.filter(user = target)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "target" : target,
        "followers" : followers,
        "following" : following,
        "page_obj" : page_obj,
        "followbtn" : followbutton
    })

@login_required(login_url='/login')
def follow(request, id):

    target = User.objects.filter(id=id).first()
    user = request.user
    already_followed = Follow.objects.filter(user = user, following = target).first()
    if user == target:
        posts = Post.objects.all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html", {
        "page_obj" : page_obj
        })
    elif already_followed:
        followbutton = False
        followers = int(Follow.objects.filter(following = target).count())
        following = int(Follow.objects.filter(user = target).count())
        posts = Post.objects.filter(user = target)
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/profile.html", {
        "target" : target,
        "followers" : followers,
        "following" : following,
        "page_obj" : page_obj,
        "followbtn" : followbutton
    })
    else:
        follow = Follow.objects.create(user = user, following = target)
        follow.save()

    followbutton = False
    followers = int(Follow.objects.filter(following = target).count())
    following = int(Follow.objects.filter(user = target).count())
    posts = Post.objects.filter(user = target)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "target" : target,
        "followers" : followers,
        "following" : following,
        "page_obj" : page_obj,
        "followbtn" : followbutton
    })

def unfollow(request, id):
    followbutton = True
    target = User.objects.filter(id=id).first()
    user = request.user
    Follow.objects.filter(user = user, following = target).delete()
        
    
    followers = int(Follow.objects.filter(following = target).count())
    following = int(Follow.objects.filter(user = target).count())
    posts = Post.objects.filter(user = target)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "target" : target,
        "followers" : followers,
        "following" : following,
        "page_obj" : page_obj,
        "followbtn" : followbutton
    })


@login_required(login_url='/login')
def following(request):
    user = request.user
    following_obj = Follow.objects.filter(user = user)
    posts = Post.objects.filter(user_id__in=following_obj.values('following_id')).order_by('-timestamp')
    
    #paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj" : page_obj
    })

def edit_post(request, id):
    
    post = Post.objects.get(id = id)

    if request.method == 'PUT':
        raw_content = json.loads(request.body)
        content = raw_content["content"]
        post.content = content
        post.save()
        print(post.content)
        return JsonResponse({
           "post" : post.serialize()
        })

    return JsonResponse({
        "error" : "POST request required"
    }, status=400)

def like_posts(request, id):
    if request.method == "PUT":
        user = User.objects.get(id=request.user.id)
        try:
            post = Post.objects.get(id=id)
            if user in post.likers.all():
                post.likers.remove(user)
                post.save()
            else:
                post.likers.add(user)
                post.save()
            return JsonResponse({
                "post": post.serialize()
            }, status=201)
        except Post.DoesNotExist:
            return HttpResponseNotFound(f"<h1>Post does not exist</h1>")
    else:
        return JsonResponse({
            "error" : "PUT request required"
        }, status=400)