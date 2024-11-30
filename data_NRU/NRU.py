# -*- coding: ... -*-
from arcpy import *
from arcpy.mapping import *
import os

############workspace######################

env.workspace=r'C:\Users\lenovo\Desktop\projets_total\projet_SIC_NRU\SIG NRU\NRU\data_NRU'

#Parametres entres par l'utilisateur

Date_demande=GetParameterAsText(0)
Numero_demande= GetParameterAsText(1)
Nom_demandeur=GetParameterAsText(2)
fichiertexte=GetParameterAsText(3)
outfolder=GetParameterAsText(4)


#Definition des parametres
mxdpath=os.path.join(env.workspace,'txt.mxd')
mxd=MapDocument(mxdpath)


#processing functions
def textToFeatureClass(outpath,fichiertexte,separateur):
    Featurepath=outpath
    env.workspace=Featurepath
    A=Array()
    occ=0
    with open(fichiertexte,'r') as fh:
        lignes=fh.readlines()[1:]
        n=len(lignes)
        for ligne in lignes:
            occ=occ+1
            x=ligne.split(separateur)[1]
            if occ!=n:
                y=ligne.split(separateur)[2][:-1]
            else:
                y=ligne.split(separateur)[2]
            A.append(Point(x,y))

    try:
        CreateFeatureclass_management(out_path=Featurepath, out_name='parcelle', geometry_type='POLYGON',  spatial_reference=26191)
    except:
        Delete_management(os.path.join(Featurepath,'parcelle'))
        CreateFeatureclass_management(out_path=Featurepath, out_name='parcelle', geometry_type='POLYGON',  spatial_reference=26191)

    with da.InsertCursor('parcelle',['Shape@']) as cursor:
        cursor.insertRow([Polygon(A)])
'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def superficieparcelle(parcelle):# return la superficie d'une parcelle
    with da.SearchCursor(parcelle,['shape@']) as cursor:
        for row in cursor:
            return row[0].getArea(units='METERS')


def totoutside(parcelle,Zone,MDB):#verifie si  parcelle est totalement hors  zone ou pas
    try:
        Intersect_analysis([parcelle,Zone],os.path.join(MDB,'intersect'))
    except:
        Delete_management(os.path.join(MDB,'intersect'))
        Intersect_analysis([Zone,parcelle],os.path.join(MDB,'intersect'))
    with da.SearchCursor(os.path.join(MDB,'intersect'),['shape@']) as cursor:
        occ=0
        for row in cursor:
            occ=occ+1
    if occ>=1:
        Delete_management(os.path.join(MDB,'intersect'))
        return False # soit partiellement inside soit totlaement  inside
    else:
        Delete_management(os.path.join(MDB,'intersect'))
        return True
'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def ZoneSecteur(parcelle,Zone,MDB):#return un tuple compose de deux liste ,la premiere donne les secteurs
    secteur=[]
    zone=[]
    superficIntersect=[]
    try:
        Intersect_analysis([parcelle,Zone],os.path.join(MDB,'intersect'))
    except:
        Delete_management(os.path.join(MDB,'intersect'))
        Intersect_analysis([Zone,parcelle],os.path.join(MDB,'intersect'))
    try:
        Dissolve_management(in_features=os.path.join(MDB,'intersect'), out_feature_class=os.path.join(MDB,'dissolvezone'), dissolve_field='ZONE_COPY')

    except:
        Delete_management(os.path.join(MDB,'dissolvezone'))
        Dissolve_management(in_features=os.path.join(MDB,'intersect'), out_feature_class=os.path.join(MDB,'dissolvezone'), dissolve_field='ZONE_COPY')
    with arcpy.da.SearchCursor(os.path.join(MDB,'dissolvezone'), ["ZONE_COPY","Shape_Area"]) as cursor:
        for row in cursor:
            zone.append((row[0],row[1]))
    Delete_management(os.path.join(MDB,'dissolvezone'))
    try:
        Dissolve_management(in_features=os.path.join(MDB,'intersect'), out_feature_class=os.path.join(MDB,'dissolvesecteur'), dissolve_field='SECTEUR')

    except:
        Delete_management(os.path.join(MDB,'dissolvesecteur'))
        Dissolve_management(in_features=os.path.join(MDB,'intersect'), out_feature_class=os.path.join(MDB,'dissolvedecteur'), dissolve_field='SECTEUR')
    with arcpy.da.SearchCursor(os.path.join(MDB,'dissolvesecteur'), ["SECTEUR","Shape_Area"]) as cursor:
        for row in cursor:
            secteur.append((row[0],row[1]))

    superficIntersect.append(superficieparcelle(os.path.join(MDB,'intersect')))
    Delete_management(os.path.join(MDB,'intersect'))
    Delete_management(os.path.join(MDB,'dissolvesecteur'))

    return(secteur,zone,superficIntersect[0])

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''

def IsInside(parcelle,Zone,MDB):#est inside totalement
    try:
        Intersect_analysis([parcelle,Zone],os.path.join(MDB,'intersect'))
    except:
        Delete_management(os.path.join(MDB,'intersect'))
        Intersect_analysis([Zone,parcelle],os.path.join(MDB,'intersect'))
    polygone_reference= os.path.join(MDB,'intersect')
    polygone_test= parcelle
    poly_test_lyr=mapping.Layer(polygone_test)
    poly_ref_lyr=mapping.Layer(polygone_reference)
    with arcpy.da.SearchCursor(poly_test_lyr, ["SHAPE@"]) as cursor:
        for row in cursor:
            if poly_ref_lyr.getSelectedExtent().contains(row[0]):#teste si la parcelle est totalement inside avec l intersection(dans notre cas elles vont etre confondue)
                Delete_management(os.path.join(MDB,'intersect'))
                return True
            else:
                Delete_management(os.path.join(MDB,'intersect'))
                return False #la parcelle contient totzlement l intersection

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''

def casetdetail(parcelle,Zone,MDB):#donne les cas selon la position de la parcelle (d'apres l'enonce)
    if totoutside(parcelle,Zone,MDB)==True:
        return (3,superficieparcelle(parcelle))
    if IsInside(parcelle,Zone,MDB)==True and totoutside(parcelle,Zone,MDB)==False:
        if len(ZoneSecteur(parcelle,Zone,MDB)[0])==1:
            return (1,(ZoneSecteur(parcelle,Zone,MDB)[0][0],ZoneSecteur(parcelle,Zone,MDB)[1][0],superficieparcelle(parcelle)))
        else:
            return (2,(ZoneSecteur(parcelle,Zone,MDB)[0],ZoneSecteur(parcelle,Zone,MDB)[1]),superficieparcelle(parcelle))
    if IsInside(parcelle,Zone,MDB)==False and totoutside(parcelle,Zone,MDB)==False:
        superext=superficieparcelle(parcelle)-ZoneSecteur(parcelle,Zone,MDB)[2]
        try:
            Intersect_analysis([parcelle,Zone],os.path.join(MDB,'intersectintersect'))
        except:
            Delete_management(os.path.join(MDB,'intersectintersect'))
            Intersect_analysis([Zone,parcelle],os.path.join(MDB,'intersectintersect'))
        intersect=os.path.join(MDB,'intersectintersect')
        if casetdetail(intersect,Zone,MDB)[0]==1:
            return (4,(ZoneSecteur(parcelle,Zone,MDB)[2],superext), casetdetail(intersect,Zone,MDB))
        if casetdetail(intersect,Zone,MDB)[0]==2:
            return (4,(ZoneSecteur(parcelle,Zone,MDB)[2],superext), casetdetail(intersect,Zone,MDB))

#ZoneSecteur(parcelle,Zone,MDB)[2] superficie a l'interieur
def NRU(Date_demande,Numero_demande,Nom_demandeur,fichiertexte,out_folder,mxd):#fonction final
    try:
        CreatePersonalGDB_management(out_folder_path=out_folder, out_name="projet")
    except:
        Delete_management(os.path.join(out_folder,"projet.mdb"))
        CreatePersonalGDB_management(out_folder_path=out_folder, out_name="projet")
    MDB=os.path.join(out_folder,"projet.mdb")
    textToFeatureClass(MDB,fichiertexte,";")
    mxd2=MapDocument(r'map.mxd')
    Zone=r'projet.mdb\zone'
    parcelle=r'projet.mdb\parcelle'
    cas=casetdetail(parcelle,Zone,MDB)
    if cas[0]==1:
        reponse1(Date_demande,Numero_demande,Nom_demandeur,cas,mxd)
    if cas[0]==2:
        reponse2(Date_demande,Numero_demande,Nom_demandeur,cas,mxd)
    if cas[0]==3:
        reponse3(Date_demande,Numero_demande,Nom_demandeur,cas,mxd)
    if cas[0]==4:
        if cas[2][0]==1:
            reponse41(Date_demande,Numero_demande,Nom_demandeur,cas,mxd)
        if cas[2][0]==2:
            reponse42(Date_demande,Numero_demande,Nom_demandeur,cas,mxd)
    supprimerlayers(mxd2)
    ajouterlayers(mxd2,parcelle,Zone)
    ExportToPDF(mxd,os.path.join(out_folder,"texte2.pdf"))
    ExportToPDF(mxd2,os.path.join(out_folder,"Map2.pdf"))
    try:
        PDF1=PDFDocumentCreate(os.path.join(out_folder,"NRU.pdf"))
    except:
        Delete_management(os.path.join(out_folder,"NRU.pdf"))
        PDF1=PDFDocumentCreate(os.path.join(out_folder,"NRU.pdf"))
    PDF1=PDFDocumentCreate(os.path.join(out_folder,"NRU.pdf"))
    PDF1.appendPages(os.path.join(out_folder,"texte2.pdf"))
    PDF1.appendPages(os.path.join(out_folder,"Map2.pdf"))
    Delete_management(os.path.join(out_folder,"projet.mdb"))
    Delete_management(os.path.join(out_folder,"texte2.pdf"))
    Delete_management(os.path.join(out_folder,"Map2.pdf"))

#mapping
def supprimerlayers(mxd):#fonction qui supprime toutes les couches
    n=len(ListDataFrames(mxd))
    for i in range (n):
        df=ListDataFrames(mxd)[i]
        m=len(ListLayers(mxd, data_frame=df))
        if m>0:
            for j in range (m):
                layers=ListLayers(mxd, data_frame=df)[0]
                arcpy.mapping.RemoveLayer(df, layers)
                m=len(ListLayers(mxd, data_frame=df))

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def ajouterlayers(mxd,plot_path,zone_path):#fonction qui ajoute les couches souhaitees et zoome sur la couche parcelle
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    zone_layer = arcpy.mapping.Layer(zone_path)
    arcpy.mapping.AddLayer(df, zone_layer)
    plot_layer = arcpy.mapping.Layer(plot_path)
    arcpy.mapping.AddLayer(df, plot_layer)
    extent = plot_layer.getSelectedExtent()
    df.extent = extent
    mxd.save()
'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def reponse1(Date_demande,Numero_demande,Nom_demandeur,cas,mxd):
    text1 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT1")[0]
    text2 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT2")[0]
    text3= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT3")[0]
    text4 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT4")[0]
    text5= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT5")[0]


    Superficie_parcelle  = str(cas[1][2])
    Commune  = "Casablanca " #on doit faire l'intersection avec la couche de commune et recuperer sa superficie
    ajout1=  str(cas[1][1][0]) #Zone
    ajout2 = str(cas[1][0][0]) #Secteur


    t6 = "\n- Zone: {} \n - Secteur : {}".format(ajout1,ajout2)
    t7 = "\nDe meme, vous trouverez en bas un extrait montrant la position du terrain par rapport a la\n"+"limite couverte par les documents d'urbanisme."
    t8 = "\nVeuillez agreer, M/Mme, l'expression de mes salutations distinguees."
    text1.text= Date_demande
    text2.text = "    "*10+" A \n" + "    "*10+"  M/Mme "+ Nom_demandeur
    text3.text = "Objet: "
    text4.text = "Note de renseignements urbanistiques indicative relative a votre demande N° {}".format( Numero_demande)
    text5.text = "En reponse a votre demande citee en objet, j'ai l'honneur de vous faire connaitre que d'apres\n" +  "les dispositions des documents d'urbanisme, "+"le terrain en question d'une superficie \n"+Superficie_parcelle +" m2 et appartenat a la commune / arrondissement "+Commune+"est affecte comme suit:\n"+t6+t7+t8
    arcpy.RefreshActiveView()
    mxd.save()

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def reponse2(Date_demande,Numero_demande,Nom_demandeur,cas,mxd):
    text1 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT1")[0]
    text2 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT2")[0]
    text3= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT3")[0]
    text4 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT4")[0]
    text5= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT5")[0]


    Superficie_parcelle  = str(cas[2])
    Commune  = "Casablanca \n" #on doit faire l'intersection avec couche de commune et recuperer sa superficie
    zonage=""
    for i in range(len(cas[1][1])):
        ajout1=  str (cas[1][1][i][0])# Zones
        ajout2=str (cas[1][1][i][1]) # Superficies zones
        ajout3 = str(cas[1][0][i][0]) # secteurs
        ajout4=str(cas[1][0][i][1]) # superficie secteurs
        zonage="-Zones: {}, Superficie: {} m2 \n-Secteurs : {} , Superficie: {} m2\n \n \n".format(ajout1,ajout2,ajout3,ajout4)+zonage

    t7 = "De meme, vous trouverez en bas un extrait montrant la position du terrain par rapport a la\n"+"limite couverte par les documents d'urbanisme."
    t8 = "\n \n \n Veuillez agreer, M/Mme, l'expression de mes salutations distinguees."
    text1.text= Date_demande
    text2.text = "    "*10+" A \n" + "    "*10+"  M/Mme "+ Nom_demandeur
    text3.text = "Objet: "
    text4.text = "Note de renseignements urbanistiques indicative relative a votre demande N° {}".format( Numero_demande)
    text5.text = "En reponse a votre demande citee en objet, j'ai l'honneur de vous faire connaitre que d'apres\n" + "les dispositions des documents d'urbanisme, "+"le terrain en question d'une superficie"+Superficie_parcelle +" m2 \net appartenat a la commune / arrondissement "+Commune+"est affecte comme suit:\n"+zonage+t7+t8
    mxd.save()

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''

def reponse3(Date_demande,Numero_demande,Nom_demandeur,cas,mxd):
    text1 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT1")[0]
    text2 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT2")[0]
    text3 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT3")[0]
    text4 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT4")[0]
    text5= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT5")[0]

    Superficie_parcelle  = str(cas[1])
    Commune  = "Casablanca" #on doit faire l'intersection avec couche de commune et recuperer sa superficie


    t7 = " \n \nDe meme, vous trouverez en bas un extrait montrant la position du terrain par rapport a la\n"+"limite couverte par les documents d'urbanisme."
    t8 = " \n \nVeuillez agreer, M/Mme, l'expression de mes salutations distinguees."
    text1.text= Date_demande
    text2.text = "    "*10+" A \n" + "    "*10+"  M/Mme "+ Nom_demandeur
    text3.text = "Objet: "
    text4.text = "Note de renseignements urbanistiques indicative relative a votre demande N° {}".format( Numero_demande)
    text5.text = "En reponse a votre demande citee en objet, j'ai l'honneur de vous faire connaitre que d'apres\n" + "les dispositions des documents d'urbanisme, "+"le terrain en question d'une superficie:\n"+Superficie_parcelle +"  m² est situe dans une zone non couverte par un document d'urbanisme\n"+t7+t8
    mxd.save()

'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def reponse41(Date_demande,Numero_demande,Nom_demandeur,cas,mxd):
    text1 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT1")[0]
    text2 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT2")[0]
    text3= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT3")[0]
    text4 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT4")[0]
    text5= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT5")[0]



    Superficie_parcelle  = str(cas[2][1][1])
    Commune  = "Casablanca" #on doit faire l'intersection avec couche de commune et recuperer sa superficie
    ajout1=  str (cas[2][1][1][0])#zone
    ajout2= str(cas[1][0]) # superficie interieure
    ajout3 = str(cas[2][1][0][0]) #secteur
    ajout4=str(cas[1][1]) # superficie exterieure

    t6 = "-Une Superficie {} situee a l'interieur du zonage selon les specifications suivantes\n"+"-Zone: {}\n-Secteur: {}m2 \n".format(ajout2,ajout1,ajout3)+"-Une superficie {}m2 situee a l'exterieur du zonage et non couverte par un document\n d'urbanisme".format(ajout4)+"\n \n De meme, vous trouverez en bas un extrait montrant la position du terrain par rapport a la\n"+" limite couverte par les documents d'urbanisme."+"\n \n Veuillez agreer, M/Mme, l'expression de mes salutations distinguees."
    text1.text= Date_demande
    text2.text = "    "*10+" A \n" + "    "*10+"  M/Mme "+ Nom_demandeur
    text3.text = "Objet: "
    text4.text = "Note de renseignements urbanistiques indicative relative a votre demande N° {}".format( Numero_demande)
    text5.text = "En reponse a votre demande citee en objet, j'ai l'honneur de vous faire connaitre que d'apres\n" +"les dispositions des documents d'urbanisme, "+"le terrain en question \n d'une superficie "+Superficie_parcelle +" m2 est situe comme suit:\n"+t6
    #text8.text =     arcpy.RefreshActiveView()
    mxd.save()
'''*****************************************************************************************************************************************************************************************
*****************************************************************************************************************************************************************************************'''
def reponse42(Date_demande,Numero_demande,Nom_demandeur,cas,mxd):
    text1 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT1")[0]
    text2 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT2")[0]
    text3= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT3")[0]
    text4 = ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT4")[0]
    text5= ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT5")[0]
    #text6 =ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT6")[0]
    #text7 =ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT7")[0]
    #text8 =ListLayoutElements(mxd, "TEXT_ELEMENT", "TEXT8")[0]


    Superficie_parcelle  = str(cas[2][2])
    Commune  = "Casablanca" #on doit faire l'intersection avec couche de commune et recuperer sa superficie
    zonage=""
    for i in range (len(cas[2][1][1])):
        ajout1=  str (cas[2][1][1][i][0])#zone
        ajout11=str(cas[2][1][1][i][1]) # superficie zone
        ajout2= str(cas[1][0]) # superficie interieure
        ajout3 = str(cas[2][1][0][i][0]) #secteur
        ajout33=str(cas[2][1][0][i][1]) # superficie secteur
        ajout4=str(cas[1][1]) #superficie d'exterieure
        zonage="-Zone: {} , Superficie: {} m2\n-Secteur: {} , Superficie: {} m2 \n \n".format(ajout1, ajout11,ajout3,ajout33)+zonage

    text1.text= Date_demande
    text2.text = "    "*10+" A \n" + "    "*10+"  M/Mme "+ Nom_demandeur
    text3.text = "Objet: "
    text4.text = "Note de renseignements urbanistiques indicative relative a votre demande N: {}".format( Numero_demande)
    text5.text="En reponse a votre demande citee en objet, j'ai l'honneur de vous faire connaitre que d'apres\n" + "les dispositions des documents d'urbanisme, "+"le terrain en question\n  d'une superficie"+Superficie_parcelle +" m2 est situe comme suit:\n"+"Une Superficie {} m2 situee a l'interieur du zonage selon les specifications suivantes\n".format(ajout2)+zonage+"-Une superficie {} m2 situee a l'exterieur du zonage et non couverte par un document\nd'urbanisme".format(ajout4)+"\n \nDe meme, vous trouverez en bas un extrait montrant la position du terrain par rapport a la\n"+"limite couverte par les documents d'urbanisme."+"\n \nVeuillez agreer, M/Mme, l'expression de mes salutations distinguees."
    arcpy.RefreshActiveView()
    mxd.save()

#############################################################################################################
NRU(Date_demande,Numero_demande,Nom_demandeur,fichiertexte,outfolder,mxd)