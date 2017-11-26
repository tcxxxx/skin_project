#!/usr/bin/python

import os
import sys
from PIL import Image
 
# target_diseases_shouldBePassedIn = ['Ingrowneyelash', 'Acne','rosacea', 'Disease1ForTest', 'Disease2ForTest', 'Disease3ForTest']

def backup_datasetTxt():
    pass

def match_diseaseNames_to_datasets(path):
    '''
    This function directs disease names to datasets
    '''
    extension = ".txt"
    disease_dict = {} # disease_name: datasets directory
    temp = ''
    for item in os.listdir(path):
        if extension in item:
        	# The end of each disease files are always: -($TIMESTAMP).txt
        	# for example: melanoma-1507572279.txt, Ingrown-Eyelash-1507728821.txt
        	# So the part before the dot should be: DISEASE-TIMESTAMP
            disease_name = item.split('.')[0][:-11]
            disease_name = temp.join(disease_name.split('-'))
            disease_dict[disease_name.lower()] = item[:-4]
    return disease_dict

def tag_disease(target_diseases):
    path = str(os.getcwd() + '/dataset')
    extension = ".txt"
    lines = []
    skinLines = []
    disease_dict = match_diseaseNames_to_datasets(path)

    skin_path = str(os.getcwd() + '/dataset/normalskin.txt')
    with open(skin_path, 'r+') as sF:
        skinLines.append(sF.readlines())

    for d in target_diseases:
        if d.lower() in disease_dict.keys():
            disease_dir = disease_dict[d.lower()]
            with open(path + '/' + disease_dir + extension, 'r+') as F: 
                lines.append(F.readlines())  	
        else:
            # Add downloading later.
            pass
            
    backup_datasetTxt()
    with open('./' + 'dataset' + extension, 'w+') as F:
        for s in skinLines[0]:
            F.write(s.strip('\n') + " " + str('0') + "\n")

        for tagNum in range(0, len(lines)):
            for i in lines[tagNum]:
                F.write(i.strip('\n') + " " + str(tagNum + 1) + "\n")

def match_symptomNames_to_datasets(path):
    extension = ".txt"
    symptom_dict = {}
    temp = ''
    for item in os.listdir(path):
        # here we filter all the files
        if extension in item:
            symptom_name = item.split('.')[0][:-11]
            symptom_name = temp.join(symptom_name.split('-'))
            symptom_dict[symptom_name.lower()] = item[:-4]
    return symptom_dict

def tag_symptoms(target_symptoms):
    path = str(os.getcwd() + '/dataset/sub_datasets')
    extension = ".txt"
    symptom_dict = match_symptomNames_to_datasets(path)
    print symptom_dict
    print target_symptoms
    num = 0
    
    for set in target_symptoms:
        dict_list = []
        lines = []
        skinLines = []

        skin_path = str(os.getcwd() + '/dataset/normalskin.txt')
        with open(skin_path, 'r+') as sF:
            skinLines.append(sF.readlines())

        for s in set:
            s = ''.join(s.strip().split())
            symptom_dir = symptom_dict[s.lower()]
            with open(path + '/' + symptom_dir + extension, 'r+') as F:
                lines.append(F.readlines())

        print "num: " + str(num)
        num += 1

        with open('./' + 'sub_file' + str(num) + extension, 'w+') as F:
            for s in skinLines[0]:
                F.write(s.strip('\n') + " " + str('0') + "\n")

            for setNum in range(0, len(lines)):
                # for fileNum in range(0, len(lines[setNum])):
                for i in lines[setNum]:
                    F.write(i.strip('\n') + " " + str(num) + "\n")
    
    '''
    for num in range(1, 4):
        with open('./' + 'sub_file' + str(num) + extension, 'w+') as F:
            for i in lines[0]:
                F.write(i.strip('\n') + " " + str('0') + "\n")
    '''


def generate_file_list(root_dir, label=1):
    standardFormat = ['jpg', 'jpeg', 'png']
    # name = root_dir.split('/')[1]
    name = root_dir + ".txt"
    item_list = []
    root_dir = os.getcwd() + "/" + root_dir

    for img_dir_no in os.listdir(root_dir):
        img_dir = os.path.join(root_dir, img_dir_no)
        img_dir_similar = os.path.join(img_dir, "similar_images")
        
        if '.DS_Store' in img_dir:
            continue

        for item in os.listdir(img_dir):
            try:
                if item == "similar_images":
                    item_dir = img_dir + "/" + item
                    num = 0
                    for simi_imgs in os.listdir(item_dir):
                        item_path = item_dir + "/" + simi_imgs
                        if any(ext in item_path for ext in standardFormat):
                            try:
                                tempF = Image.open(item_path)
                                tempF.load()
                            except Exception as e:
                                print e
                                print(item_path)
                                os.remove(item_path)
                                pass
                            else:
                                statinfo = os.stat(item_path)
                                if statinfo.st_size >= 7300:
                                    item_list.append(item_path)
                else:
                    pass
            except:
                pass
    # funny error0: f.close() 
    with open(name, "w") as F:
        for item in item_list:
            F.write(item + '\n')
    return

def checkCurrentData(query):
    """
    """
    extension = ".txt"
    dataset_dir = os.getcwd() + "/dataset/sub_datasets"
    dir_list = os.listdir(dataset_dir)
    dir_for_query = ''

    for item in dir_list:
        item = item.lower()
        if (query.lower() in item) and (extension in item):
            dir_for_query = item.split('.')[0]
    
    if len(dir_for_query) != 0:
        generate_file_list('dataset/sub_datasets/' + dir_for_query, label=1)        
        return True

def add_humanSkin():
    return

if __name__ == "__main__":
    target_diseases_list = []
    target_symptoms_list = []

    disease_num = len(sys.argv) - 1
    print "number of diseases:" + str(disease_num)
    
    file = open('sub.list')
    sub_list = file.readlines()
    for dNo in range(1, disease_num + 1):
        symptoms_list = []
        print sys.argv[dNo].strip(',')
        
        for symptom in sub_list:
            if str(dNo) in symptom:
                symptoms_list.append(symptom[2:].strip('\n'))

        target_diseases_list.append(sys.argv[dNo].strip(','))
        target_symptoms_list.append(symptoms_list)
    file.close()
    '''
    print "\ndiseases: "
    print target_diseases_list
    print "\nsymptoms: "
    print target_symptoms_list
    '''
    for set in target_symptoms_list:
        for symptom in set:
            checkCurrentData(symptom.replace(" ", ""))
    
    generate_file_list('dataset/normalskin', label=1)
    # tag diseases:
    tag_disease(target_diseases_list)
    # tag symptoms:
    tag_symptoms(target_symptoms_list)

