from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('titles/<int:title_id>/', views.TitleDetailView.as_view(),
         name='title_detail'),
    path('reviews/<int:review_id>/',
         views.ReviewDetailView.as_view(), name='review_detail'),
    path('category/<str:category_slug>/', views.CategoryListView.as_view(),
         name='category_list'),
    path('genre/<str:genre_slug>/', views.GenreListView.as_view(),
         name='genre_list'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('titles/<int:title_id>/review/create/', views.ReviewCreate.as_view(),
         name='review_create'),
    path('titles/<int:title_id>/review/<int:review_id>/update/',
         views.ReviewUpdate.as_view(), name='review_update'),
    path('titles/<int:title_id>/review/<int:review_id>/delete/',
         views.ReviewDelete.as_view(), name='review_delete'),
    path('reviews/<int:review_id>/comment/', views.CommentCreate.as_view(),
         name='comment_create'),
    path('reviews/<int:review_id>/comment/<int:comment_id>/delete/',
         views.CommentDelete.as_view(),
         name='comment_delete'),
    path('search/', views.SearchView.as_view(), name='search')
]
