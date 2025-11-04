from rest_framework import viewsets, permissions
from .models import Book
from .serializers import BookSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from .models import Borrow
from .serializers import BorrowSerializer
from .tasks import send_borrow_notification  # Celery task
from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'borrow', 'return_book']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        user = request.user
        book = self.get_object()

        if book.available_copies <= 0:
            return Response({"error": "کتاب موجود نیست."}, status=400)

        if Borrow.objects.filter(user=user, book=book, status='borrowed').exists():
            return Response({"error": "شما قبلاً این کتاب را گرفته‌اید."}, status=400)
        
        borrow = Borrow.objects.create(
            user=user,
            book=book,
            return_date=timezone.now() + timedelta(seconds=60) # تست با زمان کمتر به جای days=7
        )

        book.available_copies -= 1
        book.save()

        send_borrow_notification.delay(book.title, user.username)

        serializer = BorrowSerializer(borrow)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        user = request.user
        book = self.get_object()

        try:
            borrow = Borrow.objects.get(user=user, book=book, status='borrowed')
        except Borrow.DoesNotExist:
            return Response({"error": "شما چنین کتابی را امانت نگرفته‌اید یا قبلاً برگردانده‌اید."}, status=400)

        now = timezone.now()
        fine = 0
        if now > borrow.return_date:
            days_late = (now - borrow.return_date).days
            fine = days_late * 5000
            borrow.status = 'overdue'
        else:
            borrow.status = 'returned'

        borrow.fine = fine
        borrow.save()

        book.available_copies += 1
        book.save()

        msg = f"کتاب {book.title} با موفقیت بازگردانده شد."
        if fine > 0:
            msg += f" جریمه دیرکرد: {fine} می باشد که باید پرداخت شود."

        return Response({"message": msg, "fine": fine}, status=200)
    

class MyBorrowsView(generics.ListAPIView):
    serializer_class = BorrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Borrow.objects.filter(user=self.request.user).order_by('-borrow_date')

class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class MyFinesView(generics.ListAPIView):
    serializer_class = BorrowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Borrow.objects.filter(user=self.request.user, fine__gt=0)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_fine = sum(item.fine for item in queryset)
        return Response({
            "total_fine": total_fine,
            "items": serializer.data
        })