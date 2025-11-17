from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def get_admin_emails():
    """Get list of admin email addresses"""
    return list(User.objects.filter(is_staff=True).values_list('email', flat=True))

def send_notification(subject, template_name, context, recipient_list):
    """Send email notification using a template"""
    html_message = render_to_string(template_name, context)
    
    return send_mail(
        subject=subject,
        message='', # Empty plain text message
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False
    )

def notify_new_user_registration(user):
    """Notify admins about new user registration"""
    admin_emails = get_admin_emails()
    if not admin_emails:
        return
    # Derive a friendly name from the user object in a safe way
    try:
        # Many Django user models have get_full_name()
        name = user.get_full_name() or ''
    except Exception:
        name = ''
    if not name:
        name = getattr(user, 'first_name', '') or getattr(user, 'username', '') or getattr(user, 'email', '')

    context = {
        'user': user,
        'name': name,
    }
    
    # Send to admins
    send_notification(
        subject='New User Registration',
        template_name='emails/admin_new_user_notification.html',
        context=context,
        recipient_list=admin_emails
    )

def notify_new_request(request_obj):
    """Notify about new laundry request"""
    admin_emails = get_admin_emails()
    
    context = {
        'request': request_obj,
        'customer_name': request_obj.customer_name,
        'items': request_obj.items_description,
        'address': request_obj.address,
    }
    
    # Notify customer (email is stored on the related user)
    customer_email = None
    try:
        customer_email = getattr(request_obj.customer, 'email', None)
    except Exception:
        customer_email = None
    if customer_email:
        # Log who will receive the customer notification for traceability
        try:
            logger.info(
                f"notify_new_request: sending customer email '{customer_email}' for request id={request_obj.id} customer_id={request_obj.customer.id}"
            )
        except Exception:
            logger.info(f"notify_new_request: sending customer email '{customer_email}'")
        send_notification(
            subject='Your Laundry Request Has Been Received',
            template_name='emails/customer_new_request.html',
            context=context,
            recipient_list=[customer_email]
        )
    
    # Notify admins
    if admin_emails:
        send_notification(
            subject='New Laundry Request Received',
            template_name='emails/admin_new_request.html',
            context=context,
            recipient_list=admin_emails
        )

def notify_request_status_update(request_obj, old_status=None):
    """Notify about request status changes"""
    context = {
        'request': request_obj,
        'customer_name': request_obj.customer_name,
        'old_status': old_status,
        'new_status': request_obj.status,
        'items': request_obj.items_description,
    }
    
    recipients = []
    # Customer email
    try:
        cust_email = getattr(request_obj.customer, 'email', None)
    except Exception:
        cust_email = None
    if cust_email:
        try:
            logger.info(f"notify_request_status_update: will notify customer '{cust_email}' for request id={request_obj.id}")
        except Exception:
            logger.info(f"notify_request_status_update: will notify customer '{cust_email}'")
        recipients.append(cust_email)

    # Driver email (driver model links to a user)
    driver_email = None
    if request_obj.driver:
        try:
            driver_user = getattr(request_obj.driver, 'user', None)
            driver_email = getattr(driver_user, 'email', None) if driver_user else None
        except Exception:
            driver_email = None
    if driver_email:
        try:
            logger.info(f"notify_request_status_update: will notify driver '{driver_email}' for request id={request_obj.id}")
        except Exception:
            logger.info(f"notify_request_status_update: will notify driver '{driver_email}'")
        recipients.append(driver_email)
    
    if recipients:
        send_notification(
            subject=f'Laundry Request Status Updated: {request_obj.status}',
            template_name='emails/request_status_update.html',
            context=context,
            recipient_list=recipients
        )

def notify_driver_assignment(request_obj):
    """Notify when a driver is assigned to a request"""
    # Resolve driver and their email
    driver = getattr(request_obj, 'driver', None)
    driver_email = None
    if not driver:
        return
    try:
        driver_user = getattr(driver, 'user', None)
        driver_email = getattr(driver_user, 'email', None) if driver_user else None
    except Exception:
        driver_email = None
    if not driver_email:
        # no driver email to notify
        return
    # Resolve driver display name safely
    driver = request_obj.driver
    driver_name = ''
    if driver:
        driver_name = getattr(driver, 'name', '') or getattr(driver, 'email', '')
        # If driver is linked to a user, try that as well
        user_obj = getattr(driver, 'user', None)
        if not driver_name and user_obj:
            try:
                driver_name = user_obj.get_full_name() or getattr(user_obj, 'email', '')
            except Exception:
                driver_name = getattr(user_obj, 'email', '')

    context = {
        'request': request_obj,
        'driver_name': driver_name,
        'customer_name': request_obj.customer_name,
        'address': request_obj.address,
        'items': request_obj.items_description,
    }
    
    # Notify driver
    send_notification(
        subject='New Laundry Pickup Assignment',
        template_name='emails/driver_assignment.html',
        context=context,
        recipient_list=[driver_email]
    )
    
    # Notify customer if email available
    customer_email = None
    try:
        customer_email = getattr(request_obj.customer, 'email', None)
    except Exception:
        customer_email = None
    if customer_email:
        send_notification(
            subject='Driver Assigned to Your Laundry Request',
            template_name='emails/customer_driver_assigned.html',
            context=context,
            recipient_list=[customer_email]
        )


def notify_user_signup_confirmation(user):
    """Send a welcome email to the newly registered user confirming their signup"""
    if not user.email:
        logger.warning(f"notify_user_signup_confirmation: User {user.id} has no email address")
        return
    
    # Get user's full name or fallback to first_name or email
    try:
        name = user.get_full_name() or user.first_name or user.email
    except Exception:
        name = user.email
    
    context = {
        'name': name,
        'email': user.email,
        'date_joined': user.date_joined,
    }
    
    try:
        send_notification(
            subject='Welcome to Sophistican Laundry Logistics!',
            template_name='emails/customer_signup_confirmation.html',
            context=context,
            recipient_list=[user.email]
        )
        logger.info(f"notify_user_signup_confirmation: Sent welcome email to {user.email}")
    except Exception as e:
        logger.error(f"notify_user_signup_confirmation: Failed to send email to {user.email}: {str(e)}")
