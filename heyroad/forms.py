from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Route, Friendship

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FriendshipInviteForm(forms.Form):
    invited_username = forms.CharField(label="Friend's username",
                                       max_length=150)

# class FriendshipForm(forms.ModelForm):

#     class Meta:
#         model = Friendship
#         fields = ['user1', 'user2', 'is_accepted']