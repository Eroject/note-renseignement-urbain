from arcpy import *
import json
import pandas as pd
import io

#Paramètres entrés par l'utilisateur

json=GetParameterAsText(0)
PersonalGDB= GetParameterAsText(1)


#processing functions
def JsonToFeatureclass(jso,PersonalGDB):
    L=jso.split('\\')
    nomdelacouche=L[-1].split('.')[0]
    field_interdi=['OBJECTID','shape','shape_length','shape_Area','ID','ZONE']
    field_remplacant=['OBJECTID_copy','shape_copy','shape_length_copy','shape_Area_copy','ID_copy','ZONE_COPY']
    with io.open(jso,encoding='UTF-8') as j:
        d = json.load(j)
    L=[]
    for cle in d['features']:
        A=Array()
        for pt in cle['geometry']['rings'][0] :
            A.append(Point(pt[0],pt[1],0,0))
        cle['attributes']['shape@']=A
        L.append(cle['attributes'])
    try:
        CreateFeatureclass_management(out_path=PersonalGDB, out_name=nomdelacouche,         geometry_type='POLYGON',spatial_reference=d['spatialReference']['wkid'])
    except:
        Delete_management(os.path.join(PersonalGDB,nomdelacouche))
        CreateFeatureclass_management(out_path=PersonalGDB, out_name=nomdelacouche, geometry_type='POLYGON',spatial_reference=d['spatialReference']['wkid'])

    typ={}
    typ['OID']='LONG'
    typ['Double']='DOUBLE'
    typ['String']='TEXT'
    for field in d['fields']:
        if field['name'] not in field_interdi:
            AddField_management(in_table=os.path.join(PersonalGDB,nomdelacouche), field_name=field['name'], field_type=typ[field['type'][13:]], field_alias=field['alias'])
        else:
            indice=field_interdi.index(field['name'])
            AddField_management(in_table=os.path.join(PersonalGDB,nomdelacouche), field_name=field_remplacant[indice], field_type=typ[field['type'][13:]], field_alias=field['alias'])


    interdit=['activationTime','changeTime','creationTime','shape@']
    for i in range(0,len(d['features'])):
        champ=[]
        fields=[]
        for j in range(0,16) :
            if L[i].keys()[j] not in interdit:
                if L[i].keys()[j] not in field_interdi:
                    champ.append(L[i][(L[i].keys())[j]])
                else:
                    fields.append(L[i].keys()[j])
                    indice2=field_interdi.index(L[i].keys()[j])
                    champ.append(L[i][(L[i].keys())[j]])
                    fields.append(field_remplacant[indice2])
        champ.append(Polygon(L[i]['shape@']))
        fields.append('shape@')
        with da.InsertCursor(os.path.join(PersonalGDB,nomdelacouche),fields) as cursor:
            cursor.insertRow(champ)


#############################################################################################################

JsonToFeatureclass(json,PersonalGDB)