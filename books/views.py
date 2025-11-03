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

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'borrow']:
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
            return_date=timezone.now() + timedelta(days=7)
        )

        book.available_copies -= 1
        book.save()

        send_borrow_notification.delay(book.title, user.username)

        serializer = BorrowSerializer(borrow)
        return Response(serializer.data, status=201)
