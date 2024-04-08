from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet, ReviewViewSet,
                    CommentViewSet, UserViewSet, SignUpView,
                    TokenObtainRefreshView)

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainRefreshView.as_view(), name='token'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui', SpectacularSwaggerView.as_view(url_name='api:schema'),
         name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='api:schema'),
         name='redoc'),
]
