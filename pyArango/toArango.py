from django.shortcuts import redirect
from RestApi.models import Judge,Comissioner,Act,Court,Debter
from RestApi.views import JudgeSerializer
from pyArango.connection import *
from pyArango.collection import Collection, Field
from pyArango.graph import Graph, EdgeDefinition
from pyArango.collection import Edges
from random import randint
###################################################################
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

conn = Connection()

try:
     db = conn.createDatabase(name = "mydb")
except CreationError as err:
     db = conn["mydb"]


@api_view(['GET','POST','PUT'])
def nodeList(request):
    """Return dict cillection"""
    if request.method == 'GET':
        data = {}
        JudgeCollection = db["Judges"]
        EdgeCollection = db["Bred"]
        data["nodes"] = []
        data["links"] = []

        for i in JudgeCollection.fetchAll():
            item = {}
            item["_key"] = i._key
            item["name"] = i["name"]
            data["nodes"].append(item)

        aql = "FOR u IN Bred return u"
        res = db.AQLQuery(aql)
        return Response(data,status=status.HTTP_200_OK)

def graphRender(request):
    """Generating test graph"""
    #todo connect my database with graph visualization
    JudgeCollection = db["Judges"]
    EdgeCollection = db["Bred"]
    data = {}
    data["nodes"] = []
    data["links"] = []

    for i in JudgeCollection.fetchAll():
        item = {}
        item["_key"] = i._key
        item["name"] = i["name"]
        if "jdg" in item["_key"]:
            item["group"] = 2
        elif "mcrt" in item["_key"]:
            item["group"] = 4
        elif "crt" in item["_key"]:
            item["group"] = 8
        data["nodes"].append(item)
    #json.dump(data, open("text.json",'w'))
    dataids = {}
    dataids["judges"] = []
    dataids["court"] = []
    dataids["mcrt"] = []

    num = 0
    for i in data:
        for item in data[i]:
            if "jdg" in item["_key"]:
                dataids["judges"].append(num)
            elif "mcrt" in item["_key"]:
                dataids["mcrt"].append(num)
            elif "crt" in item["_key"]:
                dataids["court"].append(num)
            num+=1
    for i in dataids["court"]:
        item = {}
        item["source"] = i
        item["target"] = dataids["mcrt"][0]
        item["value"] = 40
        #"source":65,"target":58,"value":5
        data["links"].append(item)

    maxentity = len(dataids["judges"])
    for i in xrange(maxentity/3):
        item = {}
        item["source"] = dataids["judges"][randint(0,maxentity-1)]
        item["target"] = dataids["judges"][randint(0,maxentity-1)]
        item["value"] = 4
        #"source":65,"target":58,"value":5
        data["links"].append(item)

    for i in xrange(10):
        for j in xrange(maxentity/4+3):
            item = {}
            item["source"] = dataids["judges"][i*8 +j]
            item["target"] = dataids["court"][i]
            item["value"] = 1
            data["links"].append(item)
            if i == 0:
                if (i*8 +j) < 10:
                    item = {}
                    item["source"] = dataids["judges"][i*8 +j]
                    item["target"] = dataids["court"][9]
                    #"source":65,"target":58,"value":5
                    data["links"].append(item)
            if i == 9:
                if (i*8 +j) > 90:
                    item = {}
                    item["source"] = dataids["judges"][i*8 +j]
                    item["target"] = dataids["court"][0]
                    #"source":65,"target":58,"value":5
                    data["links"].append(item)

        with open(os.path.join(BASE_DIR, 'Bankrupt/static/metadata.json'), 'w') as outfile:
            json.dump(data, outfile, indent = 2)
    return render_to_response("graph.html")

def uploadJudges(request):
    try:
         JudgeCollection = db.createCollection(name = "Judges")
    except CreationError as err:
         JudgeCollection = db["Judges"]

    maxentity = len(Judge.objects.all())
    parts = 4
    for i in xrange(maxentity/(parts*2)-2):
        doc = JudgeCollection.createDocument()
        doc._key = "crt_%s" % (i+1)
        doc["name"] = "Court#%s" % (randint(200,4000))
        doc.save()

    #nice script
    Judges = Judge.objects.all()
    #todo transfer from judgeobj (the hash) to doc mode faster in less lines
    for sqlJudge in Judges:
        judgeobj = JudgeSerializer(sqlJudge).data
        doc = JudgeCollection.createDocument()
        doc._key = "jdg_%s" % int(judgeobj["id"])
        doc["name"] = judgeobj["name"]
        doc["middlename"] = judgeobj["middlename"]
        doc["surname"] = judgeobj["surname"]
        doc["archive"] = judgeobj["archive"]
        doc.save()

    try:
         EdgeCollection = db.createCollection(className = 'Edges' , name="Bred")
    except CreationError as err:
         EdgeCollection = db["Bred"]

    #creating courts
    #Judges at all
    maxentity = len(JudgeCollection.fetchAll())

    for i in xrange(9):
        for j in xrange(maxentity/4):
            gto = "crt_%s" % (i+1)
            gfrom = "jdg_%s" % (i*8 +j +8)
            if ((i*8 +j +1)>105): break
            doc = EdgeCollection.createDocument()
            doc.save(fromVertice = JudgeCollection[gfrom] , toVertice = JudgeCollection[gto])


    maxentity = len(JudgeCollection.fetchAll())
    for i in xrange(maxentity/3):
        gfrom = "jdg_%s" % randint(6,maxentity-4)
        gto = "jdg_%s" % randint(6,maxentity-4)
        doc = EdgeCollection.createDocument()
        doc.save(fromVertice = JudgeCollection[gfrom],
         toVertice = JudgeCollection[gto])
    # main cort
    doc = JudgeCollection.createDocument()
    doc._key = "mcrt_1"
    doc["name"] = "main_court"
    doc.save()

    for i in xrange(maxentity/(parts*2)-3):
        gfrom = "crt_%s" % (i+1)
        gto = "mcrt_1"
        doc = EdgeCollection.createDocument()
        doc.save(fromVertice = JudgeCollection[gfrom],
         toVertice = JudgeCollection[gto])

    return redirect("/index")
