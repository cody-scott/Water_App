# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from Water_QC import models

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView


# Create your views here.
class Index(ListView):
    template_name = "Water_QC/index.html"
    queryset = models.MonthFolder.objects.all()


class MonthFolder(DetailView):
    model = models.MonthFolder
    template_name = "Water_QC/folder.html"
    # queryset = models.MonthFolder.objects.all()


class Geodatabase(DetailView):
    model = models.Geodatabase
    template_name = "Water_QC/review_data.html"

    def get_context_data(self, **kwargs):
        obj = kwargs.get("object")
        kwargs['Added'] = obj.featureclass_set.filter(change_type=1).all()
        kwargs['Deleted'] = obj.featureclass_set.filter(change_type=2).all()
        kwargs['Updated'] = obj.featureclass_set.filter(change_type=3).all()
        return super(Geodatabase, self).get_context_data(**kwargs)