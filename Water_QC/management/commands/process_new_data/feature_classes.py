import logging


class WaterBase(object):
    """
    Base QC object with the field names and comparator methods
    """
    QC_Fields = ['QC_Approved', 'QC_Comments']

    @staticmethod
    def compare_value(new_value, old_value):
        try:
            if old_value != new_value:
                return False
            else:
                return True
        except:
            return False

    @staticmethod
    def compare_shape(old_shape, new_shape):
        if new_shape.equals(old_shape):
            return True
        else:
            return False

    @staticmethod
    def differences_to_dct(differences):
        return [{'field': item[0], 'old_value': item[1], 'new_value': item[2]} for item in differences]


class WaterBaseFeature(WaterBase):
    """
    Same as the base feature, but this also contains the geometry and RMWID
    """
    SDEFields = ["RMWID",
                 "SHAPE@"]

    def __init__(self):
        self.id = None
        self.shape = None
        self.qc_approved = None
        self.qc_comments = None


class WaterMainClass(WaterBase):
    SDEFields = ["RMWID",
                 "InstallYear",
                 "Material",
                 "Diameter_mm",
                 "LiningType",
                 "LiningDate",
                 "Ownership",
                 "WaterType",
                 "Status",
                 "PressureZone",
                 "SHAPE@"]

    def __init__(self):
        self.id = None
        self.install_year = None
        self.material = None
        self.diameter = None
        self.lining_type = None
        self.lining_date = None
        self.ownership = None
        self.water_type = None
        self.status = None
        self.pressure_zone = None
        self.shape = None
        self.qc_approved = None
        self.qc_comments = None

    def compare_watermains(self, old_watermain):
        differences = []

        if not self.compare_value(self.install_year, old_watermain.install_year):
            differences.append(["InstallYear", old_watermain.install_year, self.install_year])
        if not self.compare_value(self.material, old_watermain.material):
            differences.append(["Material", old_watermain.material, self.material])
        if not self.compare_value(self.diameter, old_watermain.diameter):
            differences.append(["Diameter", old_watermain.diameter, self.diameter])
        if not self.compare_value(self.lining_type, old_watermain.lining_type):
            differences.append(["LiningType", old_watermain.lining_type, self.lining_type])
        if not self.compare_value(self.lining_date, old_watermain.lining_date):
            differences.append(["LiningDate", old_watermain.lining_date, self.lining_date])
        if not self.compare_value(self.ownership, old_watermain.ownership):
            differences.append(["Ownership", old_watermain.ownership, self.ownership])
        if not self.compare_value(self.water_type, old_watermain.water_type):
            differences.append(["WaterType", old_watermain.water_type, self.water_type])
        if not self.compare_value(self.status, old_watermain.status):
            differences.append(["Status", old_watermain.status, self.status])
        if not self.compare_value(self.pressure_zone, old_watermain.pressure_zone):
            differences.append(["PressureZone", old_watermain.pressure_zone, self.pressure_zone])
        if not self.compare_shape(self.shape, old_watermain.shape):
            # differences.append(["SHAPE", old_watermain.shape.WKT, self.shape.WKT])
            differences.append(["SHAPE", None, None])

        return self.differences_to_dct(differences)


class WaterValvesClass(WaterBase):
    SDEFields = ["RMWID",
                 "InstallYear",
                 "ValveSize",
                 "Ownership",
                 "Status",
                 "SHAPE@"]

    def init(self):
        self.id = None
        self.install_year = None
        self.valve_size = None
        self.ownership = None
        self.status = None
        self.shape = None
        self.qc_approved = None
        self.qc_comments = None

    def compare_valves(self, old_valve):
        differences = []

        if not self.compare_value(self.install_year, old_valve.install_year):
            differences.append(["InstallYear", old_valve.install_year, self.install_year])
        if not self.compare_value(self.valve_size, old_valve.valve_size):
            differences.append(["ValveSize", old_valve.valve_size, self.valve_size])
        if not self.compare_value(self.ownership, old_valve.ownership):
            differences.append(["Ownership", old_valve.ownership, self.ownership])
        if not self.compare_value(self.status, old_valve.status):
            differences.append(["Status", old_valve.status, self.status])
        if not self.compare_shape(self.shape, old_valve.shape):
            differences.append(["SHAPE", "", ""])

        return self.differences_to_dct(differences)


class WaterChambersClass(WaterBase):
    SDEFields = ["RMWID",
                 "InstallYear",
                 "SHAPE@"]

    def __init__(self):
        self.id = None
        self.install_year = None
        self.shape = None
        self.qc_approved = None
        self.qc_comments = None

    def compare_chamber(self, old_chamber):
        differences = []
        if not self.compare_value(self.install_year, old_chamber.install_year):
            differences.append(["InstallYear", old_chamber.install_year, self.install_year])
        if not self.compare_shape(self.shape, old_chamber.shape):
            differences.append(["SHAPE", "", ""])
        return self.differences_to_dct(differences)


class WaterHydrantClass(WaterBaseFeature):
    QC_Fields = ["QC_Approved"]

    def __init__(self):
        super(WaterBaseFeature, self).__init__()

    def compare_hydrant(self, old_hydrant):
        logging.warning("Hydrant not implemented")
        return 'UNSET'


class WaterServicesClass(WaterBaseFeature):
    def __init__(self):
        super(WaterBaseFeature, self).__init__()

    def compare_service(self, old_service):
        logging.warning("Service not implemented")
        return 'UNSET'


class WaterServicesValvesClass(WaterBaseFeature):
    def __init__(self):
        super(WaterBaseFeature, self).__init__()

    def compare_service_valve(self, old_service_valve):
        logging.warning("Service Valve not implemented")
        return 'UNSET'


class WaterJunctionsClass(WaterBaseFeature):
    def __init__(self):
        super(WaterBaseFeature, self).__init__()

    def compare_junction(self, old_junction):
        logging.warning("Junction not implemented")
        return 'UNSET'
