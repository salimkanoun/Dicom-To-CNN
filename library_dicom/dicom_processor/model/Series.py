import numpy as np
import os

from library_dicom.dicom_processor.model.Instance import Instance
from library_dicom.dicom_processor.model.Modality import *
from library_dicom.dicom_processor.model.NiftiBuilder import NiftiBuilder
from library_dicom.dicom_processor.enums.TagEnum import *
from library_dicom.dicom_processor.enums.SopClassUID import *

class Series():
    """ A class representing a series Dicom
    """
    
    def __init__(self, path):
        """Construct a Dicom Series Object

        Arguments:
            path {String} -- [Absolute Path where Dicom Series is located (hirachical Dicoms)]
        """

        self.path = path
        self.file_names = os.listdir(path)
    
    def get_first_instance_metadata(self):
        firstFileName = self.file_names[0]
        return Instance(os.path.join(self.path,firstFileName), load_image=True)


    def get_series_details(self):
        """Read the first dicom in the folder and store Patient / Study / Series
        informations

        Returns:
            [dict] -- [Return the details of a Serie from the first Dicom]
        """
        self.series_details = {}
        self.patient_details = {}
        self.study_details = {}

        dicomInstance = self.get_first_instance_metadata()

        self.series_details = dicomInstance.get_series_tags()
        self.patient_details = dicomInstance.get_patients_tags()
        self.study_details = dicomInstance.get_studies_tags()
        self.sop_class_uid = dicomInstance.get_sop_class_uid()
        self.is_image_series = dicomInstance.is_image_modality()

        return {
            'series' : self.series_details,
            'study' : self.study_details,
            'patient' : self.patient_details,
            'path' : self.path
        }

    def is_series_valid(self):
        firstDicomDetails = self.get_series_details()
        #Le tag number of slice n'est que pour PT et NM, pas trouvé d'autre tag fiable pour les autres series
        if firstDicomDetails['series']['NumberOfSlices']!="Undefined" and firstDicomDetails['series']['NumberOfSlices'] != len(self.file_names):
            print('wrong number of slice')
            return False

        for fileName in self.file_names:
            dicomInstance = Instance(os.path.join(self.path, fileName), load_image=False)
            if (dicomInstance.get_series_tags()['SeriesInstanceUID'] != firstDicomDetails['series']['SeriesInstanceUID']):
                print('Not same Series Instance UID')
                return False
        
        return True
        
    def is_image_modality(self):
        return self.get_first_instance_metadata().is_image_modality()

    def get_numpy_array(self):
        if self.is_image_series == False : return
        instance_array = [Instance(os.path.join(self.path, file_name), load_image=True) for file_name in self.file_names]
        instance_array.sort(key=lambda instance_array:int(instance_array.get_image_position()[2]), reverse=True)
        pixel_data = [instance.get_image_nparray() for instance in instance_array]
        np_array = np.stack(pixel_data,axis=0)
        #A VERIF
        self.instance_array = instance_array

        return np_array.astype(np.int16)

    def get_z_spacing(self):
        """ called by __getMetadata """
        Z_positions = [ instance.get_image_position()[2] for instance in self.instance_array ]
        
        initial_z_spacing = Z_positions[0]-Z_positions[1]
        for i in range(1,len(Z_positions)):
            z_spacing = Z_positions[i-1]-Z_positions[i]
            if (z_spacing!=initial_z_spacing):
                raise Exception('Unconstant Spacing')
        return initial_z_spacing

    #check origin direction spacing de nifti

    def export_nifti(self, file_path):
        nifti_builder = NiftiBuilder(self)
        nifti_builder.save_nifti(file_path)
