from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} - {self.author}"



class Borrow(models.Model):
    STATUS_CHOICES = (
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    lefttime = timezone.now() + timedelta(days=7)
    return_date = models.DateTimeField(default=lefttime)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')
    fine = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.status})"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"A Notification for {self.user.username} is {self.message}"