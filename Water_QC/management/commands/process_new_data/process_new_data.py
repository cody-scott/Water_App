import logging
import sys
import os
import json

import arcview
import arcpy

# import feature_classes
from Water_QC.management.commands.process_new_data.feature_classes import \
    WaterJunctionsClass, WaterChambersClass, WaterHydrantClass, \
    WaterValvesClass, WaterServicesClass, WaterServicesValvesClass, \
    WaterMainClass

from datetime import datetime

SDELookup = {'Chambers': 'GIS.RMW.Water_Chambers',
             'Hydrants': 'GIS.RMW.Water_Hydrants',
             'Junctions': 'GIS.RMW.Water_Junctions',
             'Mains': 'GIS.RMW.Water_Mains',
             'Services': 'GIS.RMW.Water_Services',
             'ServiceValves': 'GIS.RMW.Water_ServiceValves',
             'Valves': 'GIS.RMW.Water_Valves'}


def process_geodatabase(geodatabase):
    logging.info("Feature: {}".format(geodatabase))
    if not check_gdb_path(geodatabase):
        logging.warning("{} doesn't exist".format(geodatabase))
        return None

    features = get_features(geodatabase)

    differences = []
    for feature in features:
        if "General" in feature:
            continue
        changes = (compare_feature(feature, geodatabase))
        if changes is not None:
            differences.append(changes)

    return differences


def compare_feature(feature, gdb_path):
    function_mapper = {
        "Added": added_feature,
        "Deleted": deleted_feature,
        "Updated": updated_feature
    }

    logging.info("Checking Feature: {}".format(feature))
    full_path = os.path.join(gdb_path, feature)

    if get_feature_count(feature, full_path) == 0:
        return None

    feature_name, sde_name, change_type = determine_feature_type(feature)

    differences = function_mapper[change_type](feature_name, sde_name, full_path)
    return {
        'feature_name': feature, 'feature_type': feature_name,
        'change_type': change_type, 'data': differences
    }


def get_feature_count(feature, feature_path):
    """
    Gets the count of the feature
    :param feature:
    :type feature:
    :param feature_path:
    :type feature_path:
    :return:
    :rtype:
    """
    feature_count = int(arcpy.GetCount_management(feature_path)[0])
    if feature_count == 0:
        logging.info("No items to check".format(feature))
    else:
        logging.info("{} item to check".format(feature_count))

    return feature_count


# region Comparators
# region Added features
def added_feature(feature_name, sde_feature, qc_feature_path):
    """
    Processes the features that are New to the dataset
    :param feature_name:
    :type feature_name:
    :param sde_feature:
    :type sde_feature:
    :param qc_feature_path:
    :type qc_feature_path:
    :return:
    :rtype:
    """
    logging.info("Getting new feature data")
    new_features = []

    with arcpy.da.SearchCursor(qc_feature_path, ["AreaMunicipal_ID", "SHAPE@", "QC_Approved", "QC_Comments"]) as sc:
        for row in sc:
            new_features.append(
                {'id': u'{}'.format(row[0]),
                 # 'shape': row[1].JSON,
                 'shape': reproject_to_epsg4326(row[1]).JSON,
                 'qc_approved': row[2],
                 'qc_comments': row[3]})
    return new_features
# endregion


# region Updated Features
def updated_feature(feature_name, sde_feature, qc_feature_path):
    """
    Processes the updated features
    :param feature_name:
    :type feature_name:
    :param sde_feature:
    :type sde_feature:
    :param qc_feature_path:
    :type qc_feature_path:
    :return:
    :rtype:
    """

    mapper = get_update_mapper(feature_name)

    if mapper is None:
        return []

    logging.info("QC {} Updated".format(feature_name))

    qc_items = get_updated_feature_data(qc_feature_path, mapper)
    sde_items = get_updated_feature_data(
        get_or_load_sde(feature_name, sde_feature),
        mapper,
        build_sql(qc_items),
        sde_feature=True
    )

    differences = compare_updated_feature(qc_items, sde_items, mapper[1])
    return differences


def get_update_mapper(feature_name):
    """
    Get the appropriate function and class for the feature type
    :param feature_name:
    :type feature_name:
    :return:
    :rtype:
    """
    update_function_mapper = {
        'Mains': [get_watermain_data, WaterMainClass.compare_watermains, WaterMainClass],
        'Valves': [get_valve_data, WaterValvesClass.compare_valves, WaterValvesClass],
        'Chambers': [get_chamber_data, WaterChambersClass.compare_chamber, WaterChambersClass],
        'Hydrants': [get_hydrant_data, WaterHydrantClass.compare_hydrant, WaterHydrantClass],
        'Services': [get_services_data, WaterServicesClass.compare_service, WaterServicesClass],
        'ServiceValves': [get_service_valve_data, WaterServicesValvesClass.compare_service_valve, WaterServicesValvesClass],
        'Junctions': [get_junctions_data, WaterJunctionsClass.compare_junction, WaterJunctionsClass],
    }
    mapper = update_function_mapper.get(feature_name, None)
    return mapper


def compare_updated_feature(qc_items, sde_items, compare_function):
    """
    Base comparison. For each rmwid in the new QC, check if its in sde and compare if so
    :param qc_items:
    :type qc_items:
    :param sde_items:
    :type sde_items:
    :param compare_function:
    :type compare_function:
    :return:
    :rtype:
    """
    item_difference = []
    for rmwid in qc_items:
        if rmwid in sde_items:
            item_difference.append(compare_qc_item(compare_function, qc_items, rmwid, sde_items))
        else:
            logging.warning("{} not in SDE".format(rmwid))
    return item_difference


def compare_qc_item(compare_function, qc_items, rmw_id, sde_items):
    """
    Compare the QC item against sde item
    :param compare_function:
    :type compare_function:
    :param qc_items:
    :type qc_items:
    :param rmw_id:
    :type rmw_id:
    :param sde_items:
    :type sde_items:
    :return:
    :rtype:
    """
    qc_feature = qc_items[rmw_id]
    sde_feature = sde_items[rmw_id]

    # compare function refers to the class function of the feature being compared
    feature_differences = compare_function(qc_feature, sde_feature)
    if len(feature_differences) > 0 or feature_differences == 'UNSET':
        return {
            'id': rmw_id,
            'differences': feature_differences,
            'new_shape': reproject_to_epsg4326(qc_feature.shape).JSON,
            'old_shape': reproject_to_epsg4326(sde_feature.shape).JSON,
            'qc_approved': qc_feature.qc_approved,
            'qc_comments': qc_feature.qc_comments
        }
    else:
        # No changes detected. Maybe should return other then none?
        return None


# region Class Builders
def get_updated_feature_data(feature, mapper_function, sql="", sde_feature=False):
    type_class = mapper_function[2]

    output_data = {}
    if sql == '"RMWID" IN ()':
        return output_data

    fields = get_update_fields(sde_feature, type_class)

    with arcpy.da.SearchCursor(feature, fields, sql) as sc:
        for row in sc:
            new_feat = mapper_function[0](row, sde_feature)
            if new_feat is not None and new_feat not in output_data:
                output_data[new_feat.id] = new_feat
            else:
                logging.warning("Duplicate record in {} at {}".format(feature, new_feat.id))

    return output_data


def get_update_fields(sde_feature, type_class):
    """
    Returns the needed fields based on the feature class type and if its the SDE feature or not
    :param sde_feature:
    :type sde_feature:
    :param type_class:
    :type type_class:
    :return:
    :rtype:
    """
    if sde_feature:
        fields = type_class.SDEFields
    else:
        fields = type_class.SDEFields + type_class.QC_Fields
    return fields


def get_watermain_data(row, sde_feature):
    if sde_feature:
        rmwid, install_year, material, diameter_mm, lining_type, lining_date, ownership, water_type, status, pressure_zone, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, install_year, material, diameter_mm, lining_type, lining_date, ownership, water_type, status, pressure_zone, shape, qc_approved, qc_comments = row
    WaterMain = WaterMainClass()
    WaterMain.id = rmwid
    WaterMain.install_year = install_year
    WaterMain.material = material
    WaterMain.diameter = diameter_mm
    WaterMain.lining_type = lining_type
    WaterMain.lining_date = lining_date
    WaterMain.ownership = ownership
    WaterMain.water_type = water_type
    WaterMain.status = status
    WaterMain.pressure_zone = pressure_zone
    WaterMain.shape = shape
    WaterMain.qc_approved = qc_approved
    WaterMain.qc_comments = qc_comments

    return WaterMain


def get_valve_data(row, sde_feature):
    if sde_feature:
        rmwid, install_year, valve_size, ownership, status, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, install_year, valve_size, ownership, status, shape, qc_approved, qc_comments = row
    WaterValve = WaterValvesClass()
    WaterValve.id = rmwid
    WaterValve.install_year = install_year
    WaterValve.valve_size = valve_size
    WaterValve.ownership = ownership
    WaterValve.status = status
    WaterValve.shape = shape
    WaterValve.qc_approved = qc_approved
    WaterValve.qc_comments = qc_comments

    return WaterValve


def get_chamber_data(row, sde_feature):
    if sde_feature:
        rmwid, install_year, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, install_year, shape, qc_approved, qc_comments = row
    WaterChamber = WaterChambersClass()
    WaterChamber.id = rmwid
    WaterChamber.install_year = install_year
    WaterChamber.shape = shape
    WaterChamber.qc_approved = qc_approved
    WaterChamber.qc_comments = qc_comments

    return WaterChamber


def get_hydrant_data(row, sde_feature):
    if sde_feature:
        rmwid, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, shape, qc_approved = row
        qc_comments = ""
    WaterHydrant = WaterHydrantClass()
    WaterHydrant.id = rmwid
    WaterHydrant.shape = shape
    WaterHydrant.qc_approved = qc_approved
    WaterHydrant.qc_comments = qc_comments

    return WaterHydrant


def get_services_data(row, sde_feature):
    if sde_feature:
        rmwid, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, shape, qc_approved, qc_comments = row
    WaterServices = WaterServicesClass()
    WaterServices.id = rmwid
    WaterServices.shape = shape
    WaterServices.qc_approved = qc_approved
    WaterServices.qc_comments = qc_comments

    return WaterServices


def get_service_valve_data(row, sde_feature=False):
    if sde_feature:
        rmwid, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, shape, qc_approved, qc_comments = row
    WaterServicesValves = WaterServicesValvesClass()
    WaterServicesValves.id = rmwid
    WaterServicesValves.shape = shape
    WaterServicesValves.qc_approved = qc_approved
    WaterServicesValves.qc_comments = qc_comments

    return WaterServicesValves


def get_junctions_data(row, sde_feature=False):
    if sde_feature:
        rmwid, shape = row
        qc_approved, qc_comments = "", ""
    else:
        rmwid, shape, qc_approved, qc_comments = row
    WaterJunctions = WaterJunctionsClass()
    WaterJunctions.id = rmwid
    WaterJunctions.shape = shape
    WaterJunctions.qc_approved = qc_approved
    WaterJunctions.qc_comments = qc_comments

    return WaterJunctions
# endregion
# endregion


# region Deleted Features
def deleted_feature(feature_name, sde_feature, qc_feature_path):
    """
    Process the "Deleted" feature
    :param feature_name:
    :type feature_name:
    :param sde_feature:
    :type sde_feature:
    :param qc_feature_path:
    :type qc_feature_path:
    :return:
    :rtype:
    """
    logging.info('Getting deleted feature data: {}'.format(qc_feature_path))
    removed_features = []

    comments_field = True
    if feature_name in ['Hydrants']:
        comments_field = False

    deleted_ids = get_deleted_rmwid(qc_feature_path, comments_field)
    sde_feature = get_or_load_sde(feature_name, sde_feature)

    with arcpy.da.SearchCursor(sde_feature, ["RMWID", "SHAPE@"], build_sql(deleted_ids)) as sc:
        for row in sc:
            removed_features += process_deleted_feature(deleted_ids, row)
    return removed_features


def build_sql(input_dct):
    """
    Generate the sql for the deleted ids, based on the input dictionary
    :param input_dct: deleted ids
    :type input_dct: dict
    :return:
    :rtype:
    """
    return "\"RMWID\" IN ({})".format(','.join("'{}'".format(x) for x in input_dct))


def process_deleted_feature(deleted_ids, row):
    """
    Process the features that are deleted
    :param deleted_ids:
    :type deleted_ids:
    :param row:
    :type row:
    :return:
    :rtype:
    """
    removed_features = []
    qc_data = deleted_ids.get(row[0], [None, None])
    removed_features.append(
        {
            'id': row[0],
            'shape': reproject_to_epsg4326(row[1]).JSON,
            'qc_approved': qc_data[0],
            'qc_comments': qc_data[1],
        })
    return removed_features


def get_deleted_rmwid(qc_feature_path, comments_field):
    """
    Gets the deleted rwmids for the feature that is deleted
    :param qc_feature_path:
    :type qc_feature_path:
    :param comments_field:
    :type comments_field:
    :return:
    :rtype:
    """
    logging.info('collecting removed RMWID')
    deleted_ids = {}

    fields = get_delete_comments_field(comments_field)

    with arcpy.da.SearchCursor(qc_feature_path, fields) as sc:
        for row in sc:
            deleted_ids.update(get_deleted_ids(comments_field, row))
    return deleted_ids


def get_delete_comments_field(comments_field):
    """
    Gets the appropriate comments field based on the feature
    :param comments_field:
    :type comments_field:
    :return:
    :rtype:
    """
    if comments_field:
        fields = ["RMWID", "QC_Approved", "QC_Comments"]
    else:
        fields = ["RMWID", "QC_Approved"]
    return fields


def get_deleted_ids(comments_field, row):
    """
    Returns the delete ids for the feature based on the comments field
    :param comments_field:
    :type comments_field:
    :param row:
    :type row:
    :return:
    :rtype:
    """
    deleted_ids = {}
    if comments_field:
        deleted_ids[row[0]] = [row[1], row[2]]
    else:
        deleted_ids[row[0]] = [row[1], None]
    return deleted_ids
# endregion


# region Unset Update
def unset_comparator(feature_name, sde_feature, qc_feature_path):
    """
    Returns a blank list for a compator. This is because the comparator has not been created for the feature
    :param feature_name:
    :type feature_name:
    :param sde_feature:
    :type sde_feature:
    :param qc_feature_path:
    :type qc_feature_path:
    :return:
    :rtype:
    """
    # Comparator that is not set for the feature
    return []
# endregion
# endregion


def reproject_to_epsg4326(in_shape):
    """
    Reprojects the feature to the datum for webmaps (4326)
    :param in_shape:
    :type in_shape:
    :return:
    :rtype:
    """
    epsg_4326_spatial_reference = arcpy.SpatialReference(4326)
    new_shape = in_shape.projectAs(epsg_4326_spatial_reference)
    return new_shape


def determine_feature_type(feature):
    """
    Determine the type of the supplied feature
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    change_type, check_name= get_change_type_and_feature(feature)
    return get_sde_feature_name(check_name, change_type)


def get_change_type_and_feature(feature):
    """
    Checks the feature name for the type of feature (Added/Deleted/Updated) and the name of the feature
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    check_name = feature.replace("QC_Region", "")
    change_type = ""
    for type_var in ["Added", "Deleted", "Updated"]:
        if type_var in check_name:
            change_type = type_var
            check_name = check_name.replace("_ToBe{}".format(type_var), "")
            return change_type, check_name
    return "", ""


def get_sde_feature_name(check_name, change_type):
    """
    Gets the appropriate SDE feature based on the feature name, and the change type of the feature
    IE: if its a hydrant that is updated, it would get the Hydrants feature name
    :param check_name:
    :type check_name:
    :param change_type:
    :type change_type:
    :return:
    :rtype:
    """
    for item in SDELookup:
        if item == check_name:
            return item, SDELookup[item], change_type


# region Data Loading Area
def check_gdb_path(geodatabase_path):
    """
    Verify if the supplied geodatabase path exists as a geodatabase
    :param geodatabase_path:
    :type geodatabase_path:
    :return:
    :rtype:
    """
    if os.path.isdir(geodatabase_path):
        return True
    else:
        return False


def get_features(geodatabase):
    """
    Get all features from the supplied geodatabase
    :param geodatabase:
    :type geodatabase:
    :return:
    :rtype:
    """
    logging.info("Getting features for {}".format(geodatabase))
    set_workspace(geodatabase)
    return [dataset for dataset in arcpy.ListFeatureClasses()]


def set_workspace(geodatabase):
    """
    Sets the arcpy.env.workspace to the current geodatabase
    This is required for looping the features within the geodatabase
    :param geodatabase:
    :type geodatabase:
    :return:
    :rtype:
    """
    logging.info("Setting workspace to {}".format(geodatabase))
    arcpy.env.workspace = geodatabase
    return


def get_or_load_sde(feature_name, feature):
    """
    Checks if the SDE Feature has been loaded into memory and loads if it has not been already
    :param feature_name:
    :type feature_name:
    :param feature:
    :type feature:
    :return:
    :rtype:
    """
    global data_dct
    if feature_name not in data_dct:
        data_dct[feature_name] = load_sde_feature(feature, feature_name)
    else:
        logging.info("{} already loaded".format(feature_name))
    return data_dct[feature_name]


def load_sde_feature(feature, feature_name):
    """
    Loads the feature from SDE into memory
    :param feature:
    :type feature:
    :param feature_name:
    :type feature_name:
    :return:
    :rtype:
    """
    logging.info("Loading {} from SDE".format(feature_name))
    outdata = arcpy.CopyFeatures_management(os.path.join(SDE_PATH, feature),
                                            "in_memory\\{}".format(feature_name))
    return outdata
# endregion


def setup_logger(script_id):
    """
    Setup the logging file to save script progress/errors
    :param script_id:
    :type script_id:
    :return:
    :rtype:
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # fh = logging.FileHandler(os.path.join(WORKING_FOLDER, "{}.log".format(
    #     datetime.now().strftime("%Y-%m-%d_%H%M%S"))))
    fh = logging.FileHandler(os.path.join(WORKING_FOLDER, "{}.log".format(script_id)))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


SDE_PATH = u'Database Connections\\Production.sde'
WORKING_FOLDER = os.path.join(os.getenv('APPDATA'), "QC_DATA")
data_dct = {}
