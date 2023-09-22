from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ContentBlockView(APIView):
    def get(self, request):
        return Response({'message':'Successfully sended content'},status=status.HTTP_201_CREATED)