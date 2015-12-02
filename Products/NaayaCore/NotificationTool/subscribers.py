from datetime import timedelta

from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from naaya.core.zope2util import path_in_site

import constants
import utils
from interfaces import ISubscriptionContainer

csv_email_template = EmailPageTemplateFile('emailpt/csv_import.zpt', globals())
zip_email_template = EmailPageTemplateFile('emailpt/zip_import.zpt', globals())

def check_skip_notifications(subscriber):
    def wrapper(event):
        """This session key will be set for admins that don't want to notify
        users with their bulk modifications updates.
        Also check if the object is approved.

        """

        if (hasattr(event.context, 'REQUEST') and
            hasattr(event.context.REQUEST, 'SESSION') and
            event.context.REQUEST.SESSION.get('skip_notifications', False) is
            True):
            return
        return subscriber(event)
    return wrapper

@check_skip_notifications
def handle_object_approved(event):
    """ Called when an object has been approved """

    if not event._send_notifications:
        return

    ob = event.context
    portal = ob.getSite()
    contributor = event.contributor
    notification_tool = portal.getNotificationTool()

    notification_tool.notify_administrative(ob, contributor)
    notification_tool.notify_maintainer(ob, ob.aq_parent, contributor=contributor)
    notification_tool.notify_instant(ob, contributor)

    action_logger = portal.getActionLogger()
    action_logger.create(type=constants.LOG_TYPES['approved'],
                         contributor=contributor, path=path_in_site(ob))

@check_skip_notifications
def handle_object_add(event):
    """An object has been created. Create a log entry.
    Notifications to subscribers are only sent in object-approved handler.
    Administrative notifications are only sent if the object is not approved.
    If it is already approved, then notifications were already sent in the
    object-approved handler.
    """

    if not event.schema.get('_send_notifications', True):
        return

    ob = event.context
    portal = ob.getSite()
    contributor = event.contributor

    if not ob.approved:
        notification_tool = portal.getNotificationTool()
        notification_tool.notify_administrative(ob, contributor)
        notification_tool.notify_maintainer(ob, ob.aq_parent,
            contributor=contributor)

    if ob.approved:
        #Create log entry
        action_logger = portal.getActionLogger()
        action_logger.create(type=constants.LOG_TYPES['created'],
                             contributor=contributor, path=path_in_site(ob))

@check_skip_notifications
def handle_object_edit(event):
    """An object has been modified. Send instant notifications and create a log
    entry if the object is approved

    """
    ob = event.context
    portal = ob.getSite()
    contributor = event.contributor
    notification_tool = portal.getNotificationTool()

    notification_tool.notify_administrative(ob, contributor, ob_edited=True)
    notification_tool.notify_maintainer(ob, ob.aq_parent,
        contributor=contributor, ob_edited=True)

    if ob.approved: #Create log entry
        notification_tool.notify_instant(ob, contributor, ob_edited=True)
        action_logger = portal.getActionLogger()
        action_logger.create(type=constants.LOG_TYPES['modified'],
                             contributor=contributor, path=path_in_site(ob))

@check_skip_notifications
def handle_comment_added(event):
    """An comment has been added to an object. Send notifications and
    create a log entry

    """
    ob = event.context
    parent_ob = event.parent_ob
    portal = parent_ob.getSite()
    contributor = event.contributor
    notification_tool = portal.getNotificationTool()

    notification_tool.notify_comment_administrative(ob, parent_ob, contributor)
    notification_tool.notify_comment_maintainer(ob, parent_ob,
        contributor=contributor)
    notification_tool.notify_comment_instant(ob, parent_ob, contributor)

    action_logger = portal.getActionLogger()
    action_logger.create(type=constants.LOG_TYPES['commented'],
                         contributor=contributor, path=path_in_site(parent_ob))

@check_skip_notifications
def handle_csv_import(event):
    """ Send instant notification when a csv is imported to a folder"""

    portal = event.context.getSite()
    obj_titles = [event.context[oid].title_or_id() for oid in event.ids]

    subscriber_data_default = {
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'obj_titles': obj_titles,
        'item_count': len(obj_titles),
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate()),
    }

    send_notifications_for_event(event, subscriber_data_default,
                                 csv_email_template)

@check_skip_notifications
def handle_zip_import(event):
    """Send instant notification when an zip is imported to a folder"""

    portal = event.context.getSite()
    subscriber_data_default = {
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'zip_contents': event.zip_contents,
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate())
    }

    send_notifications_for_event(event, subscriber_data_default,
                                 zip_email_template)


def change_user_roles(event):
    """Update subscriptions when a user's roles were updated:
       If he now gets the Administrator role, he should be subscribed
       to administrative notifications. If he loses the role, his subscription
       should be revoked"""

    notif_tool = event.context.getNotificationTool()
    portal = event.context.getSite()
    if 'Administrator' in event.assigned:
        if not utils.match_account_subscription(ISubscriptionContainer(event.context),
                                    event.user_id, 'administrative', 'en'):
            notif_tool.add_account_subscription(event.user_id,
                path_in_site(event.context), 'administrative', 'en', [])
    if 'Administrator' in event.unassigned:
        if utils.match_account_subscription(ISubscriptionContainer(event.context),
                                    event.user_id, 'administrative', 'en'):
            notif_tool.remove_account_subscription(event.user_id,
                path_in_site(event.context), 'administrative', 'en')

def send_notifications_for_event(event, subscriber_data_default, template):
    """Send notifications to site maintainers and subscribers. Create event
    handler must be supressed when this action is run.

    """

    folder = event.context
    portal = folder.getSite()
    notification_tool = portal.getNotificationTool()
    action_logger = portal.getActionLogger()

    subscribers_data = {}
    maintainers_data = {}

    #Get maintainers
    maintainers = portal.getMaintainersEmails(folder)
    for email in maintainers:
        data = dict(subscriber_data_default)
        data.update({
            'ob': folder,
            'here': notification_tool,
        })
        maintainers_data[email] = data

    #Get subscribers
    if notification_tool.config['enable_instant'] is True:
        subscribers_data = utils.get_subscribers_data(notification_tool,
            folder, **subscriber_data_default)

    subscribers_data.update(maintainers_data)
    notification_tool._send_notifications(subscribers_data,
                                          template.render_email)
    #Create log entry
    action_logger.create(type=constants.LOG_TYPES['bulk_import'],
                         path=path_in_site(folder))

def heartbeat_notification(site, heartbeat):
    """notifications are delayed by 1 minute to allow for non-committed
    transactions (otherwise there's a remote chance that objects added
    or changed when heartbeat runs would be missed)"""

    when = heartbeat.when - timedelta(minutes=1)
    site.getNotificationTool()._cron_heartbeat(when)
