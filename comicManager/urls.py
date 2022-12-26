from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('lib', views.BookLibPathViewSet, basename='lib')  # 注意顺序
router.register('', views.BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls))
]
