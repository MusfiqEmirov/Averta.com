from django.urls import path

from services.views.views_v1 import (
    HomePageView,
    ServicePageView,
    AboutPageView,
    ContactPageView,
    FAQPageView,
    BlogPageView,
    BlogDetailPageView,
    BlogViewCountsApiView,
)


app_name = 'services'

urlpatterns = [
    path(
        '',
        HomePageView.as_view(),
        name='home-page',
    ),
    path(
        'services/',
        ServicePageView.as_view(),
        name='service-page',
    ),
    path(
        'services/<slug:category_slug>/',
        ServicePageView.as_view(),
        name='service-category-page',
    ),
    path(
        'about/',
        AboutPageView.as_view(),
        name='about-page',
    ),
    path(
        'contact/',
        ContactPageView.as_view(),
        name='contact-page',
    ),
    path(
        'faq/',
        FAQPageView.as_view(),
        name='faq-page',
    ),
    path(
        'blog/',
        BlogPageView.as_view(),
        name='blog-page',
    ),
    path(
        'blog/api/view-counts/',
        BlogViewCountsApiView.as_view(),
        name='blog-view-counts',
    ),
    path(
        'blog/<int:blog_id>/',
        BlogDetailPageView.as_view(),
        name='blog-detail',
    ),
]
