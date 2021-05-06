from json import dumps, loads
from requests import get

my_dict  = dict(
    patient = None,# f{Patient['name'][0]['given'][0]} {Patient['name']['family']}
    encounter_type = None,# Encounter['type'][0]['text'],
    encounter_class = None,# Encounter['class']['code'],
    encounter_reason = None,# ,
    encounter_time = None,# Encounter['period']['start'],
    encounter_diagnosis = None,# Condition['code']['text'],
    discharge_disposition = None,# ,
    payer = None,# Coverage['payor'][0]['display'],
    provider = None,# f{Practitioner['name'][0]['given'][0]} {Practitioner['name']['family']}
    provider_organization = None,# Organization['name']
    location = None,# Location[0]['location']['name']
  )

def get_res(my_base,my_type,my_id, my_params=None,):
    '''
    use value to   get data through a series of Gets
    and return as a table of data
    '''
    enc = get(url=f'{my_base}/{my_type}/{my_id}', params=my_params)
    return enc.json()


def enc_data(my_type,my_id,my_base,):

    #for k,v in my_dict.items():
        #print(f'{k} = {v}')

    enc = get_res(my_base,my_type,my_id)
    #print(enc)

    try:
        my_dict["encounter_type"] = enc['type'][0]['text']
    except KeyError:
        my_dict["encounter_type"] = None
    try:
        my_dict["encounter_class"] = enc['class']['code']
    except KeyError:
        my_dict["encounter_class"] = None
    try:
        my_dict["encounter_time"] = enc['period']['start']
    except KeyError:
        my_dict["encounter_time"] = None
    try:
        my_dict["encounter_reason"] = enc['reason']
    except KeyError:
        my_dict["encounter_reason"] = None
    try:
        my_dict["discharge_disposition"] = enc['dd']
    except KeyError:
        my_dict["discharge_disposition"] = None

    my_type = "Patient"
    my_id = enc['subject']['reference'].split('/')[-1]
    pat = get_res(my_base,my_type,my_id)
    #print(pat)
    try:
        my_dict["patient"] = f"{pat['name'][0]['given'][0]} {pat['name'][0]['family']}"
    except KeyError:
        my_dict["patient"] = None

    my_type = "Practitioner"
    my_id = enc['participant'][0]['individual']['reference'].split('/')[-1]
    pract = get_res(my_base,my_type,my_id)
    #print(pract)
    try:
        my_dict["practitioner"] = f"{pract['name'][0]['given'][0]} {pract['name'][0]['family']}"
    except KeyError:
        my_dict["practitioner"] = None

    my_type = "Location"
    my_id = enc['location'][0]['location']['reference'].split('/')[-1]
    loc = get_res(my_base,my_type,my_id)
    #print(loc)
    try:
        my_dict["location"]= loc['location']['name']
    except KeyError:
        my_dict["location"] = None


    my_type = "Organization"
    my_id = enc['serviceProvider']['reference'].split('/')[-1]
    org = get_res(my_base,my_type,my_id)
    #print(loc)
    try:
        my_dict["provider_organization"]= org['name']
    except KeyError:
        my_dict["provider_organization"] = None

    my_type = "Condition"
    my_id = ''
    cond = get_res(my_base,my_type,my_id,my_params={'encounter':enc['id'],'patient':pat['id']},)
    cond=cond['entry'][0]['resource']
    try:
        my_dict["encounter_diagnosis"]= cond['code']['text']
    except KeyError:
        my_dict["encounter_diagnosis"] = None

    my_type = "Coverage"
    my_id = ''
    cov = get_res(my_base,my_type,my_id,my_params={'patient':pat['id']},)
    cov=cov['entry'][0]['resource']
    try:
        my_dict["payer"]= cov['payor'][0]['display']
    except KeyError:
        my_dict["payer"] = None

    out = ""
    for k,v in my_dict.items():
        out = out + f"- {k.replace('_',' ').title()} = {v}\n"
    return out

def main():
    my_type = "Encounter"
    my_id = "2081026"
    my_base = "http://hapi.fhir.org/baseR4"
    print(enc_data(my_type,my_id,my_base,))

# run app
if __name__ == '__main__':
    main()
