# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class LoginBase(object):
    """Helper methods for login process.
    """
    @property
    def portal_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()

    @property
    def portal(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.context

    @property
    def came_from(self):
        referrer = self.request.get('HTTP_REFERER', self.portal_url)
        return self.request.get('came_from', referrer)

    def redirect(self, came_from):
        plone_utils = getToolByName(self.context, 'plone_utils')
        portal_url = getToolByName(self.context, 'portal_url')
        scheme, location, path, parameters, query, fragment = \
            plone_utils.urlparse(came_from)
        template_id = path.split('/')[-1]
        # We need localhost in the list, or Five.testbrowser tests won't be
        # able to log in via login_form (since r17128).
        template_list = ['login', 'login_success', 'login_password',
                         'login_failed', 'login_form', 'logged_in',
                         'logged_out', 'registered', 'mail_password',
                         'mail_password_form', 'register', 'require_login',
                         'member_search_results', 'pwreset_finish',
                         'localhost']
        if template_id in template_list:
            came_from = ''

        if came_from and portal_url.isURLInPortal(came_from):
            return self.request.RESPONSE.redirect(came_from)
        return self.request.RESPONSE.redirect(self.portal_url)
