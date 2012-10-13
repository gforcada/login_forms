# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import form
from z3c.form.interfaces import HIDDEN_MODE

from plone.z3cform.layout import wrap_form

from plone.autoform.form import AutoExtensibleForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from example.membership import _
from example.membership.interfaces import ILoginForm
from example.membership.browser.login_base import LoginBase


class LoginForm(AutoExtensibleForm, form.EditForm, LoginBase):
    schema = ILoginForm
    id = "login_form"
    ignoreContext = True
    label = _(u"login_form_title", default="Login")
    description = _(u"login_form_description")

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)

    def updateWidgets(self):
        super(LoginForm, self).updateWidgets()
        self.widgets['came_from'].mode = HIDDEN_MODE
        self.widgets['came_from'].value = self.came_from

    @button.buttonAndHandler(_(u'login_form_button'), name='submit')
    def handle_apply(self, action):
        data, errors = self.extractData()
        if not errors:
            plone_tools = getMultiAdapter((self.context, self.request),
                                          name=u'plone_tools')

            if 'came_from' in data.keys() and data['came_from']:
                self.request['came_from'] = data['came_from']

            plone_tools.membership().loginUser(self.request)
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            return self._redirect(
                target='%s/login_next?came_from=%s' %
                (portal_state.portal_url(), self.came_from))

    @button.buttonAndHandler(_(u'cancel_form_button'), name='cancel')
    def handle_cancel(self, action):
        data, errors = self.extractData()

        IStatusMessage(self.request).add(_(u'login_cancel_notification'),
                                        type='info')

        if 'came_from' in data.keys() and data['came_from']:
            self.redirect(data['came_from'])

        return self._redirect()


LoginFormView = wrap_form(LoginForm,
                          index=ViewPageTemplateFile('login_form.pt'))
