# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# from django.contrib.gis.db import models
from django.utils import timezone


class FeatureType(models.Model):
    feature_name = models.CharField(max_length=200)

    def __str__(self):
        return "{}".format(self.feature_name)

    class Meta:
        ordering = ['feature_name']


class ChangeType(models.Model):
    change_type = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.change_type)

    class Meta:
        ordering = ['change_type']


class City(models.Model):
    city_name = models.CharField(max_length=30)


class MonthFolder(models.Model):
    folder_name = models.CharField(max_length=100)
    folder_path = models.TextField()

    completed = models.BooleanField(default=False)

    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]


# Create your models here.
class Geodatabase(models.Model):
    folder = models.ForeignKey(
        MonthFolder
    )

    city = models.ForeignKey(
        City
    )

    geodatabase_name = models.CharField(max_length=200)

    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.geodatabase_name)

    class Meta:
        ordering = ['city']




class FeatureClass(models.Model):
    geodatabase = models.ForeignKey(
        Geodatabase,
    )
    feature_type = models.ForeignKey(
        FeatureType,
    )
    change_type = models.ForeignKey(
        ChangeType,
    )

    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['feature_type']


class Feature(models.Model):
    feature_class = models.ForeignKey(FeatureClass)
    rmwid = models.CharField(max_length=25)
    qc_comments = models.CharField(max_length=200, null=True)
    qc_approved = models.NullBooleanField()

    class Meta:
        ordering = ['rmwid']


class FeatureChange(models.Model):
    feature = models.ForeignKey(
        Feature,
    )
    change_field = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.CharField(max_length=255, null=True, blank=True)
    new_value = models.CharField(max_length=255, null=True, blank=True)

