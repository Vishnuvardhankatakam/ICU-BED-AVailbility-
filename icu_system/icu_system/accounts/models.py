from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Using Django's built-in User model
# This file is intentionally minimal as we're using Django's built-in User model
# for authentication and user management
