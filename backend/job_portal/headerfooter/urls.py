from django.urls import path
from .views import HeaderFooterView
from . import views

urlpatterns = [
    path('header-footer/', HeaderFooterView.as_view(), name='header-footer'),
    path('footer_detail/', views.footer_detail)
]
