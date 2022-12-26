from django.db import models


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=500, verbose_name="标题", blank=True)
    author = models.CharField(max_length=100, verbose_name="作者", blank=True)
    publishDate = models.DateField(auto_now=False, auto_now_add=False, verbose_name="发行时间", blank=True, null=True)
    rating = models.SmallIntegerField(verbose_name="评分", blank=True, null=True)
    type = models.CharField(max_length=200, verbose_name="种类", blank=True, null=True)
    path = models.CharField(max_length=3000, verbose_name='路径', blank=True, null=True)


class BookLibPath(models.Model):
    folderPath = models.CharField(max_length=3000, verbose_name='文件夹路径', blank=True, null=True)
