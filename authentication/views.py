import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.contrib import messages

from .forms import SignUpForm, ProfilePictureForm, UserUpdateForm, ProfileUpdateForm
from .models import DatabaseConfiguration, EmailConfiguration, VerificationCode, Person


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            request.session['user_email'] = user.email

            send_code(user)

            return redirect('verify_code')
    else:
        form = SignUpForm()

    return render(request, 'Sign_Up.html', {'form': form})


@csrf_protect
def verify_code(request):
    if request.method == 'POST':
        if 'resend' in request.POST:
            user_email = request.session.get('user_email')

            if user_email:
                user = Person.objects.filter(email=user_email).first()

                if user:
                    verification_code = VerificationCode.objects.filter(user=user).last()
                    if verification_code:
                        verification_code.delete()

                    send_code(user)

                    messages.success(request, 'A new verification code has been sent to your email.')
                else:
                    messages.error(request, 'No user email found.')

            return render(request, 'Verify_Code.html')

        else:
            entered_code = request.POST.get('code')

            if not entered_code:
                messages.error(request, 'Please enter a verification code.')
                return render(request, 'Verify_Code.html')

            verification_code = VerificationCode.objects.filter(code=entered_code).last()

            if verification_code is None:
                messages.error(request, 'Invalid verification code.')
                return render(request, 'Verify_Code.html')

            if verification_code.expired():
                verification_code.delete()
                messages.error(request, 'Verification code has expired.')
                return render(request, 'Verify_Code.html')

            user = verification_code.user
            verification_code.delete()
            user.is_active = True
            user.save()

            request.session.pop('user_email', None)

            messages.success(request, 'Your account has been verified successfully.')
            return redirect('signin')

    return render(request, 'Verify_Code.html')


def send_code(user):
    code = get_random_string(length=6)
    VerificationCode.objects.create(user=user, code=code)
    send_mail(
        'Verification Code',
        f'Your new verification code is: {code}',
        'EMAIL_HOST_USER',
        [user.email],
        fail_silently=False,
    )


@csrf_protect
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('account_page')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'Sign_In.html')


@login_required
def account_page(request):
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user)
    picture_form = ProfilePictureForm(instance=request.user)

    if request.method == 'POST':
        if 'logout' in request.POST:
            logout(request)
            return redirect('signin')
        elif 'save_account' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('account_page')
        elif 'save_personal' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('account_page')
        elif 'profile_picture' in request.FILES:
            picture_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
            if picture_form.is_valid():
                picture_form.save()
                return redirect('account_page')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'picture_form': picture_form
    }

    return render(request, 'account_page.html', context)


@receiver(post_save, sender=DatabaseConfiguration)
def update_env_file(instance, **kwargs):
    env_file_path = os.path.join(settings.BASE_DIR, '.env')
    with open(env_file_path, 'r') as env_file:
        lines = env_file.readlines()

    with open(env_file_path, 'w') as env_file:
        for line in lines:
            key = line.split('=')[0]
            if key in ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']:
                env_file.write(f"{key}={getattr(instance, key.lower(), '')}\n")
            else:
                env_file.write(line)


@receiver(post_save, sender=EmailConfiguration)
def update_env_file(instance, **kwargs):
    env_file_path = os.path.join(settings.BASE_DIR, '.env')
    with open(env_file_path, 'r') as env_file:
        lines = env_file.readlines()

    with open(env_file_path, 'w') as env_file:
        for line in lines:
            key = line.split('=')[0]
            if key in ['EMAIL_BACKEND', 'EMAIL_HOST',
                       'EMAIL_PORT', 'EMAIL_USE_TLS', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']:
                env_file.write(f"{key}={getattr(instance, key.lower(), '')}\n")
            else:
                env_file.write(line)
