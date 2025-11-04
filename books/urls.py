from rest_framework.routers import DefaultRouter
from .views import BookViewSet
from django.urls import path
from .views import MyBorrowsView, MyNotificationsView, MyFinesView

urlpatterns = [
    path('my-borrows/', MyBorrowsView.as_view(), name='my-borrows'),
    path('notifications/', MyNotificationsView.as_view(), name='my-notifications'),
    path('fines/', MyFinesView.as_view(), name='my-fines'),
]

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns += router.urls
