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


def get_clinical_data_for_study(study_id):
    PATH = f'../studies/{study_id}-patient-data.pkl'
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
            for attribute in patient:
                data[attribute['clinicalAttributeId']].append(
                    attribute['value']
                )
            for attribute in data:
                if not any(
                    d['clinicalAttributeId'] == attribute for d in patient
                ):
                    print(attribute)
                    data[attribute].append(np.nan)

        dataframe = pd.DataFrame(data)
        dataframe.to_pickle(PATH)

    return dataframe


studies = ['coadread_tcga', 'brca_tcga ', 'skcm_tcga ']

# for study in studies:
#    get_clinical_data_for_study(study)
# df = get_clinical_data_for_study(studies[0])
df = check_attibutes_in_study(studies[0])
print(df)
