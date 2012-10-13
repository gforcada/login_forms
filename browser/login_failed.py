# -*- coding: utf-8 -*-
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from example.browser.login_form import LoginForm


LoginFailedView = wrap_form(
                    LoginForm,
                    index=ViewPageTemplateFile('login_failed.pt'))
