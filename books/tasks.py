from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Borrow, Notification

@shared_task
def send_borrow_notification(book_title, username):
    print(f"کتاب {book_title} به {username} امانت داده شد.")
    
@shared_task
def check_overdue_books():
    now = timezone.now()
    print(f"Start CHecking book overdue: {now}")
    
    overdue_borrows = Borrow.objects.filter(status='borrowed', return_date__lt=now) or Borrow.objects.filter(status='overdue', return_date__lt=now)
    
    print(f"Overdue count: {overdue_borrows.count()}")
    
    if not overdue_borrows.exists():
        print("No overdue ")
        return "No overdue Founded!"
    
    for borrow in overdue_borrows:
        days_late = (now - borrow.return_date).days
        fine = days_late+1 * 5000

        print(f"analyze book {borrow.book.title} - User: {borrow.user.username}")
        print(f"return date: {borrow.return_date} - Return days: {days_late}")

        borrow.status = 'overdue'
        borrow.fine = fine
        borrow.save()

        Notification.objects.create(
            user=borrow.user,
            message=f"book '{borrow.book.title}' دیرکرد دارد ({days_late} روز). جریمه: {fine} ریال"
        )

        print(f"book '{borrow.book.title}' برای '{borrow.user.username}' دیرکرد دارد. جریمه: {fine} ریال.")
    
    result_message = f"بررسی دیرکردها کامل شد. {overdue_borrows.count()} کتاب دیرکرد پیدا شد."
    print(f" {result_message}")
    return result_message