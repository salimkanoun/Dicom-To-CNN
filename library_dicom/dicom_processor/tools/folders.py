import os

def get_series_path(path):
    """Go through all the folder to find every series path

    Arguments:
        path {[string]} -- [Absolute path where the repertory is located]

    Returns:
        [list] -- [Path's list of every series]
    """

    seriesPath = []
    for (path, dirs, files) in os.walk(path): 
        if not (dirs) :
            seriesPath.append(path)
    return seriesPath

def write_json_file(path, file_name, content, extension = 'json'):
    wrinting_file = open(os.path.join(path, file_name+'.'+extension), 'w')
    wrinting_file.write(content)
    wrinting_file.close()

def remove_bi_file(path):
    file_names = os.listdir(path)
    if('graphic.brownFat.gr2' in file_names):
        os.remove( os.path.join(path,"graphic.brownFat.gr2") )