'''
Created on 30.09.2014

@author: yfauser
'''
import xml.etree.ElementTree as ET

def CreateXML(root_object,parameter_list):
    xml_root_object = ET.Element(root_object)
    ParseList(xml_root_object,parameter_list)
    xml_document = ET.tostring(xml_root_object)
    return xml_document
    
def ParseList(xml_root_object,parameter_list):
    # This function will parse through a list containing either a single dictionary entry or another
    # list recursively and create the needed Subitems of the XML Document
    for subitem in parameter_list:
        xml_subitem_name = subitem.keys()[0]
        if type(subitem[xml_subitem_name]) is str:
            xml_subitem = ET.SubElement(xml_root_object,xml_subitem_name)
            xml_subitem.text = subitem[xml_subitem_name]
        elif type(subitem[xml_subitem_name]) is list:
            xml_subitem = ET.SubElement(xml_root_object,xml_subitem_name)
            ParseList(xml_subitem,subitem[xml_subitem_name])
    
          

        
        