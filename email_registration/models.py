from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


class Registration(models.Model):
    sent_on = models.DateTimeField(_('sent on'), default=timezone.now)
    code = models.CharField(_('code'), max_length=40, unique=True)
    email = models.EmailField(_('e-mail address'), unique=True)
    user = models.ForeignKey(User, verbose_name=_('user'),
        blank=True, null=True)

    class Meta:
        verbose_name = _('registration')
        verbose_name_plural = _('registrations')

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(40)
        super(Registration, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('email_registration_confirm', (), {'code': self.code})

    def send_mail(self, request):
        self.sent_on = timezone.now()
        self.save()

        lines = render_to_string('registration/email_registration_email.txt', {
            'registration': self,
            'url': request.build_absolute_uri(self.get_absolute_url()),
            }).splitlines()

        message = EmailMultiAlternatives(
            subject=lines[0],
            body=u'\n'.join(lines[2:]),
            to=[self.email],
            headers={
                #'Reply-To': 'TODO something sane',
                },
            )
        message.send()
