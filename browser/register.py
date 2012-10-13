# -*- coding: utf-8 -*-
from zope.site.hooks import getSite
from Products.Five.browser import BrowserView


class RegisterView(BrowserView):

    def __call__(self):
        site = getSite()
        self.request.response.redirect(
            site.absolute_url() + '/registrator/request_registration')
