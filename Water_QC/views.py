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
    template_name = "Water_QC/geodatabase.html"