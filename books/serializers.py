from rest_framework import serializers
from .models import Book
from .models import Borrow, Notification
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BorrowSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title')

    class Meta:
        model = Borrow
        fields = ['id', 'book', 'book_title', 'borrow_date', 'return_date', 'status', 'fine']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']
