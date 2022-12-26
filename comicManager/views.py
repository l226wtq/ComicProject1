import zipfile
import os

from PIL import Image
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from djangoProject1.settings import STATICFILES_DIRS, BASE_DIR
from .models import Book, BookLibPath
from rest_framework.viewsets import ModelViewSet

from .serializers import BookSerializer, BookLibPathSerializer


def index(request):
    return HttpResponse('hello')


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPageNumberPagination

    def generateCover(self, filePath, coverID):
        thumbnailSize = (400, 600)
        if os.path.exists(f'''{filePath}.zip'''):
            with zipfile.ZipFile(f'''{filePath}.zip''', mode="r") as bookZip:
                for name in bookZip.namelist():
                    if (zipfile.Path(root=bookZip, at=name).is_file()):
                        with bookZip.open(name) as coverFile:  # 这里似乎有bug
                            im = Image.open(coverFile)
                            im.thumbnail(size=thumbnailSize)
                            im.convert('RGB').save(f'{BASE_DIR}\\static\\covers\\{coverID}.webp', format="WebP",
                                                   qulity=90)
                        break

        else:
            print("no exists")

    # 扫描zip并添加入DB
    def scanDirbooks(self):
        comicLibPaths = BookLibPath.objects.all().values_list('folderPath', flat=True)
        for path in comicLibPaths:
            DBBooktitileList = self.queryset.values_list('title', flat=True)
            for root, dirs, files in os.walk(path):
                create_bulk = []
                try:
                    lastID = Book.objects.all().order_by('-id')[0].id
                except IndexError:
                    lastID = 0
                for file in files:
                    filename = os.path.splitext(file)[0]
                    exname = os.path.splitext(file)[1]
                    if exname == ".zip":
                        # 按照文件名称来判断是否一再数据库里
                        if filename in DBBooktitileList:
                            obj = Book.objects.get(title=filename)
                            if (obj.path != root):
                                obj.path = root
                                obj.save()
                        else:
                            lastID += 1
                            self.generateCover(os.path.join(root, filename), lastID)
                            create_bulk.append(Book(title=filename, path=root))
                Book.objects.bulk_create(create_bulk)

    @action(methods=['get'], detail=False)
    def refresh(self, request):
        return HttpResponse('refresh')

    @action(methods=['get'], detail=False)
    def scan(self, request):
        self.scanDirbooks()
        return HttpResponse('scan')

    @action(methods=['get'], detail=True)
    def bookLength(self, request, pk):
        try:
            book = Book.objects.get(id=pk)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = BookSerializer(book)
        bookTitle = ser.data['title']
        bookPath = ser.data['path']
        if os.path.exists(f'''{bookPath}//{bookTitle}.zip'''):
            bookZip = zipfile.ZipFile(f'''{bookPath}//{bookTitle}.zip''', mode="r")
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # print([item for item in bookZip.infolist() if not item.is_dir()])
        return HttpResponse([item for item in bookZip.infolist() if not item.is_dir()].__len__())

    def getBookPicFileName(self, obj):
        return int(os.path.splitext(obj.filename)[0])

    @action(methods=['get'], detail=True)
    def bookPic(self, request, pk):
        try:
            book = Book.objects.get(id=pk)
            print(request)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = BookSerializer(book)
        bookTitle = ser.data['title']
        bookPath = ser.data['path']
        page = int(request.query_params.get('page'))
        # picHeight=request.query_params['height']
        # picWidth=request.query_params['width']
        if os.path.exists(f'''{bookPath}//{bookTitle}.zip'''):
            bookZip = zipfile.ZipFile(f'''{bookPath}//{bookTitle}.zip''', mode="r")
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        templist = [item for item in bookZip.infolist() if not item.is_dir()]
        templist.sort(key=self.getBookPicFileName)  # 按照数字名称排序
        # print(templist)
        # picList = [item for item in bookZip.infolist() if not item.is_dir()].sort()
        # return HttpResponse(bookZip.read(picList[page - 1]), content_type='image/webp')
        return HttpResponse(bookZip.read(templist[page - 1]), content_type='image/jpeg')


class LibCustomPageNumberPagination(PageNumberPagination):
    page_size = 20


class BookLibPathViewSet(ModelViewSet):
    queryset = BookLibPath.objects.all()
    serializer_class = BookLibPathSerializer
    pagination_class = LibCustomPageNumberPagination
