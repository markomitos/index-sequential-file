#!/usr/bin/python

import os
import struct
import copy

from app.constants import *
from app.record import Record
from app.sequential_file import SequentialFile
from app.serial_file import SerialFile
from app.binary_file import BinaryFile
from app.index_sequential_file import *

LRECORD = Record(LEAF, LFMT, CODING)
HRECORD = Record(HEADER, HFMT, CODING)
ORECORD = Record(OVERFLOW,OFMT, CODING)
RECORD = Record(ATTRIBUTES, FMT, CODING)


#parsira txt file u listu slogova
def read_txt(fn):
    rows = []
    with open(fn, "r") as f:
        for line in f.readlines():
            cols = line.split()
            rows.append({
                "id": int(cols[0]),
                "sending_address": cols[1].replace("_"," "),
                "date": cols[2],
                "time":cols[3],
                "receiving_adress":cols[4].replace("_"," "),
                "price":cols[5],
                "status": 1
            })
    return rows

#ispis opcija menija
def printMenu():
    print(100* "=")
    print("1. Formiranje nove datoteke")
    print("2. Izbor aktivne datoteke")
    print("3. Prikaz naziva trenutne datoteke")
    print("4. Formiranje serijske datoteke")
    print("5. Formiranje sekvencijalne datoteke")
    print("6. Formiranje indeks sekvencijalne datoteke")
    print("7. Prikaz svih slogova datoteke")
    print("8. Izlaz")
    print(100*"=")

#1. trazena funkcionalnost - pravljenje novog filea. Ukoliko file vec postoji korisnik bira da li zeli da ga pregazi
def nameFile():
    name = input("Unesite ime datoteke: ").strip()
    file="data/"+ name+".dat"
    if find(name+".dat","C:/Users/marko/Desktop/fakultet/3. semestar/op/projekat1/data"):
        print("Datoteka pod ovim imenom vec postoji!")
        unos=input("Da li zelite da nastavite sa pravljenjem ove datoteke?(da/ne): ").strip().lower()
        if unos=="da":
            with open(file,"w") as f:
                print("Datoteka je uspesno napravljena!")
    else:
        with open(file,"w") as f:
                print("Datoteka je uspesno napravljena!")

#proverava da li file postoji
def find(name, path):
    for root,dirs,files in os.walk(path):
        if name in files:
            return os.path.join(root,name)
    return False

#2. bira trenutnu aktivnu datoteku
def chooseCurrentFile():
    while True:
        unos=input("Unesite ime datoteke: ").strip()
        file=find(unos,"C:/Users/marko/Desktop/fakultet/3. semestar/op/projekat2/index-sequential-file/data")
        if file!=False:
            return file
        else:
            print("Unesite validno ime datoteke!")

#3. prikazuje trenutnu datoteku
def showCurrentFile(active_file):
    name=active_file.split("/")
    print("Naziv trenutne datoteke je "+name[-1])

#pomocna funkcija koja cita sve blokove binarnog filea
def readBlocks(active_file):
    binary_file = BinaryFile("data/tmp.dat",RECORD,F)
    blocks=[]
    with open(active_file,"rb") as file:
        while True:       
            block=binary_file.read_block(file)
            if not block:
                break
            blocks.append(block)
    return blocks

#ispis binarne datoteke
def showWords(active_file):
    binary_file = BinaryFile("data/tmp.dat",RECORD,F)
    blocks=readBlocks(active_file)
    for i in range(0,len(blocks)):
            print("Block {}, adresa bloka: ".format(i+1)+str(id(blocks[i])))
            binary_file.print_block(blocks[i])

#funkcionalnost 4 - unos serijske datoteke u realnom vremenu
def inputSerialFile():
    serial_file = SerialFile(SERIAL_FILENAME,RECORD,F)
    serial_file.init_file()
    while True:
        while True:
            id = input("Unesite evidencioni broj(do 8 cifara): ")
            if len(id)<9 and id!="":
                break
            print("Unesite do 8 cifara!")
        while True:
            sending_address=input("Unesite adresu posiljaoca (do 50 karaktera): ")
            if len(sending_address)<51 and id!="":
                break
            print("Unesite do 50 karaktera!")
        while True:
            date = input("Unesite datum isporuke(u formatu dd.mm.yyyy.): ")
            if len(date)<12 and date!="":
                break
            print("Unesite validan datum!")
        while True:
            time = input("Unesite vreme isporuke (u formatu hh:ss): ")
            if len(time)<6 and time!="":
                break
            print("Unesite validno vreme!")
        while True:
            receiving_address=input("Unesite adresu primaoca (do 50 karaktera): ")
            if len(receiving_address)<51 and receiving_address!="":
                break
            print("Unesite do 50 karaktera!")
        while True:
            price = input("Unesite cenu isporuke (do 1000000000): ")
            if len(price)<10 and price!="":
                break
            print("Unesite do 9 karaktera!")
        new_entry={"id":int(id),"sending_address":sending_address,"date":date,"time":time,"receiving_address":receiving_address,"price":price,"status":1}
        serial_file.insert_record(new_entry)
        unos=input("Da li zelite da dodate jos podataka?(da/ne)")
        if not(unos[0].lower()=="d"):
            break

#ispis menia
def serialMenu():
    print(100*"=")
    print("1. Dodavanje novog sloga")
    print("2. Izmena postojeceg sloga")
    print("3. Brisanje postojeceg sloga")
    print("4. Nazad")
    print(100*"=")

#dodavanje nove reci u serijsku datoteku
def addWord(update_file):
    id=input("Unesite evidencioni broj nastave: ").strip()
    word={}
    name=input("Unesite naslov: ").strip()
    date=input("Unesite datum u fomatu dd.mm.yyyy: ").strip()
    time=input("Unesite vreme u formatu hh:mm: ").strip()
    classroom=input("Unesite oznaku prostorije: ").strip()
    attendence=input("Unesite broj prisutnih ucenika: ").strip()
    word["id"]=int(id)
    word["name"]=name
    word["date"]=date
    word["time"]=time
    word["classroom"]=classroom
    word["attendence"]=attendence
    word["status"]=3
    update_file.insert_record(word)

#izmena reci u datoteci
def changeWord(update_file,active_file):
    blocks=readBlocks(active_file)
    id=input("Unesite evidencioni broj nastave koju zelite da promenite: ").strip()
    word={}
    found=False
    for block in blocks:
        for w in block:
            if str(w['id'])==id:
                found=True
                print(w)
                word=w
    if not found:
        word={"id":int(id),"name":"x","date":"x","time":"x","classroom":"x","attendence":"x","status":4}
    name=input("Unesite novo naslov(ili x da bi ostao kao stari): ").strip()
    date=input("Unesite novi datum u fomatu dd.mm.yyyy(ili x da bi ostao kao stari): ").strip()
    time=input("Unesite novo vreme u formatu hh:mm(ili x da bi ostalo kao staro): ").strip()
    classroom=input("Unesite novu oznaku prostorije(ili x da bi ostala ista): ").strip()
    attendence=input("Unesite novi broj prisutnih ucenika(ili x da bi ostao isti): ").strip()
    if name!="x":
        word["name"]=name
    if date!="x":
        word["date"]=date
    if time!="x":
        word["time"]=time
    if classroom!="x":
        word["classroom"]=classroom
    if attendence!="x":
        word["attendence"]=attendence
    word["status"]=4
    update_file.insert_record(word)

#brisanje reci iz datoteke
def deleteWord(update_file):
    id=input("Unesite evidencioni broj nastave koju zelite da obrisete: ").strip()
    word={"id":int(id),"name":"x","date":"x","time":"x","classroom":"x","attendence":"x","status":5}
    update_file.insert_record(word)

    
#4. pravljenje serijske datoteke promena
def updateSerialFile(active_file):
    update_file=SerialFile(SERIAL_FILENAME,RECORD,F)
    update_file.init_file()
    showCurrentFile(active_file)
    showWords(active_file)
    unos=""
    while True:
        serialMenu()
        unos=input("Unesite broj ispred opcije u meniju koju zelite da izvrsite: ").strip()
        if unos=="1":
            addWord(update_file)
        elif unos=="2":
            changeWord(update_file,active_file)
        elif unos=="3":
            deleteWord(update_file)
        elif unos=="4":
            return
        else:
            print("Unesite validan unos!")

#pomocna funkcija koja od liste blokova pravi listu reci
def wordifyBlocks(blocks):
    words=[]
    for block in blocks:
        for w in block:
            if w["id"]!=-1:
                words.append(w)
    return words

#5. funkcija iz serijske datoteke formira sekvencijalnu datoteku
def createSequentialFile(serial_file_location):
    update_file= SequentialFile(SEQUENTIAL_FILENAME,RECORD,HRECORD,OVERFLOW,LRECORD,F)
    update_file.init_file()
    blocks=readBlocks(serial_file_location)
    words=wordifyBlocks(blocks)
    sorted_words=sorted(words,key=lambda d:d["id"])
    print("Sortirani slogovi: ")
    for word in sorted_words:
        print(word)
        update_file.insert_record(word)


def serializeTest():
    words=read_txt("data/test.txt")
    serial_file=SerialFile("data/test.dat",RECORD,F)
    serial_file.init_file()
    for word in words:
        serial_file.insert_record(word)
    showWords("data/test.dat")

def createIndexSequential():
    index_sequential_file=IndexSequentialFile(INDEX_SEQUENTIAL_FILENAME,RECORD,HRECORD,LRECORD,ORECORD,F)
    index_sequential_file.init_file()
    print(index_sequential_file.find_by_id(25252525))
    print(index_sequential_file.find_by_id(55555555))
    return INDEX_SEQUENTIAL_FILENAME


#meni aplikacije
def menu():
    unos=""
    active_file="data/test.dat"
    serial_file_location="data/serial.dat"
    sequental_file_location="data/sequental.dat"
    while True:
        printMenu()
        unos=input("Unesite broj ispred opcije menija koji zelite da iskoristite: ").strip()
        print(100*"=")
        if unos=="1":
            nameFile()
        elif unos=="2":
            active_file=chooseCurrentFile()
        elif unos=="3":
            showCurrentFile(active_file)
        elif unos=="4":
            inputSerialFile()
        elif unos=="5":
            createSequentialFile(active_file)
        elif unos=="6":
            active_file=createIndexSequential()
        elif unos=="7":
            showWords(active_file)
        elif unos=="8":
            exit()
        else:
            print("Molimo vas unesite validnu opciju!")



if __name__ == "__main__":
    menu()
