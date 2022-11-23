from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import *
from .serializer import *

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    if not 'email' in request.POST:
        return Response({'detail': 'Does not have email'}, status=status.HTTP_400_BAD_REQUEST)
    if not 'name' in request.POST: 
        return Response({'detail': 'Does not have name'}, status=status.HTTP_400_BAD_REQUEST)
    if not 'password' in request.POST: 
        return Response({'detail': 'Does not have password'}, status=status.HTTP_400_BAD_REQUEST)  

    email = request.POST['email']
    password = request.POST['password']
    name = request.POST['name']
    
    user = User.objects.create(email=email, name=name)
    user.set_password(password)
    user.save()
    user_serializer = UserSerializer(user).data
    return Response(user_serializer)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = UserSerializer(request.user).data
    return Response(user)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user_serializer = UserSerializer(request.user, data=request.data, partial=True)
    if user_serializer.is_valid():
        user_serializer.save()
    else:
        return Response({'detail': 'User serializer error'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(user_serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_news(request):
    if not 'title' in request.POST:
        return Response({'detail': 'Does not have title'}, status=status.HTTP_400_BAD_REQUEST)
    if not 'message' in request.POST: 
        return Response({'detail': 'Does not have message'}, status=status.HTTP_400_BAD_REQUEST) 

    user = request.user
    title = request.POST['title']
    message = request.POST['message']

    news = News.objects.create(user=user, title=title, message=message)
    news.save()

    news_serializer = NewsSerializer(news).data
    return Response(news_serializer)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_news(request):
    news = News.objects.all()
    news_serializer_array = NewsSerializer(news, many=True).data

    for news_serializer in news_serializer_array: 
        if 'user' in news_serializer and news_serializer['user'] != None: 
            try: 
                user = User.objects.get(pk=news_serializer['user'])
                news_serializer['user'] = UserSerializer(user).data
            except: 
                news_serializer['user'] = None            

    return Response(news_serializer_array)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_news_of_user(request):
    user = request.user
    news = News.objects.filter(user=user)
    news_serializer_array = NewsSerializer(news, many=True).data

    for news_serializer in news_serializer_array: 
        if 'user' in news_serializer and news_serializer['user'] != None: 
            try: 
                user = User.objects.get(pk=news_serializer['user'])
                news_serializer['user'] = UserSerializer(user).data
            except: 
                news_serializer['user'] = None 

    return Response(news_serializer_array)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_news(request):
    if not 'id'in request.GET:
        return Response({'detail': 'Does not have id'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        news = News.objects.get(id=int(request.GET['id']))
    except:    
        return Response({'detail': 'News not found'}, status=status.HTTP_400_BAD_REQUEST)
    if news.user != request.user: 
         return Response({'detail': 'You don`t have permission to edit this news'}, status=status.HTTP_400_BAD_REQUEST)
    news_serializer = NewsSerializer(news, data=request.data, partial=True)

    if news_serializer.is_valid():
        news_serializer.save()
    else:
        return Response({'detail': 'News serializer error'}, status=status.HTTP_400_BAD_REQUEST)

    news_serializer = news_serializer.data

    if 'user' in news_serializer and news_serializer['user'] != None: 
        try: 
            user = User.objects.get(pk=news_serializer['user'])
            news_serializer['user'] = UserSerializer(user).data
        except: 
            news_serializer['user'] = None 
    
    return Response(news_serializer)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_news(request):
    if not 'id'in request.GET:
        return Response({'detail': 'Does not have id'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        news = News.objects.get(id=int(request.GET['id']))
    except:    
        return Response({'detail': 'News not found'}, status=status.HTTP_400_BAD_REQUEST)
    if news.user != request.user: 
        return Response({'detail': 'You don`t have permission to delete this news'}, status=status.HTTP_400_BAD_REQUEST)

    try: 
        news.delete()
        worked = True
    except:
        worked = False
    return Response({'worked':worked})