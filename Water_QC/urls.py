from __future__ import unicode_literals

from django.conf.urls import url, include
from Water_QC import views

from rest_framework.routers import DefaultRouter, SimpleRouter
from Water_QC.api.views import *

router = DefaultRouter()
# router.register(r'folders', MonthFolderViewSet)
# router.register(r'geodatabase', GeodatabaseViewSet)
router.register(r'featureclass', FeatureClassViewSet)
router.register(r'featurechange', FeatureChangeViewSet)
router.register(r'changetype', ChangeTypeViewSet)
router.register(r'feature', FeatureViewSet)

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^api/', include(router.urls)),
    url(r'^folder=(?P<pk>[0-9]+)', views.MonthFolder.as_view()),
    url(r'^geodatabase=(?P<pk>[0-9]+)', views.Geodatabase.as_view()),

]
