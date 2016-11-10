import csv
import os
import xml.etree.ElementTree as ET
from patient import Patient
from brain import Brain
import matplotlib.pyplot as plt
import numpy as np

group_maps = {}  # map from key (group type (i.e. 'M')) to a map for that key (i.e. for males)
patient_map = {}
brain_regions = []


def parse_xml(xml_file):
    # Parses config.xml and sets relevant parameters.
    config = ET.parse(xml_file)
    root = config.getroot()
    # dir to data file
    data_file = root.find('data').text
    # name of subject id variable in data file
    subject_id = root.find('subjectId').text
    # binary variable to define the groups
    group_by = root.find('groups').text
    # variables to be used in analysis
    variables = []
    for variable in root.find('variables').iter('variable'):
        variables.append(variable.text)
    return data_file, subject_id, group_by, variables


def read_file(csv_file):
    # Read in raw data from csv, from path supplied in config.xml
    with open(csv_file, 'r') as f:
        data = [row for row in csv.reader(f.read().splitlines())]
    return data


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def csv_to_map(csv_file, subject_id, group_by):
    data = []
    with open(csv_file) as csvfile:
        # reader = csv.reader(csvfile, dialect=csv.excel_tab)
        reader = read_file(csv_file)
        data = list(reader)

    # data[0] contains all the column names
    data_names = data[0]  # column names from data
    id_index = data[0].index(subject_id);
    group_index = data[0].index(group_by);

    # for each patient
    for row in data[1:]:

        row_id = row[id_index]
        row_group = row[group_index]
        row_data = {}
        # row_data is map from name of brain region (string) to its value (float)
        for i in range(0, len(row)):
            if (data_names[i] in brain_regions):
                if (isfloat(row[i])):
                    row_data[data_names[i]] = float(row[i])
                else:
                    row_data[data_names[i]] = float("inf")

        # add new patient to patient_map
        patient_map[row_id] = Patient(row_id, row_group, row_data)

        # update group's map
        update_map(row_data, row_group)


def update_map(data_map, which_group):
    if not group_maps.has_key(which_group):
        group_maps[which_group] = {}

    update = group_maps[which_group]

    for key in data_map.keys():
        if not update.has_key(key):
            update[key] = [];
        update[key].append(float(data_map[key]))


if __name__ == "__main__":

    data_file, subject_id, group_by, variables = parse_xml('config.xml')
    brain_regions = variables
    csv_to_map(data_file, subject_id, group_by)

    b = Brain(group_maps['F'], group_maps['M'])
    b.setEndPercentage(1.0 / 4.0)

    # Calculate log likelihood ratios and export in excel file
    ratio_data = []

    column_names = ['SubjectId', 'Gender'] + sorted(group_maps['F'].keys())

    ratio_data.append(column_names)

    patient_ids = patient_map.keys()

    patient_map[patient_ids[1]].plotProbDensity(group_maps['F'], group_maps['M'])

    for patient_id in patient_ids:
        ratio_patient = []
        ratio_patient.append(float(patient_id))
        ratio_patient.append(patient_map[patient_id].getGender())
        patient_data = patient_map[patient_id].genderLikelihood(group_maps['F'], group_maps['M'])
        for i in range(len(column_names[2:])):
            ratio_patient.append(patient_data[column_names[i + 2]])
        ratio_data.append(ratio_patient)

    ratio_data[1:] = sorted(ratio_data[1:], key=lambda sl: (sl[1], sl[0]))

    with open('results/loglikelihood.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(ratio_data)

    f.close()