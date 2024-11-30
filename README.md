# NRU - Note Renseignement Urbain

## Description du Projet
Le projet **NRU (Note Renseignement Urbain)** est une application sous forme de toolbox pour **ArcGIS**. Cette application vise à simplifier la consultation des informations relatives à une parcelle urbaine. Elle prend en compte les données du demandeur, ainsi que les coordonnées de la parcelle à examiner. L'application génère ensuite un fichier **PDF** contenant des informations détaillées sur la parcelle, y compris sa localisation par rapport aux communes, zones et équipements spécifiés.

## Fonctionnalités Principales

### 1. Consultation de Parcelle
L'utilisateur fournit des informations sur le demandeur et les coordonnées de la parcelle à examiner.

### 2. Analyse Géographique
Les données géographiques telles que les communes, zones et équipements sont utilisées pour situer la parcelle dans son environnement urbain.

### 3. Export PDF
Les résultats de la consultation sont compilés dans un fichier PDF, offrant une vue complète des informations sur la parcelle.

### 4. Stockage des Couches
Les couches géographiques générées sont stockées dans une **"Personal Geodatabase"** pour une gestion efficace des données.

### 5. JsonToFeatureclass
Si les couches sont disponibles au format **JSON**, une application supplémentaire appelée **"JsonToFeatureclass"** est incorporée dans le même toolbox pour simplifier le processus de conversion et d'intégration des données. Un autre script, nommé **`JsonToFeatureclass.ipynb`**, est présent dans le dossier **`data_NRU\json`**. Ce script contient une fonction spécifique dédiée à la conversion des données JSON en couches, facilitant ainsi l'intégration fluide des données dans l'application.

## Utilisation de l'Application

1. Assurez-vous d'avoir **ArcGIS** installé sur votre système.
2. Importez le toolbox NRU dans **ArcGIS**.
3. Remplissez les informations demandées concernant le demandeur et les coordonnées de la parcelle.
4. L'application utilise les données géographiques à propos des couches **'zones'**, **'communes'** et **'équipements'**.
5. Un fichier **PDF** est créé, contenant toutes les informations recueillies.
6. Si les couches sont disponibles sous forme de **JSON**, utilisez l'application **"JsonToFeatureclass"** pour faciliter l'intégration dans la **"Personal Geodatabase"**.

## Remarques

- Les couches géographiques générées par l'application sont enregistrées dans une **"Personal Geodatabase"** nommée **`projet.mdb`** située dans le dossier **`data_NRU`**.
- Pour utiliser des couches **'zones'** et **'communes'** différentes, veuillez les intégrer dans la **"Personal Geodatabase"** en remplaçant les couches existantes.
- Pour assurer une intégration correcte des données, veuillez respecter le format d'insertion des données défini. Vous pouvez consulter les fichiers texte présents dans le dossier **`test_result`**, spécifiquement ceux nommés **'parcelle'**, pour obtenir un exemple du format attendu.
- Avant d'exécuter les scripts Python ou les fichiers IPython (**ipynb**), assurez-vous de disposer de la bibliothèque **arcpy**.

## Documentation et Tutoriels

- Pour faciliter la compréhension des fonctionnalités de l'application **NRU**, un dossier nommé **`test_result`** est disponible. Ce dossier contient des exemples de tests qui ont été effectués, ainsi que les résultats obtenus.
- Un tutoriel vidéo est disponible dans le dossier **`video`** pour vous familiariser davantage avec l'application.

## Données

Les données utilisées par l'application sont stockées sous forme de **classes d'entités ('feature classes')** dans la **"Personal Geodatabase"** nommée **`projet.mdb`**. Les mêmes données sont également disponibles au format **JSON** dans le dossier **`data_NRU\json`**. Ces fichiers JSON peuvent être utilisés pour l'intégration des données si nécessaire.

## Auteurs

Ce projet a été développé par **AJALE Saad** dans le cadre d'un projet d'étude.

## Contact

Pour des questions ou des problèmes, veuillez contacter :  
**Email** : [ajalesaad@gmail.com](mailto:ajalesaad@gmail.com)  
**LinkedIn** : [www.linkedin.com/in/ajale-saad-b8136124b](https://www.linkedin.com/in/ajale-saad-b8136124b)

---

**Note** : NRU est un outil de consultation et n'assume aucune responsabilité quant à l'exactitude des informations fournies. Utilisez les résultats générés à des fins informatives uniquement.
