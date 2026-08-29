from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from cards.models import KnowledgeCard

from .forms import ProfileForm, ProfileUserForm, SignUpForm
from .models import get_or_create_profile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_or_create_profile(user)
            # Sign the person straight in - a hackathon demo shouldn't make
            # someone fill in a login form immediately after a signup form.
            login(request, user)
            messages.success(request, f"Welcome to MonGoats, {user.username}!")
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)

    if request.method == "POST":
        user_form = ProfileUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        user_form = ProfileUserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    your_cards = KnowledgeCard.objects.filter(owner=request.user)

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "user_form": user_form,
            "profile_form": profile_form,
            "your_cards": your_cards,
        },
    )
