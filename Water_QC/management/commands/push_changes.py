from django.core.management.base import BaseCommand, CommandError
from Water_QC import models

import os

import arcview
import arcpy


def push_changes():
    folder_object = get_gdb()
    if folder_object is not None:
        update_geodatabase(folder_object)


def update_geodatabase(folder_object):
    folder_object = folder_object #type: models.MonthFolder
    for geodatabase in folder_object.geodatabase_set.all():
        update_feature_class(geodatabase, folder_object.folder_path)


def update_feature_class(geodatabase_object, folder_path):
    geodatabase_object = geodatabase_object # type: models.Geodatabase
    gdb_path = os.path.join(folder_path, geodatabase_object.geodatabase_name)
    for feature_class in geodatabase_object.featureclass_set.all():
        update_feature(feature_class, gdb_path)


def update_feature(feature_class_object, geodatabase_path):
    feature_class_object = feature_class_object #type: models.FeatureClass

    feature_str = "QC_Region{}_ToBe{}".format(
        feature_class_object.feature_type.feature_name,
        feature_class_object.change_type.change_type,
    )
    feature_path = os.path.join(geodatabase_path, feature_str)

    features = {}

    for feature in feature_class_object.feature_set.all():
        features[feature.rmwid] = [feature.qc_approved, feature.qc_comments]

    if features == {}:
        return

    update_feature_arc(
        feature_path,
        feature_class_object.change_type.change_type,
        features
    )


def update_feature_arc(feature_path, change_type, data):
    if change_type == "Added":
        fields = ["AreaMunicipal_ID", "QC_Approved", "QC_Comments"]
        sql_data = ",".join([id for id in data])
    else:
        fields = ["RMWID", "QC_Approved", "QC_Comments"]
        sql_data = ",".join(["'{}'".format(id) for id in data])

    sql = "\"{}\" IN ({})".format(fields[0], sql_data)

    print("Updating {}".format(feature_path))
    with arcpy.da.UpdateCursor(feature_path, fields, sql) as sc:
        for row in sc:
            id = u'{}'.format(row[0])
            qc_approved, qc_comment = data.get(id, [None, None])
            if qc_approved is True:
                qc_approved = "Yes"
            elif qc_approved is False:
                qc_approved = "No"

            row[1] = qc_approved
            row[2] = qc_comment
            sc.updateRow(row)


def get_gdb():
    objects = models.MonthFolder.objects.filter(completed=False).all()
    list_items = [[item.id, item.folder_name] for item in objects]

    print("Enter ID from list or 'q' to quit")
    for item in list_items:
        print("ID: {}\tFolder: {}".format(item[0], item[1]))

    if len(list_items) == 0:
        print("No items")
        return None

    while True:
        id_val = raw_input()
        if id_val == "q":
            return None
        try:
            id_int = int(id_val)
            folder = models.MonthFolder.objects.get(id=id_int)
            return folder
        except:
            print("Not a correct id, choose correct value or enter 'q'")
            pass




class Command(BaseCommand):
    help = "Sync the GDB and the sqlite dbs together"

    def handle(self, *args, **options):
        push_changes()
