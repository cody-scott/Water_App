from process_new_data.process_new_data import process_geodatabase
from django.core.management.base import BaseCommand, CommandError
import os
import logging

from Water_App.settings import QC_SOURCE_PATH
from Water_QC import models

QC_IGNORE_FOLDERS = [
    '2015-02-20',
    '2015-05-28',
    '2015-08-20',
    '2015-09-10',
    '2015-10-05',
    '2015-11-03',
    '2015-12-01',
    '2016-01',
    '2016-02',
    '2016-03',
    '2016-09',
    '2017-01',
]


def load_new_data():
    folders = get_folders(QC_SOURCE_PATH)
    for folder in folders:
        existing_folder = models.MonthFolder.objects.filter(folder_name=folder).first() #type: models.Geodatabase
        existing_gdbs = []
        if existing_folder is not None:
            new_folder = existing_folder
            existing_gdbs = [gdb.geodatabase_name for gdb in existing_folder.geodatabase_set.all()]
        else:
            new_folder = models.MonthFolder()
            new_folder.folder_name = folder
            new_folder.folder_path = os.path.join(QC_SOURCE_PATH, folder)
            new_folder.save()

        geodatabases = _get_geodatabases(new_folder.folder_path)
        for geodatabase in geodatabases:
            if geodatabase[0] in existing_gdbs:
                continue

            results = process_geodatabase(os.path.join(new_folder.folder_path, geodatabase[0]))

            new_gdb = models.Geodatabase()
            new_gdb.folder = new_folder
            new_gdb.city = get_city_object(geodatabase[1])
            new_gdb.geodatabase_name = geodatabase[0]
            new_gdb.save()

            save_results(results, new_gdb)

def get_city_object(city):
    city = models.City.objects.filter(city_name__iexact=city).first()
    return city


def get_folders(path):
    folders = []
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if (os.path.isdir(full_path)) and (item not in QC_IGNORE_FOLDERS):
            folders.append(item)
    return folders


def _get_geodatabases(folder):
    geodatabase = []
    for item in os.listdir(folder):
        if '.GDB' in item.upper():
            city = _check_city(item)
            geodatabase.append([item, city])
    return geodatabase


def save_results(results, geodatabase_object):
    for item in results:

        ct = models.ChangeType.objects.filter(
            change_type__iexact=item.get("change_type")).first()
        ft = models.FeatureType.objects.filter(
            feature_name__iexact=item.get("feature_type")).first()

        new_fc = models.FeatureClass()
        new_fc.geodatabase = geodatabase_object
        new_fc.change_type = ct
        new_fc.feature_type = ft
        new_fc.save()

        if ct.change_type == "Updated":
            updated_features(item.get("data"))
        elif ct.change_type == "Deleted":
            delete_features(item.get("data"))
        else:
            added_features(item.get("data"))


def added_features(data):
    pass


def delete_features(data):
    pass


def updated_features(data):
    pass


def _check_city(geodatabase):
    for item in ["CAMBRIDGE", "KITCHENER", "WATERLOO"]:
        if item in unicode(geodatabase).upper():
            return item
    return "OTHER"


class Command(BaseCommand):
    help = "Sync the GDB and the sqlite dbs together"

    def handle(self, *args, **options):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        load_new_data()
