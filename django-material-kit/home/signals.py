from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import *
from django.contrib.auth.models import User

@receiver(m2m_changed, sender=User.groups.through)
def update_user_profile(sender, instance, action, *args, **kwargs):
    grupo_tecnico = Group.objects.get(name='Encargados de logística')
    grupo_policial = Group.objects.get(name='Personal policial agentes')

    if action == 'post_add':
        try:
            user_profile = Usuario.objects.get(user=instance)
        except Usuario.DoesNotExist:
            return

        if grupo_tecnico in instance.groups.all():
            Tecnico.objects.update_or_create(usuario=user_profile, defaults={'is_deleted': False})
            instance.is_staff = True
            instance.save()

        if grupo_policial in instance.groups.all():
            PersonalPolicial.objects.update_or_create(usuario=user_profile, defaults={'is_deleted': False})
            instance.is_staff = False
            instance.save()

    elif action == 'post_remove':
        try:
            user_profile = Usuario.objects.get(user=instance)
        except Usuario.DoesNotExist:
            return

        if grupo_tecnico not in instance.groups.all():
            Tecnico.objects.filter(usuario=user_profile).update(is_deleted=True)
            if grupo_policial in instance.groups.all():
                instance.is_staff = False
                instance.save()

        if grupo_policial not in instance.groups.all():
            PersonalPolicial.objects.filter(usuario=user_profile).update(is_deleted=True)
            if grupo_tecnico in instance.groups.all():
                instance.is_staff = True
                instance.save()
                
        if grupo_policial not in instance.groups.all() and grupo_tecnico not in instance.groups.all():
            user_profile.is_deleted = True
            user_profile.save()