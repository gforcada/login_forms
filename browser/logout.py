# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from example.membership import _
from example.membership.browser.login_base import LoginBase


class LogoutView(BrowserView, LoginBase):
    """Logout the user and perform a redirect.
    """

    def __call__(self):
        context = aq_inner(self.context)
        membership_tool = getToolByName(context, 'portal_membership')
        portal_url_tool = getToolByName(self.context, 'portal_url')

        portal_url = portal_url_tool.portal_url()
        membership_tool.logoutUser(self.request)
        IStatusMessage(self.request).add(_(u'logout_notification'),
                                         type='info')
        self.request.response.expireCookie('__ac', path='/')
        return self.request.RESPONSE.redirect('%s/login' % portal_url)
