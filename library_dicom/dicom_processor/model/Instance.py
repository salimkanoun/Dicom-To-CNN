import pydicom
import os
import numpy as np

from library_dicom.dicom_processor.enums.TagEnum import *
from library_dicom.dicom_processor.enums.SopClassUID import *

class Instance:
    """A class to represent a Dicom file 
    """

    def __init__(self, path, load_image=True):
        """Construct a Dicom file object

        Arguments:
            path {[String]} -- [Absolute path where the Dicom file is located]
        """
        self.path = path
        if (load_image) : self.__load_full_instance()
        else : self.__load_metadata()

    def __load_metadata(self):
        self.dicomData = pydicom.dcmread(self.path, stop_before_pixels=True)
    
    def __load_full_instance(self):
        self.dicomData = pydicom.dcmread(self.path)
  
    def get_series_tags(self):
        series_tags={}
        for tag_address in TagsSeries:
            if tag_address.value in self.dicomData : series_tags[tag_address.name] = self.dicomData[tag_address.value].value
            else : series_tags[tag_address.name] = "Undefined"
        return series_tags

    def get_patients_tags(self):
        patient_tags={}
        for tag_address in TagsPatient:
            if tag_address.value in self.dicomData : 
                patient_tags[tag_address.name] = self.dicomData[tag_address.value].value
                if( type(self.dicomData[tag_address.value].value) != str):
                    #patient name return PersonName3 object, convert it to string
                    patient_tags[tag_address.name] = str(patient_tags[tag_address.name])
            else : patient_tags[tag_address.name] = "Undefined"
        return patient_tags

    def get_studies_tags(self):
        studies_tags={}
        for tag_address in TagsStudy:
            if tag_address.value in self.dicomData : studies_tags[tag_address.name] = self.dicomData[tag_address.value].value
            else : studies_tags[tag_address.name] = "Undefined"
        return studies_tags

    def get_instance_tags(self):
        instance_tags={}
        for tag_address in TagsInstance:
            if tag_address.value in self.dicomData : instance_tags[tag_address.name] = self.dicomData[tag_address.value].value
            else : instance_tags[tag_address.name] = "Undefined"
        return instance_tags

    def get_sop_class_uid(self):
        if 'SOPClassUID' in self.dicomData.dir() : return self.dicomData.SOPClassUID
        else : raise Exception('Undefined SOP Class UID')

    def get_radiopharmaceuticals_tags(self):
        radiopharmaceuticals_tags={}
        radiopharmaceutical_sequence = []

        try :
            radiopharmaceutical_sequence = self.dicomData[0x00540016][0]
        except Exception: 
            print("no Radiopharmaceuticals tags")

        for tag_address in TagsRadioPharmaceuticals:
            if tag_address.value in radiopharmaceutical_sequence : radiopharmaceuticals_tags[tag_address.name] = radiopharmaceutical_sequence[tag_address.value].value
            else : radiopharmaceuticals_tags[tag_address.name] = "Undefined"

        return radiopharmaceuticals_tags

    def get_pet_correction_tags(self):
        if TagPTCorrection.CorrectedImage.value in self.dicomData :
            return list(self.dicomData[TagPTCorrection.CorrectedImage.value].value)
        else: return "Undefined"
    
    def get_philips_private_tags(self):
        philips_tags={}
        for tag_address in philips_tags:
            if tag_address.value in self.dicomData : 
                philips_tags[tag_address.name] = float(self.dicomData[tag_address.value].value)
            else : philips_tags[tag_address.name] = "Undefined"
        return philips_tags

    def is_secondary_capture(self):
        return True if self.get_sop_class_uid in CapturesSOPClass else False

    def is_image_modality(self):
        return True if self.get_sop_class_uid in ImageModalitiesSOPClass else False

    def __get_rescale_slope(self):
        return self.dicomData[TagsInstance.RescaleSlope.value].value

    def __get_rescale_intercept(self):
        return self.dicomData[TagsInstance.RescaleIntercept.value].value

    def get_image_orientation(self):
        return self.dicomData[TagsInstance.ImageOrientation.value].value
    
    def get_image_position(self):
        return self.dicomData[TagsInstance.ImagePosition.value].value

    def get_pixel_spacing(self):
        return self.dicomData[TagsInstance.PixelSpacing.value].value

    def is_image_modality(self):
        sop_values = set(item.value for item in ImageModalitiesSOPClass)
        return True if self.get_sop_class_uid() in sop_values else False

    def get_image_nparray(self):
        if self.is_image_modality() == False : 
            raise Exception('Not Image Modality')
        else:
            pixel_array = self.dicomData.pixel_array
            rescale_slope = self.__get_rescale_slope()
            rescale_intercept = self.__get_rescale_intercept()

            resultArray = ( pixel_array * rescale_slope) + rescale_intercept
            return resultArray
    
    