#!/usr/bin/python
# -*- coding: latin-1 -*-

import xml.etree.ElementTree as ET, os, sys, glob, re
import configparser
from time import gmtime, strftime
from uuid import getnode as get_mac


# Generate new Wid based on MAC, Timestamp, Counter
def _get_wid(wid_count):
    """

    Args:
        wid_count: wid counter must be incremented after each call

    Returns:
        str: WID generated

    """
    mac = hex(get_mac())[2:].upper()
    ts = strftime("%Y%m%d%H%M%S", gmtime())
    wid_counter = "%06x" % wid_count

    return str(mac+ts+wid_counter)


# Safe return of config parameter from parser.ini, return 0 if option is not found
def _get_config(_section, _parameter):
    """

    Args:
        _section: Section name to get from .ini file
        _parameter: Parameter name to get from .ini file

    Returns:
        str: value of the parameter or "None" if not found
    """
    # Get script current directory
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    # Read configuration file options.ini
    config = configparser.ConfigParser()
    config.read(os.path.join(scriptDir, "options.ini"))
    configOptional = []
    try :  return config[_section][_parameter]
    except KeyError:
        if not _parameter in configOptional:
            print( "WARNING : Parameter \"", _parameter, "\" not defined for template : ", _section)
            print( "WARNING : Please review", os.path.join(scriptDir, "options.ini"), " configuration")
        return "none"


# Safe return of config parameter from parser.ini, return 0 if option is not found
def _get_threshold(_section, _parameter):
    """

    Args:
        _section:
        _parameter:

    Returns:

    """
    # Get script current directory
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    # Read configuration file threshold.ini
    config = configparser.ConfigParser()
    config.read(os.path.join(scriptDir, "threshold.ini"))

    configOptional = ["property", "value"]
    try:
        return config[_section][_parameter]
    except KeyError:
        if not _parameter in configOptional:
            print("WARNING : Parameter \"", _parameter, "\" not defined for template : ", _section)
            print("WARNING : Please review ", os.path.join(scriptDir, "threshold.ini"), "configuration")
        return "none"


lib_list = {
    "InfoVista VM Mobile Basic": ("144", "14DB9B80589911DD9E0B0019B912D16E"),
    "InfoVista VistaMart Solution Model": ("157", "08D684717D4611DAAD220030482A3499"),
    "InfoVista VM Mobile-Planning Basic": ("38", "D58BDBC00B0D11E3B77C000C293EBF75"),
    "InfoVista Core": ("313", "62B1003EE320D011993B0020AFB73740"),
    "InfoVista VIN AdHoc Basic": ("7", "27CD43A05D9811DF9CB3005056B32481"),
    "InfoVista Common Card Element": ("18", "C7226A6CE325DF118B8100123F64919E"),
    "InfoVista VM Mobile ZTE": ("1", "7E995580EA8B11E587BDF8B156B694C5"),
    "InfoVista Solution Model": ("287", "5ADD78DEE482734188C23335A2D15C3B"),
    "InfoVista Mobile - Basics": ("52", "5B58D5DC0E33DD11A280B0B0A0B7120D"),
    "InfoVista Network - Basics": ("139", "199B6BD04F3C2A499CB9C271C24735EC"),
    "InfoVista Mobile SGSN": ("44", "3D9AC900533111DD9A860019B912D16E"),
}

vista_list = {
    "2G Cell":"39718FB047C411DFA3650019B912D35C",
    "BSC":"FDB77DE047C311DFA3650019B912D35C",
    "BTS":"2093983047C411DFA3650019B912D35C",
    "3G Cell":"7BF1841047C111DFA3650019B912D35C",
    "Node-B":"6E1B9AC047C011DFA3650019B912D35C",
    "RNC":"5DA6CE3047C011DFA3650019B912D35C",
    "LTE Cell":"53DB43E0F18411DF9829001422438980",
    "Enode-B":"A84C0100F18211DF9829001422438980",
    "MGW": "F646191047C611DFA3650019B912D35C",
}
vista_group = {
    "2G" : ("2G Cell","BSC", "BTS"),
    "3G" : ("3G Cell","Node-B", "RNC"),
    "4G" : ("LTE Cell","Enode-B"),
}

# Header
def gen_xml_tree_root(libname):
    """

    Args:
        libname: Name of the library

    Returns:

    """
    root = ET.Element("Library", Name=libname, Type="2", Wid="77401ED04D4422DFB5AC000C2985C9D6")
    return root


# Default Detail Settings
def gen_xml_tree_header(root):
    """

    Args:
        root: ET.ElementTree.root

    Returns:
        ET.ElementTree
    """
    sroot = ET.SubElement(root, "Dependencies", type="Refs")

    for libname, param in lib_list.items():
        try:
            s2_sroot = ET.SubElement(sroot, "Library", Name=str(libname), Version=str(param[0]), Wid=str(param[1]))
        except AttributeError:
            print("Error in building dependencies line: ", str(libname))

    sroot = ET.SubElement(root, "Generation")
    s2_sroot = ET.SubElement(sroot, "Engine")

    if _get_config('DEFAULT', 'Engine') != "none":
        s2_sroot.text = str(_get_config('DEFAULT', 'Engine'))
    else:
        #Failback
        s2_sroot.text = "vistamart 5.0 (build 5.0.65)"
    s2_sroot = ET.SubElement(sroot, "Time")

    sroot = ET.SubElement(root, "Version")
    if _get_config('DEFAULT', 'Revision') != "none":
        sroot.text = "$ Revision: "+str(_get_config('DEFAULT', 'Revision'))+" $"
    else:
        #Failback
        sroot.text = "$ Revision: 1 $"

    sroot = ET.SubElement(root, "Provider")
    if _get_config('DEFAULT', 'Provider') != "none":
        sroot.text = str(_get_config('DEFAULT', 'Provider'))
    else:
        # Failback
        sroot.text = "InfoVista"

    sroot = ET.SubElement(root, "LicenseKey")
    sroot = ET.SubElement(root, "Scope")
    sroot = ET.SubElement(root, "NecessaryBuild")
    if _get_config('DEFAULT', 'NecessaryBuild') != "none":
        sroot.text = str(_get_config('DEFAULT', 'NecessaryBuild'))
    else:
        # Failback
        sroot.text = "50000"

    sroot = ET.SubElement(root, "Access")
    if _get_config('DEFAULT', 'Access') != "none":
        sroot.text = str(_get_config('DEFAULT', 'Access'))
    else:
        # Failback
        sroot.text = "2"

    sroot = ET.SubElement(root, "Vistas")
    sroot = ET.SubElement(root, "Properties")
    sroot = ET.SubElement(root, "Rules")
    sroot = ET.SubElement(root, "Protocols")
    sroot = ET.SubElement(root, "Calendars")
    sroot = ET.SubElement(root, "MibFiles")
    sroot = ET.SubElement(root, "Mibs")
    sroot = ET.SubElement(root, "Indicators")
    sroot = ET.SubElement(root, "Formulas")
    sroot = ET.SubElement(root, "Metrics")
    sroot = ET.SubElement(root, "FilterFamilies")
    sroot = ET.SubElement(root, "ReportTemplates")
    sroot = ET.SubElement(root, "RuleModules")
    sroot = ET.SubElement(root, "CIRules")
    sroot = ET.SubElement(root, "GlobalVariables")
    sroot = ET.SubElement(root, "VMResolvers")

    return root


def gen_adhoc_header(root):
    """

    Args:
        root:

    Returns:
        ET.ElementTree: Pointing on the <AdhocModel> Element

    """
    sroot = ET.SubElement(root, "AdhocModels")

    if _get_config('ADHOC', 'Name') != "none":
        adhoc_name = str(_get_config('ADHOC', 'Name'))
    else:
        #Failback
        adhoc_name = "Generated Ad-hoc Model"

    s2_sroot = ET.SubElement(sroot, "AdhocModel", name=adhoc_name, Wid=_get_wid(10))

    return s2_sroot


def gen_adhoc_vista(root_format, vista_list):
    """

    Args:
        root_format:
        vista_list:

    Returns:

    """
    ct = 20
    wid_list = {}

    for name, wid in vista_list:
        wid_list[name] = _get_wid(++ct)
        s1_sroot = ET.SubElement(root_format, "AdhocVista", Alias=str(name), Wid=wid_list[name])
        s2_sroot = ET.SubElement(s1_sroot, "Allproperties")
        s2_sroot.text = "0"
        s2_sroot = ET.SubElement(s1_sroot, "Allindicators")
        s2_sroot.text = "0"
        s2_sroot = ET.SubElement(s1_sroot, "VistaWid")
        s2_sroot.text = str(wid)

    return wid_list


def gen_adhoc_indicator(root_format, input_list, wid_list):
    """

    Args:
        root_format:
        vista_list:

    Returns:

    """
    ct = 20

    for name, wid in input_list:
        s1_sroot = ET.SubElement(root_format, "AdhocIndicator", Alias=str(name), Wid=_get_wid(++ct))
        s2_sroot = ET.SubElement(s1_sroot, "Allproperties")
        s2_sroot.text = "0"
        s2_sroot = ET.SubElement(s1_sroot, "Allindicators")
        s2_sroot.text = "0"
        s2_sroot = ET.SubElement(s1_sroot, "VistaWid")
        s2_sroot.text = str(wid)





#Default Detail Settings
def gen_xml_adhoc_content(root_col, col, name, wid, unit="None"):
    """

    Args:
        root_col:
        col:
        name:
        wid:
        unit:
    Returns:

    """

    sroot = ET.SubElement(root_col, "AdhocVistas")
    wid_list = gen_adhoc_vista(sroot, vista_list)
    sroot = ET.SubElement(root_col, "AdhocIndicators")
    gen_adhoc_indicator(sroot, input_list, wid_list)


    s2_sroot = ET.SubElement(sroot, "Data", list="true")
    s3_sroot = ET.SubElement(s2_sroot, "Metric", list="true")
    # WID VALUE INPUT
    s4_sroot = ET.SubElement(s3_sroot, "Indicator_"+wid, list="true")
    s5_sroot = ET.SubElement(s4_sroot, "Name")
    s6_sroot = ET.SubElement(s5_sroot, "value")
    # NAME VALUE INPUT
    s6_sroot.text = name

    s1_root = ET.SubElement(sroot, "DrillDowns", list="true")
    s2_sroot = ET.SubElement(s1_root, "DrillDown_0", list="true")

    s3_sroot = ET.SubElement(s2_sroot, "AccessFrom")
    s4_sroot = ET.SubElement(s3_sroot, "value")
    s4_sroot.text = "1"

    s3_sroot = ET.SubElement(s2_sroot, "Type")
    s4_sroot = ET.SubElement(s3_sroot, "value")
    s4_sroot.text = "2"

    s3_sroot = ET.SubElement(s2_sroot, "VistaPortalTemplate", list="true")

    s4_sroot = ET.SubElement(s3_sroot, "ReportTemplate")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    #DRILLDOWN VALUE INPUT
    s5_sroot.text = drilldown

    s4_sroot = ET.SubElement(s3_sroot, "TemporalEvolution")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "false"

    s4_sroot = ET.SubElement(s3_sroot, "ExploreGroupsMode")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "-1"

    s4_sroot = ET.SubElement(s3_sroot, "Vista")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "none"

    s4_sroot = ET.SubElement(s3_sroot, "Property")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "none"

    s4_sroot = ET.SubElement(s3_sroot, "DisplayRate", list="true")
    s5_sroot = ET.SubElement(s4_sroot, "Code")
    s6_sroot = ET.SubElement(s5_sroot, "value")
    s6_sroot.text = "-1"

    s3_sroot = ET.SubElement(s2_sroot, "IconLink", list="true")

    s4_sroot = ET.SubElement(s3_sroot, "Image")
    s5_sroot = ET.SubElement(s4_sroot, "value")

    s5_sroot.text = "downarrow.gif"

    s4_sroot = ET.SubElement(s3_sroot, "ToolTip")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "Raw Counters"

    s1_root = ET.SubElement(sroot, "Format", list="true")
    s2_sroot = ET.SubElement(s1_root, "SubLabel")

    if unit != "None":
        try:
            split = mapping_unit[unit].split(',')
            #print("Mapped unit:", split[0], split[1])
        except:
            #print("INFO - no match for unit:", unit)
            return

        s2_sroot = ET.SubElement(s1_root, "Unit", list="true")
        s3_sroot = ET.SubElement(s2_sroot, "UnitType")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = split[0]
        s3_sroot = ET.SubElement(s2_sroot, "UnitNbFractionDigits")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = "3"
        s3_sroot = ET.SubElement(s2_sroot, "UnitNbElt")
        if (unit == "%"):
            s4_sroot = ET.SubElement(s3_sroot, "value")

            s3_sroot = ET.SubElement(s2_sroot, "UnitBase")
            s4_sroot = ET.SubElement(s3_sroot, "value")
            s4_sroot.text = split[1]

            s3_sroot = ET.SubElement(s2_sroot, "UnitToFitTo")
            s4_sroot = ET.SubElement(s3_sroot, "value")

        else:
            s4_sroot = ET.SubElement(s3_sroot, "value")
            s4_sroot.text = "0"

            s3_sroot = ET.SubElement(s2_sroot, "UnitBase")
            s4_sroot = ET.SubElement(s3_sroot, "value")
            s4_sroot.text = split[1]

        s3_sroot = ET.SubElement(s2_sroot, "UnitHeader")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = "true"

        s3_sroot = ET.SubElement(s2_sroot, "UnitCell")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = "true"

        s3_sroot = ET.SubElement(s2_sroot, "UnitYAxis")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = "true"

        s3_sroot = ET.SubElement(s2_sroot, "UnitLegend")
        s4_sroot = ET.SubElement(s3_sroot, "value")
        s4_sroot.text = "true"

        gen_column_threshold(s1_root, order, threshold_list)


def gen_xml_footer(root):
    """

    Args:
        root:

    Returns:

    """

    sroot = ET.SubElement(root, "PortalVersion", list="true")

    s2_sroot = ET.SubElement(sroot, "Version")
    s3_sroot = ET.SubElement(s2_sroot, "value")
    if _get_config('DEFAULT', 'VP_VERSION') != "none":
        s3_sroot.text = str(_get_config('DEFAULT', 'VP_VERSION'))
    else:
        #Failback
        s3_sroot.text = "5.1"


    s2_sroot = ET.SubElement(sroot, "BuildNumber")
    s3_sroot = ET.SubElement(s2_sroot, "value")
    if _get_config('DEFAULT', 'BUILD_NUMBER') != "none":
        s3_sroot.text = str(_get_config('DEFAULT', 'BUILD_NUMBER'))
    else:
        #Failback
        s3_sroot.text = "51029"

    sroot = ET.SubElement(root, "GroupingsLabel", list="true")

    s2_sroot = ET.SubElement(sroot, "DrillDowns", list="true")
    s3_sroot = ET.SubElement(s2_sroot, "DrillDown_1", list="true")
    s4_sroot = ET.SubElement(s3_sroot, "AccessFrom")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "0"

    s4_sroot = ET.SubElement(s3_sroot, "Type")
    s5_sroot = ET.SubElement(s4_sroot, "value")
    s5_sroot.text = "0"

    return sroot
