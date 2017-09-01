# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response


from Water_QC.api.serializers import *
from Water_QC.models import *

from django_filters.rest_framework import DjangoFilterBackend

# class MonthFolderViewSet(viewsets.ModelViewSet):
#     queryset = MonthFolder.objects.all()
#     serializer_class = MonthFolderSerializer
#
#
# class GeodatabaseViewSet(viewsets.ModelViewSet):
#     queryset = Geodatabase.objects.all()
#     serializer_class = GeodatabaseSerializer
#
#
# class FeatureClassViewSet(viewsets.ModelViewSet):
#     queryset = FeatureClass.objects.all()
#     serializer_class = FeatureClassSerializer


class FeatureChangeViewSet(viewsets.ModelViewSet):
    queryset = FeatureChange.objects.all()
    serializer_class = FeatureChangeSerializer


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('rmwid', 'qc_approved', )


class FeatureClassViewSet(viewsets.ModelViewSet):
    queryset = FeatureClass.objects.all()
    serializer_class = FeatureClassSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('change_type', 'geodatabase', )


class ChangeTypeViewSet(viewsets.ModelViewSet):
    queryset = ChangeType.objects.all()
    serializer_class = ChangeTypeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('change_type',)