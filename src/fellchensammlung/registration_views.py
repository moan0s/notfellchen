from django.utils.html import strip_tags
from django_registration.backends.activation.views import RegistrationView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


class HTMLMailRegistrationView(RegistrationView):
    def send_activation_email(self, user):
        """
        overwrites the function in django registration
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context["user"] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request,
        )
        # Force subject to a single line to avoid header-injection issues.
        subject = "".join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request,
        )
        plain_message = strip_tags(message)
        user.email_user(subject, plain_message, settings.DEFAULT_FROM_EMAIL, html_message=message)
