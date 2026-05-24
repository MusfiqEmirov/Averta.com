from django.urls import path

from services.views.views_v1 import (
    HomePageView,
    ServicePageView,
    ServiceDetailPageView,
    PackagePageView,
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
        'services/<slug:service_slug>/',
        ServiceDetailPageView.as_view(),
        name='service-detail',
    ),
    path(
        'packages/',
        PackagePageView.as_view(),
        name='package-page',
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
        'blog/<slug:blog_slug>/',
        BlogDetailPageView.as_view(),
        name='blog-detail',
    ),
]
