# -*- coding: utf-8 -*-
from datetime import datetime

from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from example..membership import _
from example.membership.browser.login_base import LoginBase


class LoginNextView(BrowserView, LoginBase):
    """Check if the user is logged in and redirect.
    """

    def __call__(self):
        self.login_next()

    def login_next(self):
        plone_tools = getMultiAdapter((self.context, self.request),
                                      name=u'plone_tools')

        # check if user is authenticated
        mtool = plone_tools.membership()
        if mtool.isAnonymousUser():
            self.request.RESPONSE.expireCookie('__ac', path='/')
            # redirect to login_failed with error message
            IStatusMessage(self.request).add(
                    _(u'login_failed_notification'),
                    type='error')
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            return self.request.RESPONSE.redirect(
                '%s/login_failed' % portal_state.portal_url())

        memberdata = mtool.getAuthenticatedMember()
        member_id = memberdata.getProperty('id')
        member = mtool.getMemberById(member_id).getHomeFolder()

        time = datetime.now()
        # Set last login time on member
        member.last_login = time

        # redirect with welcome message
        IStatusMessage(self.request).add(_(u'login_welcome_notification'),
                                         type='info')
        self.redirect(self.came_from)

    @property
    def portal_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.portal_url()
