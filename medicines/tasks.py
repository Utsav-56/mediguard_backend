from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from dateutil import rrule as dateutil_rrule
from dateutil.parser import parse as parse_date
import logging

from .models import Schedule, Reminder, Intake

logger = logging.getLogger(__name__)


@shared_task
def expand_schedule_rrule(schedule_id):
    """Generate next occurrences and write reminders for a schedule"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        
        # Delete existing pending reminders for this schedule
        Reminder.objects.filter(
            schedule=schedule, 
            status__in=['pending', 'snoozed']
        ).delete()
        
        # Get user timezone
        user_tz = pytz.timezone(schedule.timezone)
        now = timezone.now()
        
        if schedule.rrule:
            # Parse RRULE and generate next occurrences
            next_occurrences = _get_next_occurrences_from_rrule(schedule, user_tz, now)
        else:
            # Single occurrence
            next_occurrences = _get_single_occurrence(schedule, user_tz, now)
        
        # Create reminder objects
        reminders_created = 0
        for occurrence_dt in next_occurrences:
            reminder = Reminder.objects.create(
                schedule=schedule,
                status='pending',
                next_run=occurrence_dt
            )
            reminders_created += 1
        
        logger.info(f"Created {reminders_created} reminders for schedule {schedule_id}")
        return f"Created {reminders_created} reminders"
        
    except Schedule.DoesNotExist:
        logger.error(f"Schedule {schedule_id} not found")
        return f"Schedule {schedule_id} not found"
    except Exception as e:
        logger.error(f"Error expanding schedule {schedule_id}: {str(e)}")
        return f"Error: {str(e)}"


def _get_next_occurrences_from_rrule(schedule, user_tz, now, count=7):
    """Generate next N occurrences from RRULE"""
    try:
        # Combine date and time in user timezone
        start_dt = user_tz.localize(
            datetime.combine(schedule.date, schedule.time)
        )
        
        # Parse RRULE
        rrule_obj = dateutil_rrule.rrulestr(
            schedule.rrule,
            dtstart=start_dt
        )
        
        # Generate next occurrences
        occurrences = []
        for occurrence in rrule_obj:
            # Convert to UTC
            occurrence_utc = occurrence.astimezone(pytz.UTC)
            
            # Only include future occurrences
            if occurrence_utc > now:
                occurrences.append(occurrence_utc)
                if len(occurrences) >= count:
                    break
            
            # Check end_date
            if schedule.end_date and occurrence.date() > schedule.end_date:
                break
        
        return occurrences
        
    except Exception as e:
        logger.error(f"Error parsing RRULE for schedule {schedule.id}: {str(e)}")
        return []


def _get_single_occurrence(schedule, user_tz, now):
    """Generate single occurrence for non-recurring schedule"""
    try:
        # Combine date and time in user timezone
        occurrence_dt = user_tz.localize(
            datetime.combine(schedule.date, schedule.time)
        )
        
        # Convert to UTC
        occurrence_utc = occurrence_dt.astimezone(pytz.UTC)
        
        # Only return if it's in the future
        if occurrence_utc > now:
            return [occurrence_utc]
        
        return []
        
    except Exception as e:
        logger.error(f"Error creating single occurrence for schedule {schedule.id}: {str(e)}")
        return []


@shared_task
def process_due_reminders():
    """Find reminders due, send notifications, update triggered_at, schedule next run"""
    now = timezone.now()
    
    # Find due reminders
    due_reminders = Reminder.objects.filter(
        status='pending',
        next_run__lte=now
    ).exclude(
        snooze_until__gt=now
    ).select_related('schedule__medicine__user')
    
    processed_count = 0
    
    for reminder in due_reminders:
        try:
            with transaction.atomic():
                # Send notification (placeholder for now)
                send_reminder_notification(reminder)
                
                # Update reminder status
                reminder.triggered_at = now
                reminder.status = 'triggered'
                reminder.save()
                
                # Schedule next occurrence if recurring
                _schedule_next_occurrence(reminder)
                
                processed_count += 1
                
        except Exception as e:
            logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
    
    logger.info(f"Processed {processed_count} due reminders")
    return f"Processed {processed_count} reminders"


def send_reminder_notification(reminder):
    """Send notification for reminder (placeholder)"""
    # TODO: Implement FCM/APNs/SMS notification
    medicine = reminder.schedule.medicine
    user = medicine.user
    
    logger.info(
        f"NOTIFICATION: Reminder for {user.full_name} to take {medicine.name} "
        f"at {reminder.next_run}"
    )
    
    # Here you would integrate with FCM, APNs, or SMS services
    # Example structure:
    # payload = {
    #     'title': f'Time to take {medicine.name}',
    #     'body': f'Scheduled for {reminder.next_run.strftime("%H:%M")}',
    #     'data': {
    #         'reminder_id': reminder.id,
    #         'medicine_id': medicine.id,
    #         'schedule_id': reminder.schedule.id
    #     }
    # }
    # send_push_notification.delay(user.id, payload)


def _schedule_next_occurrence(reminder):
    """Schedule next occurrence for recurring reminders"""
    schedule = reminder.schedule
    
    if not schedule.rrule:
        # Non-recurring, mark as inactive
        reminder.status = 'inactive'
        reminder.save()
        return
    
    try:
        user_tz = pytz.timezone(schedule.timezone)
        current_time = reminder.next_run.astimezone(user_tz)
        
        # Parse RRULE to get next occurrence
        rrule_obj = dateutil_rrule.rrulestr(
            schedule.rrule,
            dtstart=current_time
        )
        
        # Get next occurrence after current
        next_occurrence = None
        for occurrence in rrule_obj:
            if occurrence > current_time:
                next_occurrence = occurrence
                break
        
        if next_occurrence:
            # Check end_date
            if schedule.end_date and next_occurrence.date() > schedule.end_date:
                reminder.status = 'inactive'
                reminder.save()
                return
            
            # Create new reminder for next occurrence
            next_occurrence_utc = next_occurrence.astimezone(pytz.UTC)
            Reminder.objects.create(
                schedule=schedule,
                status='pending',
                next_run=next_occurrence_utc
            )
        else:
            # No more occurrences
            reminder.status = 'inactive'
            reminder.save()
            
    except Exception as e:
        logger.error(f"Error scheduling next occurrence for reminder {reminder.id}: {str(e)}")


@shared_task
def send_push_notification(user_id, payload):
    """Wrapper around FCM/APNs notification sending"""
    try:
        from accounts.models import User
        from health_metrics.models import PushSubscription
        
        user = User.objects.get(id=user_id)
        subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
        
        sent_count = 0
        for subscription in subscriptions:
            try:
                # TODO: Implement actual push notification sending
                # based on subscription.platform
                logger.info(f"Sending push notification to {user.full_name} on {subscription.platform}")
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send push notification to subscription {subscription.id}: {str(e)}")
        
        return f"Sent {sent_count} notifications"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error sending push notification to user {user_id}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def cleanup_old_intakes():
    """Archive or delete old intakes per retention policy"""
    try:
        # Delete intakes older than 1 year
        cutoff_date = timezone.now() - timedelta(days=365)
        deleted_count, _ = Intake.objects.filter(created_at__lt=cutoff_date).delete()
        
        logger.info(f"Cleaned up {deleted_count} old intake records")
        return f"Cleaned up {deleted_count} records"
        
    except Exception as e:
        logger.error(f"Error cleaning up old intakes: {str(e)}")
        return f"Error: {str(e)}"