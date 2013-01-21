from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from social_auth.models import UserSocialAuth


class Company(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(User)
    company = models.ForeignKey(Company, null=True)
    picture = models.ForeignKey(UserSocialAuth, null=True)
    title = models.CharField(max_length=255)
    blog = models.URLField()
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def company_choices(self):
        return Company.objects.filter(domain__in=self.domains)

    @property
    def domains(self):
        if self.user.email:
            return [get_domain(self.user.email)]


def get_domain(email):
    return email.split('@')[1]


@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    Company.objects.get_or_create(domain=get_domain(instance.email))
