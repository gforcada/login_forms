# -*- coding: utf-8 -*-
import re
from zope import interface
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.site.hooks import getSite
from zope.component import getMultiAdapter
from five import grok
from z3c.form import button
from z3c.form import interfaces as forminterfaces
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget

from plone.directives import form

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from example.util.fridge.fridgemanager import IFridgeManager
from example.util.fridge.browser.fridge import FridgeForm

from example.membership import _
from example.membership.interfaces import IRegistration
from example.membership.interfaces import IRegistrator


class ProfileRegistrationForm(form.SchemaForm, FridgeForm):
    grok.name('registration')
    grok.require('zope2.View')
    grok.context(IRegistrator)

    schema = IRegistration

    ignoreContext = True
    id = "ProfileRegistrationForm"
    label = _(u"profile_registration_form_title")
    description = _(u"profile_registration_form_description")

    def __init__(self, context, request):
        super(ProfileRegistrationForm, self).__init__(context, request)

        portal_state = getMultiAdapter((context, request),
                                       name=u'plone_portal_state')
        self.schema['accept_terms'].description = \
            _(u"accept_link_form_help",
            mapping={'link': '%s/agb' % portal_state.portal_url()})

    def _redirect(self, target=''):
        if not target:
            portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
            target = portal_state.portal_url()
        self.request.response.redirect(target)

    @button.buttonAndHandler(_(u"save_profile_form_button"), name='submit')
    def handle_apply(self, action):
        data, errors = self.extractData()

        if errors:
            return

        fridgemanager = IFridgeManager(self.context)
        user_data = fridgemanager.get_entry_payload(data['fridge_rand'])

        if user_data is not None:
            # Testing uniqueness of username
            portal = getSite()
            pas_tool = getToolByName(portal, 'acl_users')
            members = pas_tool.getUserById(data['username'])
            if members is not None:
                raise forminterfaces.WidgetActionExecutionError(
                    'username',
                    interface.Invalid(_(u"username_invalid_error")))

            # Add member: We store username, password and email-address in the
            # default Plone member profile. All other member properties
            # (description, location, home_page, newsletter, etc.) are stored in
            # the Dexterity-based memberfolder.
            roles = []
            domains = []

            mtool = getToolByName(portal, 'portal_membership')
            password = data['password']
            if isinstance(password, unicode):
                password = password.encode('utf-8')
            mtool.addMember(data['username'], password,
                                      roles, domains)
            mtool.createMemberarea(data['username'])
            membersfolder = mtool.getMembersFolder()

            memberfolder = membersfolder[data['username']]
            memberfolder.title = data['fullname']
            memberfolder.description = data['description']
            memberfolder.location = data['location']
            memberfolder.home_page = data['home_page']
            memberfolder.portrait = data['portrait']
            memberfolder.newsletter = data['newsletter']

            memberfolder.email = user_data['email']

            notify(ObjectModifiedEvent(memberfolder))
            memberfolder.reindexObject()

            # Remove the fridge entry
            fridgemanager.delete_entry(data['fridge_rand'])

            # Log the new member in
            pas_tool.session._setupSession(data['username'].encode("utf-8"),
                                           self.request.RESPONSE)

            IStatusMessage(self.request).add(_(u'profile_registration_success_notification',
                                               default="Registration success"),
                                            type='info')
        else:
            IStatusMessage(self.request).add(_(u'profile_registration_expired_or_invalid_notification'),
                                             type='error')

        return self._redirect()

    @button.buttonAndHandler(_(u'cancel_form_button'), name='cancel')
    def handle_cancel(self, action):
        IStatusMessage(self.request).add(_(u'profile_registration_cancel_notification'),
                                        type='info')
        return self._redirect()

    def updateFields(self):
        super(ProfileRegistrationForm, self).updateFields()
        self.fields['newsletter'].widgetFactory = \
            SingleCheckBoxFieldWidget
        self.fields['accept_terms'].widgetFactory = \
            SingleCheckBoxFieldWidget

    def updateWidgets(self):
        super(ProfileRegistrationForm, self).updateWidgets()
        self.widgets['home_page'].addClass("url")


class UsernameAvailable(BrowserView):

    def __call__(self):
        portal = getSite()
        if 'form.widgets.username' in self.request.form:
            username = self.request.form['form.widgets.username']

            # check that the name is a valid identifier
            regex = re.compile(r'^[\-a-z0-9]{1,30}$')
            if regex.search(username) is None:
                return "false"

            # check that the id is available
            pas_tool = getToolByName(portal, 'acl_users')
            members = pas_tool.getUserById(username)
            if members is not None:
                return "false"

        return "true"
