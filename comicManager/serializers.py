from rest_framework import serializers
from .models import Book, BookLibPath


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookLibPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLibPath
        fields = '__all__'
