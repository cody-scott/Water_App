# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


from Water_QC.models import *


# class FeatureClassSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FeatureClass
#         fields = (
#             'id', 'url'
#         )
#
#
# class GeodatabaseSerializer(serializers.ModelSerializer):
#     featureclass_set = FeatureClassSerializer(
#         many=True,
#         read_only=True
#     )
#     class Meta:
#         model = Geodatabase
#         fields = (
#             'id', 'geodatabase_name', 'city', 'url', 'featureclass_set'
#         )
#
#
# class MonthFolderSerializer(serializers.ModelSerializer):
#     geodatabase_set = GeodatabaseSerializer(
#         many=True,
#         read_only=True,
#     )
#     class Meta:
#         model = MonthFolder
#         fields = (
#             "id", 'folder_name', 'folder_path', 'completed', 'geodatabase_set',
#         )

class FeatureChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureChange
        fields = (
            'change_field', 'old_value', 'new_value'
        )


class FeatureSerializer(serializers.ModelSerializer):
    featurechange_set = FeatureChangeSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = Feature
        fields = (
            'id', 'rmwid', 'qc_comments', 'qc_approved', 'featurechange_set', 'url',
            'feature_class'
        )
        read_only_fields = ('feature_class', 'rmwid', )


class FeatureClassSerializer(serializers.ModelSerializer):
    feature_type = serializers.StringRelatedField(many=False)
    change_type = serializers.StringRelatedField(many=False)
    feature_set = FeatureSerializer(many=True, read_only=True)

    class Meta:
        model = FeatureClass
        fields = (
            'id', 'feature_type', 'change_type', 'feature_set',
        )


class ChangeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeType
        fields = ('id', 'change_type', )
