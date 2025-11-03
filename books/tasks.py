from celery import shared_task

@shared_task
def send_borrow_notification(book_title, username):
    print(f"📘 کتاب {book_title} به {username} امانت داده شد.")
