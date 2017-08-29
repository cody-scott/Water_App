from __future__ import unicode_literals

from django.conf.urls import url, include
from Water_QC import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
]
