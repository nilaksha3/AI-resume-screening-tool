from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('candidate', _('Candidate')),
        ('hr-manager', _('HR Manager')),
    ]
    
    # Define role only once
    role = models.CharField(
        _('Role'), 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='candidate'
    )
    email = models.EmailField(unique=True)  # Ensure email is unique

    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = _('Custom User')
        verbose_name_plural = _('Custom Users')

    # Define __str__ method only once
    def __str__(self):
        return self.username or self.email
from django.db import models

class ResumeUpload(models.Model):
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='resumes/')
    position = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected

    def __str__(self):
        return self.file_name

# profile and edit profile 
# models.py - Updated Profile model

# models.py
from django.db import models
from django.conf import settings  # Import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Skill(models.Model):
    """Model representing a skill that can be associated with a user's profile."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Profile(models.Model):
    """Model extending the User model to include additional profile information."""
    ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('hr-manager', 'HR Manager'),
    ]
    
    # Change this line to use settings.AUTH_USER_MODEL
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name='profiles')
    
    def __str__(self):
        return f"{self.user.username}'s Profile ({self.role})"

# Also update the signal to use settings.AUTH_USER_MODEL
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # Save profile if it exists
    if hasattr(instance, 'profile'):
        instance.profile.save()
        
#@#########
from django.db import models

class Application(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=255)
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending")
    ats_score = models.IntegerField(null=True, blank=True)  # Optional ATS score

    def __str__(self):
        return f"{self.name} - {self.position} ({self.status})"
