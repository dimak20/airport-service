import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from air_service.email_utils import send_email
from air_service.models import Ticket

logger = logging.getLogger(__name__)


@shared_task
def send_ticket_reminders():
    reminder_time = timezone.now() + timedelta(hours=3)

    tickets = Ticket.objects.filter(
        flight__departure_time__lte=reminder_time,
        flight__departure_time__gt=timezone.now(),
        notification_sent=False
    )

    if not tickets.exists():
        return 0

    updated_tickets = []
    sent_count = 0

    for ticket in tickets:
        try:
            subject = f"Reminder about your ticket {ticket.flight.route}"
            message_content = (
                f"Your plane takes off at "
                f"{ticket.flight.departure_time.strftime('%Y-%m-%d %H:%M')}. "
                f"Ticket number: {ticket.id}.\n"
                f"Row: {ticket.row}, seat: {ticket.seat}. "
                f"Airplane: {ticket.flight.airplane.name}."
            )

            send_email(subject, message_content, ticket.order.user.email)

            ticket.notification_sent = True
            updated_tickets.append(ticket)
            sent_count += 1

        except Exception as e:
            logger.error(f"Error sending email to {ticket.order.user.email}: {e}")

    if updated_tickets:
        with transaction.atomic():
            Ticket.objects.bulk_update(updated_tickets, ['notification_sent'])
        logger.info(f"Sent reminders for tickets: {[ticket.id for ticket in updated_tickets]}")

    return sent_count
