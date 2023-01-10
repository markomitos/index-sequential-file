#!/usr/bin/python

import os
import struct

from app.binary_file import BinaryFile
from app.constants import *
from math import log,ceil
from main import readBlocks,wordifyBlocks
from app.tree import *

import pathlib


class IndexSequentialFile(BinaryFile):
    def __init__(self, filename, record, header,leaf,overflow, blocking_factor, empty_key=-1):
        self.filename = filename
        self.record = record
        self.record_size = struct.calcsize(self.record.format)
        self.blocking_factor = blocking_factor
        self.block_size = self.blocking_factor * self.record_size
        self.empty_key = empty_key
        self.header = header
        self.header_size = struct.calcsize(self.header.format)
        self.b=ceil(len(wordifyBlocks(readBlocks(SEQUENTIAL_FILENAME)))/5*1.25)
        self.index_address=self.b*self.block_size+self.header_size
        self.leaf=leaf
        self.leaf_size=struct.calcsize(self.leaf.format)
        self.overflow_address=self.index_address+self.b*self.leaf_size
        self.tree_height = ceil(log(self.b,N))
        self.root=None
        self.first_free_overflow=0
        self.overflow = overflow
        self.overflow_size = struct.calcsize(self.overflow.format)


    def read_overflow(self, f):
        binary_data = f.read(self.overflow_size)

        if len(binary_data) == 0:
            return None

        return self.record.encoded_tuple_to_dict(binary_data) 
        
    def write_overflow(self,file,word):
        binary_data = bytearray()   # Niz bita koji bi trebalo da se upise u datoteku
        rec_binary_data = self.overflow.dict_to_encoded_values(word)
        binary_data.extend(rec_binary_data)
        file.write(binary_data)


    def write_header(self,file):
        binary_data = bytearray()   # Niz bita koji bi trebalo da se upise u datoteku
        header={"index_address":self.index_address,"overflow_address":self.overflow_address}
        rec_binary_data = self.header.dict_to_encoded_values(header)
        binary_data.extend(rec_binary_data)
        file.write(binary_data)



    def write_leaf(self,file,leaf):
        l={"block_value":leaf.block_value,"block_address":leaf.block_address,"overflow_value":leaf.overflow_value,"overflow_address":leaf.overflow_address}
        binary_data = bytearray()
        leaf_binary_data= self.leaf.dict_to_encoded_values(l)
        binary_data.extend(leaf_binary_data)
        file.write(binary_data)

    def createTree(self,nodes):
        if len(nodes)<2:
            return nodes[0]
        new_nodes=[]
        len_n=len(nodes)
        for n in range(0,len_n,2):
            if (n+1)<len_n:
                new_nodes.append(Node(nodes[n].value_left,nodes[n],nodes[n+1].value_left,nodes[n+1]))
            else:
                new_nodes.append(Node(nodes[n].value_left,nodes[n]))
        return self.createTree(new_nodes)
        
    def readHeader(self,f):
        binary_data = f.read(self.header_size)

        if len(binary_data) == 0:
            return None

        return self.header.encoded_tuple_to_dict(binary_data)


    def init_tree(self):
        leaves=[]
        with open(self.filename, "rb+") as f:
            header=self.readHeader(f)
            self.index_address=header["index_address"]
            self.overflow_address=header["overflow_address"]
            first=True
            for i in range(self.b):
                words=[]
                block=self.read_block(f)
                for word in block:
                    if word["id"]!=-1:
                        words.append(word)
                min=99999999
                if first:
                    min=0
                else:
                    min=words[0]["id"]
                leaves.append(Leaf(min,i,min,i))
                first=False
            for leaf in leaves:
                self.write_leaf(f,leaf)
            #formira stabo
            nodes=[]
            len_l=len(leaves)
            for l in range(0,len_l,2):
                if((l+1)<len_l):
                    nodes.append(Node(leaves[l].overflow_value,leaves[l],leaves[l+1].overflow_value,leaves[l+1]))
                else:#neparan broj listova
                    nodes.append(Node(leaves[l].overflow_value,leaves[l]))
            
            self.root=self.createTree(nodes)
            

    def print_primary(self):
        with open(self.filename, "rb") as f:
            f.seek(self.header_size)
            for i in range(self.b):
                print("Blok ",i)
                self.print_block(self.read_block(f))

    def init_file(self):
        bl=readBlocks(SEQUENTIAL_FILENAME)
        words=wordifyBlocks(bl)
        i=0
        with open(self.filename, "rb+") as f:
            self.write_header(f)
            while i < len(words):
                block = []
                for _ in range(self.blocking_factor-1):
                    if i < len(words):
                        block.append(words[i])
                        i+=1
                    else:
                        block.append(self.get_empty_rec())
                    
                block.append(self.get_empty_rec())
                self.write_block(f, block)
        self.init_tree()
        self.print_primary()
        self.print_tree()

    def print_tree(self):
        nodes=[self.root]
        print("Stablo: ")
        i=0
        while str(type(nodes[0]))=="<class 'app.tree.Node'>": 
            print(i, ". nivo stabla: ")
            new_nodes=[]
            output=""
            for node in nodes:
                new_nodes.append(node.left)
                new_nodes.append(node.right)
                output+=str(node) + " --- "
            print(output[:len(output)-5])
            nodes=new_nodes
            i+=1
        output=""
        print(i, ". nivo stabla: ")
        for node in nodes:
            output+=str(node) + " --- "
        print(output[:len(output)-5])

    def find_in_primary(self,block_address,id):
        with open(self.filename, "rb") as f:
            f.seek(self.header_size+self.block_size*block_address)
            block = self.read_block(f)
            for i in range(self.blocking_factor):
                if block[i]["id"]==-1:
                    return None, block_address, i
                if block[i]["id"]==id:
                    return block[i],block_address,i
                if block[i]["id"]>id:
                    return None, block_address, i

    def find_in_overflow(self,overflow_address,id):
        with open(self.filename, "rb") as f:
            f.seek(self.overflow_address+self.overflow_size*overflow_address) 
            current_word = self.read_overflow(f)
            next_address=overflow_address
            while next_address!=-1:
                if current_word["id"]==id:
                    return current_word,-1,next_address
                if current_word["id"]>id or current_word["next"]==-1:
                    return None, -1, next_address
                next_address=current_word["next"]
                f.seek(self.overflow_address+self.overflow_size*next_address)
                current_word = self.read_overflow(f) 
            


    def find_by_id(self,id):
        current_node=self.root
        while str(type(current_node))=="<class 'app.tree.Node'>": 
            if current_node.value_right==-1 or id<current_node.value_right:
                current_node=current_node.left
            else:
                current_node=current_node.right
        if current_node.block_value == current_node.overflow_value or id<current_node.overflow_value:
            return self.find_in_primary(current_node.block_address,id),current_node.overflow_address
        return self.find_in_overflow(current_node.overflow_address,id),current_node.overflow_address

    def write_in_overflow(self,word,index):
        with open(self.filename, "rb") as f:
            f.seek(self.overflow_address+self.overflow_size*index)
            previous=self.read_overflow(f)
            previous["next"]=self.first_free_overflow
            f.seek(-self.overflow_size,1)
            self.write_overflow(f)
            f.seek(self.overflow_address+self.overflow_size*self.first_free_overflow)
            new_word={
                "id":word[id], 
                "sending_address": word["sending_address"],
                "date": word["date"],
                "time": word["time"],
                "receiving_address": word["receiving_address"],
                "price": word["price"],
                "next": self.first_free_overflow,
                "status": word["status"]
            }
            self.first_free_overflow+=1
            self.write_overflow(f,new_word)

    def insert_record(self,word):
        found,block_address,index,overflow_address=self.find_by_id(word["id"])
        if found!=None:
            print("Already exists!")
            return

        #treba ga smestiti u overflow
        if block_address==-1:
            self.write_in_overflow(word,index)
        else:
            with open(self.filename, "rb") as f:
                f.seek(self.header_size+self.block_size*block_address)
                block=self.read_block(f)
                #ukoliko postoji prazno mesto upise ga
                if block[index]["id"]==-1 or block[index]["status"]==2:
                        block[index]=word
                        f.seek(-self.block_size, 1)
                        self.write_block(f, block)
                        return
                tmp_word = block[self.blocking_factor-1]
                for k in range(self.blocking_factor-1, index, -1):
                    block[k] = block[k-1]               # move records
                block[index] = word                         
                f.seek(-self.block_size, 1)
                self.write_block(f, block)
                f.seek(self.overflow_address+self.overflow_size*overflow_address,1) 
                current_word = self.read_overflow(f)
                next_address=overflow_address
                while next_address!=-1:
                    if current_word["id"]>id or current_word["next"]==-1:
                        break
                    next_address=current_word["next"]
                    f.seek(self.overflow_address+self.overflow_size*next_address)
                    current_word = self.read_overflow(f) 
                self.write_in_overflow(tmp_word,next_address)




        

    def __insert_overflow(self, f, rec):
        f.seek(self.b * self.block_size)

        while True:
            record = self.read_record(f)
            if not record:
                break
            if record.get("id") == rec.get("id"):
                if record.get("status") == 1:
                    print("Already exists with ID {}".format(rec.get("id")))
                else:
                    f.seek(-self.record_size, 1)
                    self.write_record(f, rec)
                return

        self.write_record(f, rec)





    # def find_by_id(self, id):
    #     block_idx = self.hash(id)

    #     with open(self.filename, "rb+") as f:
    #         f.seek(block_idx * self.block_size)
    #         block = self.read_block(f)

    #         for i in range(self.blocking_factor):
    #             if block[i].get("status") == 0:
    #                 return None
    #             if block[i].get("status") == 1 and block[i].get("id") == id:
    #                 return (block_idx, i)

    #         return self.__find_in_overflow(f, id)

    #     return None

    def insert_record(self, rec):
        id = rec.get("id")
        block_idx = find_by_id(id)

        with open(self.filename, "rb+") as f:
            f.seek(block_idx * self.block_size)
            block = self.read_block(f)

            i = 0
            while i < self.blocking_factor and block[i].get("status"):
                if block[i].get("id") == id:
                    if block[i].get("status") == 1:
                        print("Already exists with ID {}".format(id))
                    else:
                        block[i] = rec
                        f.seek(block_idx * self.block_size)
                        self.write_block(f, block)
                    return
                i += 1

            if i == self.blocking_factor:
                self.__insert_overflow(f, rec)
                return

            block[i] = rec
            f.seek(block_idx * self.block_size)
            self.write_block(f, block)

    def delete_by_id(self, id):
        found = self.find_by_id(id)

        if not found:
            return None

        block_idx = found[0]
        rec_idx = found[1]

        with open(self.filename, "rb+") as f:
            if block_idx < self.b:
                f.seek(block_idx * self.block_size)
                block = self.read_block(f)
                block[rec_idx]["status"] = 2
                f.seek(block_idx * self.block_size)
                self.write_block(f, block)
            else:
                f.seek(self.b * self.block_size + rec_idx * self.record_size)
                rec = self.read_record(f)
                rec["status"] = 2
                f.seek(-self.record_size, 1)
                self.write_record(f, rec)
            return found
