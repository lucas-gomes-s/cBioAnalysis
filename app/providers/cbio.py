from cgitb import text
import requests
import pandas as pd
import numpy as np
from os.path import exists

BASE_URL = 'https://www.cbioportal.org/api'

response = requests.get(f'{BASE_URL}/studies')
studies = response.json()


def check_attibutes_in_study(study_id):
    response = requests.get(
        f'{BASE_URL}/studies/{study_id}/clinical-attributes'
    )
    clinical_attributes = response.json()
    print(clinical_attributes)
    return clinical_attributes


def check_molecular_profiles_in_study(study_id):
    response = requests.get(
        f'{BASE_URL}/studies/{study_id}/molecular-profiles'
    )
    molecular_profiles = response.json()
    print(molecular_profiles)
    return molecular_profiles


def get_clinical_data_for_study(study_id):
    PATH = f'app/studies/{study_id}-patient-data.pkl'
    if exists(PATH):
        dataframe = pd.read_pickle(PATH)
    else:
        clinical_attributes = check_attibutes_in_study(study_id)
        data = {
            'patientId': [],
        }
        for attribute in clinical_attributes:
            if attribute['patientAttribute']:
                data[attribute['clinicalAttributeId']] = list()

        response = requests.get(f'{BASE_URL}/studies/{study_id}/patients')
        patients = response.json()

        for patient in patients:
            response = requests.get(
                f'{BASE_URL}/studies/{study_id}/patients/{patient["patientId"]}/clinical-data'
            )
            patient = response.json()
            if patient['patientId'] not in data['patientId']:
                data['patientId'].append(patient['patientId'])
            for attribute in patient:
                print(attribute)
                data[attribute['clinicalAttributeId']].append(
                    attribute['value']
                )
            for attribute in data:
                if attribute != 'patientId' and not any(
                    d['clinicalAttributeId'] == attribute for d in patient
                ):
                    print(attribute)
                    data[attribute].append(np.nan)

        dataframe = pd.DataFrame(data)
        dataframe.to_pickle(PATH)

    return dataframe


def write_study_data_to_html(df, html_file):
    html_code = df.to_html()

    text_file = open(f'{html_file}.html', 'w')
    text_file.write(html_code)
    text_file.close()


studies = ['coadread_tcga', 'brca_tcga ', 'skcm_tcga ']

# for study in studies:
#    get_clinical_data_for_study(study)
df = get_clinical_data_for_study(studies[0])
# write_study_data_to_html(df, "main")
#df = check_attibutes_in_study(studies[0])
#prfiles = check_molecular_profiles_in_study(studies[0])
#for prfile in prfiles:
#    print(prfile['molecularProfileId'])
#
#response = requests.get(
#    f'{BASE_URL}/molecular-profiles/coadread_tcga_mrna_median_Zscores/molecular-data'
#)
#data = response.json()
#print(data)
