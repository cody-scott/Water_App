from django.core.management.base import BaseCommand, CommandError
from Water_QC.models import FeatureType, ChangeType, City


def load_base_data():
    feature_types_list = FeatureType.objects.all()
    change_types_list = ChangeType.objects.all()
    if len(feature_types_list) == 0 and len(change_types_list) == 0:
        load_cities()
        load_change_types()
        load_feature_types()
    else:
        print("Data Loaded already")


def load_cities():
    for city in ["Cambridge", "Kitchener", "Waterloo"]:
        new_city = City()
        new_city.city_name = city
        new_city.save()


def load_change_types():
    change_types = ["Added", "Deleted", "Updated"]
    for item in change_types:
        new_change = ChangeType()
        new_change.change_type = item
        new_change.save()


def load_feature_types():
    feature_types = [
        'Chambers',
        'Hydrants',
        'Junctions',
        'Mains',
        'Services',
        'ServiceValves',
        'Valves',
    ]
    for item in feature_types:
        new_feature_type = FeatureType()
        new_feature_type.feature_name = item
        new_feature_type.save()


class Command(BaseCommand):
    help = "Sync the GDB and the sqlite dbs together"

    def handle(self, *args, **options):
        load_base_data()
