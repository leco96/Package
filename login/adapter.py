from allauth.account.adapter import DefaultAccountAdapter


class CustomDefaultAdapter(DefaultAccountAdapter):
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = 'wwww.prueba.com'
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": 'www.dirección-ejemplo.com',
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        if signup:
            pass
            email_template = './prueba'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)