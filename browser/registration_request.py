# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta

from five import grok
from zope.i18n import translate
from zope import interface
from zope.component import getMultiAdapter
from zope.event import notify
from zope.site.hooks import getSite

from z3c.form import button
from z3c.form import interfaces as forminterfaces
from plone.directives import form

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from example.util.mailer.events import MailEvent
from example.util.fridge.fridgemanager import IFridgeManager

from example.membership.interfaces import IRegistrator
from example.membership.interfaces import IRegistrationRequest
from example.membership import DOMAIN
from example.membership import _


FORM_ID = "registration"


class RequestRegistrationForm(form.SchemaForm):
    grok.name('request_registration')
    grok.require('zope2.View')
    grok.context(IRegistrator)

    schema = IRegistrationRequest
    ignoreContext = True
    id = "request_registration_form"
    label = _(u"request_registration_form_title")
    description = _(u"request_registration_form_description")

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)

    def updateWidgets(self):
        super(RequestRegistrationForm, self).updateWidgets()
        self.widgets['email'].addClass("email")
        self.widgets['email_repeat'].addClass("email")

    @button.buttonAndHandler(_(u"register_form_button"), name='submit')
    def handle_apply(self, action):
        data, errors = self.extractData()
        if errors:
            return

        portal = getSite()

        # create a new rand
        expires = datetime.now() + timedelta(days=2)
        data = {'email': data['email']}
        rand = IFridgeManager(self.context).add_entry(data, expires)

        # send mail to user
        mail_to = data['email']
        url = u"%s/%s/%s" % (self.context.absolute_url(), FORM_ID, rand)
        link = u'<a href="%s">%s</a>' % (url, url)
        message = translate(msgid=u'request_registration_mail_text',
                            domain=DOMAIN,
                            mapping={'link': link,
                                     'expires': expires.strftime('%d.%m.%Y %H:%M')},
                            context=self.request,
                            default=u'Finish your registration here ${link} by ${expires}.',
                            )
        mail_subject = translate(msgid="request_registration_mail_subject",
                                 domain=DOMAIN,
                                 context=self.request,
                                 default=u'Registration',
                                 )
        notify(MailEvent(message, mail_to, subject=mail_subject))

        IStatusMessage(self.request).add(_(u'request_registration_success_notification'),
                                        type='warn')
        return self._redirect()

    @button.buttonAndHandler(_(u'cancel_form_button'), name='cancel')
    def handle_cancel(self, action):
        IStatusMessage(self.request).add(_(u'request_registration_cancel_notification'),
                                        type='info')
        return self._redirect()
