import csv

"""CSV Parser for CSV generated by petctviewer.org

Returns:
    [CsvReader] -- [CSV Parser]
"""
class CsvReader():


    def __init__(self, path):
        self.path=path
        self.__load_data()
        self.details_rois = self.get_csv_roi_details()

    def __load_data(self):
        """Load data in this object, during reading, search
        for manual and automatic (nifti) roi declaration part
        """
        with open(self.path, 'r') as csvfile : 
            reader = csv.reader(csvfile)
            csv_data = []
            index = 0
            for row in reader :
                if(row and 'Number of ROIs = ' in row[0]) :
                    number_of_manual_roi = row[0].replace("Number of ROIs = ", "").strip()
                    self.first_line_manual_roi = index
                    self.number_of_manual_roi = int(number_of_manual_roi)
                    #self.number_of_nifti_roi = 0
                if(row and 'Number of Nifti ROIs = ' in row[0]) :
                    number_of_nifti_roi = row[0].replace("Number of Nifti ROIs = ", "").strip()
                    self.first_line_nifti_roi = index
                    self.number_of_nifti_roi = int(number_of_nifti_roi) 
                    #self.number_of_manual_roi = 0 
                csv_data.append(row) #liste de liste(chaque ligne = liste)
                index += 1

        self.csv_data = csv_data

    def get_rois_results(self):
        """Return CSV lines containing ROIs results
        """
        return self.csv_data[1 : self.csv_data.index([]) - 2 ]
    

    def get_manual_rois(self):
        """return manual rois block
        """

        try :
            first_manual_roi = self.first_line_manual_roi + 1
        except AttributeError:
            return ([])
        
        last_manual_row =  first_manual_roi + self.number_of_manual_roi
        return self.csv_data[ first_manual_roi : last_manual_row ]

    def get_nifti_rois(self):
        """ return automatic (nifti) roi block
        """
        
        try :
            first_nifti_row = self.first_line_nifti_roi + 1
        except AttributeError:
            return ([])
        
        nifti_roi_bloc = self.csv_data[first_nifti_row : ] 
        nifti_roi_bloc = nifti_roi_bloc[0 : nifti_roi_bloc.index([])]
        nifti_roi_list = []
        for row in nifti_roi_bloc :
            if "num points = " in row[1] : 
                nifti_roi_list.append(row)
            else : 
                nifti_roi_list[-1] = nifti_roi_list[-1] + row

        return nifti_roi_list


    def get_SUL(self):
        """return the SUL value of the CSV

        """
        sul =  self.csv_data[0 :  self.csv_data.index([])]
        return float(sul[-1][3])


    def get_SUVlo(self):
        """ return the SUVlo value of the CSV

        """
        last_row = self.csv_data[-1]
        return last_row[0]

    @classmethod 
    def convert_manual_row_to_object(cls, manual_row, results_row):
        """Return a row manual row in an object with ROI details

        Arguments:
            manual_row {list} -- raw, row manual row

        Returns:
            [object] -- object describing the row

        """

        number_point_field = manual_row[4]
        number_point = int( number_point_field.replace(" num points = ", "").strip() )
        point_list_string = manual_row[ 5 : (5 + number_point) ]
        point_list = CsvReader.list_string_to_point_list_int( point_list_string )

        result_answer = {
                'name' : manual_row[0].strip(),
                'roi_number' : results_row[1],
                'first_slice' : int(manual_row[2].strip()),
                'last_slice' : int(manual_row[3].strip()),
                'type_number' : int(manual_row[1].strip()),
                'point_list' : point_list,
                'suv_mean' : results_row[5],
                'sd' : results_row[6],
                'suv_max' : results_row[11]
        }

        return result_answer


    @classmethod
    def convert_nifti_row_to_object(cls, nifti_row, results_row):
        """Return list of point included in the roi

        Arguments:
            nifti_row {list} -- nifti row of the csv

        Returns:
            [list] -- list of point in the roi
        """
        point_list_string = nifti_row[2:]
        point_list = CsvReader.list_string_to_point_list_int( point_list_string )
        result_answer = {
                'name' : nifti_row[0].strip(),
                'roi_number' : results_row[1],
                'first_slice' : 0,
                'last_slice' : 0,
                'type_number' : 0,
                'point_list' : point_list,
                'suv_mean' : results_row[5],
                'sd' : results_row[6],
                'suv_max' : results_row[11]
        }
        return result_answer

    @classmethod
    def list_string_to_point_list_int(cls, point_list_string):
        """
        Transforms point string into list of coordinate (int)
        """
        point_list_string = list(map(str.strip, point_list_string))
        point_list = []
        for point_string in point_list_string:
            list_string_point = point_string.split()
            list_int_point = list(map(int, list_string_point))
            point_list.append(list_int_point)
        return point_list


    def get_csv_roi_details(self):
        """return a dict with each ROI information to build the mask

        """

        rois_results = self.get_rois_results()
        manual_rois = self.get_manual_rois() #list vide si pas de manual
        number_of_manual_rois = len(manual_rois)
        nifti_rois = self.get_nifti_rois() #list vide si pas de nifti
        number_of_nifti_rois = len(nifti_rois)
        details = {}


        for number_roi_nifti in range(number_of_nifti_rois) :
            details[number_roi_nifti + 1] = self.convert_nifti_row_to_object(nifti_rois[number_roi_nifti], rois_results[number_roi_nifti])
        for number_roi_manual in range(number_of_manual_rois):
            details[number_of_nifti_rois + 1 + number_roi_manual]  = self.convert_manual_row_to_object(manual_rois[number_roi_manual], rois_results[number_of_nifti_rois + 1 + number_roi_manual])


        details['SUL'] = self.get_SUL()
        details['SUVlo'] = self.get_SUVlo()
        return details 