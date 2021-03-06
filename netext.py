"""Extra functions and other extensions for pynet datastructures
"""
import pynet,os#,netio
import random
import heapq
import string
import shutil
import copy
import numpy
#from PIL import Image


class Net_edges:
    def __init__(self,net):
        self.net=net
    def __iter__(self):
        if self.net.isSymmetric():
            for node1Index in self.net:
                node1=self.net[node1Index]
                for node2Index in node1:
                    if node1Index.__hash__()<node2Index.__hash__():
                        yield [node1Index,node2Index,self.net[node1Index,node2Index]]       
        else:
            for node1Index in self.net:
                node1=self.net[node1Index]
                for node2Index in node1.iterOut():
                    yield [node1Index,node2Index,self.net[node1Index,node2Index]]       

    def __len__(self):
        lenght=0
        if self.net.isSymmetric():
            for nodeIndex in self.net:
                lenght+=len(self.net[nodeIndex].edges)
            return lenght/2
        else:
            for nodeIndex in self.net:
                lenght+=self.net[nodeIndex].outDeg()
            return lenght
    def __str__(self):
        return str(list(self))
        #rs=""
        #for edge in self:
        #    rs+=str(edge)+" "
        #return rs
pynet.VirtualNet.edges=property(Net_edges)

class Net_weights:
    def __init__(self,net):
        self.net=net
    def __iter__(self):
        for edge in self.net.edges:
            yield edge[2]
    def __len__(self):
        return len(self.net.edges)
    def __str__(self):
        return reduce(lambda x,y: str(x)+" "+str(y),self)
pynet.VirtualNet.weights=property(Net_weights)

class Node_edges:
    def __init__(self,node):
        self.node=node
    def __iter__(self):
        for index in self.node:
            yield self.node.net[self.node.name,index]       
    def __len__(self):
        return self.node.deg()
        #return len(self.node.net._nodes[self.node.index])
    def __str__(self):
        rs=""
        for edge in self:
            rs+=str(edge)+"\t"
        return rs
pynet.Node.edges=property(Node_edges)


def getStrength(node):
    return sum(node.edges)
pynet.Node.strength=getStrength

def strengths(net,nodes=None):
    strengths={}
    if nodes==None:
        nodes=net
    for node in nodes:
        strengths[node]=net[node].strength()
    return strengths


def Net_add(self,net):
    for node in net:
        for neigh in net[node]:
            self[node,neigh]=net[node,neigh]
pynet.VirtualNet.add=Net_add


class NodeProperties(dict):
    def __init__(self):
        super(dict,self)
        self.__dict__={}
    def addProperty(self,propertyName):
        if not hasattr(self,propertyName):
            newValue={}
            self[propertyName]=newValue
            self.__setattr__(propertyName,newValue)
            
def addNodeProperty(net,propertyName):
    if not hasattr(net,"nodeProperty"):
        net.nodeProperty=NodeProperties()
    net.nodeProperty.addProperty(propertyName)
    #if not hasattr(net.nodeProperty,propertyName):
    #    newValue={}
    #    #net.nodeProperty.__setattr__(propertyName,newValue)
    #    net.nodeProperty[propertyName]=newValue

def copyNodeProperties(fromNet,toNet):
    if hasattr(fromNet,"nodeProperty"):
        for p in fromNet.nodeProperty:
            addNodeProperty(toNet,p)
            for node in toNet:
                value=fromNet.nodeProperty[p][node]
                toNet.nodeProperty[p][node]=value

def getNumericProperties(net):
    """ Returns a list of all node properties
    whose values are numeric (int or float)"""

    propertylist=list(net.nodeProperty)

    numericproperties=[]

    for prop in propertylist:

        numericproperty=True

        for node in net:

            if not(isinstance(net.nodeProperty[prop][node],int) or (isinstance(net.nodeProperty[prop][node],float))):

                numericproperty=False

        if numericproperty==True:

            numericproperties.append(prop)

    return numericproperties


def getPropertyTypes(net):
    """Returns a dictionary where keys are nodeProperties
    and values indicate their type ('int','float','number','string','string/color','mixed')
    """
    propertylist=list(net.nodeProperty)
    propertydict={}

    for prop in propertylist:
        intprop=True
        floatprop=True
        numprop=True
        strprop=True

        for node in net:
            if not(isinstance(net.nodeProperty[prop][node],int)):
                   intprop=False
            if not(isinstance(net.nodeProperty[prop][node],float)):
                   floatprop=False
            if not(isinstance(net.nodeProperty[prop][node],float)) and not(isinstance(net.nodeProperty[prop][node],int)):
                   numprop=False
            if not(isinstance(net.nodeProperty[prop][node],str)):
                   strprop=False

        if intprop==True:
            propertydict[prop]='int'
        elif floatprop==True:
            propertydict[prop]='float'
        elif numprop==True:
            propertydict[prop]='number'
        elif strprop==True:
            propertydict[prop]='string'
        else:
            propertydict[prop]='mixed'

    return propertydict


class Enumerator:
    """
    Finds enumeration for hashable items. For new items a new number is
    made up and if the item already has a number it is returned instead
    of a new one.
    >>> e=Enumerator()
    >>> e['foo']
    0
    >>> e['bar']
    1
    >>> e['foo']
    0
    >>> list(e)
    ['foo', 'bar']
    """
    def __init__(self):
        self.number={}
        self.item=[]

    def _addItem(self,item):
        newNumber=len(self.number)
        self.number[item]=newNumber
        self.item.append(item)
        return newNumber

    def __getitem__(self,item):
        try:
            return self.number[item]
        except KeyError:
            return self._addItem(item)
 
    def getReverse(self,number):
        return self.item[number]

    def __iter__(self):
        return self.number.__iter__()

    def __len__(self):
        return len(self.number)




def deg(net):
    degrees={}
    for node in net:
        degrees[node]=net[node].deg()
    return degrees


def fullNet(nodes,weight=1):    
    net=pynet.SymmNet()
    for node1 in nodes:
        for node2 in nodes:
            net[node1,node2]=weight
    return net

            
#def collapseBiNet(net,nodes):
#    newNet=pynet.SymmNet()
#    for node in nodes:
#        newNet.add(fullNet(list(net[node])))




def getMeanDistance(theSet,distanceFunction):
    l=list(theSet)
    n=0
    s=0.0
    for i in l:
        for j in l:
            if i.__hash__()>j.__hash__():
                s+=distanceFunction(i,j)
                n+=1
    return s/float(n)


def getPathLengths(net,start,undirected=True):
    '''Dijkstra's algorithm for shortest paths
    Returns all possible path from the starting Node
    Parameters :
    net   : Network
    start : Starting Node
    undirected : bool
    If True, network in undirected else directed
    '''
    if undirected:
        # The implementation for undirected networks.
        # Assumes the network is unweighted 
        edge=set([start])
        interior=set()
        pathlengths={}
        i=0
        while len(edge)>0:
            i+=1
            interior=edge.union(interior)
            newEdge=set()
            for node in edge:
                for neighbor in net[node]:
                    if neighbor not in interior:
                        newEdge.add(neighbor)
                        pathlengths[neighbor]=i
            edge=newEdge
        return pathlengths

    else :
        # The implementation for directed networks.
        # Assumes the network in unweighted 
        edge=set([start])
        interior=set()
        pathlengths={}
        i=0
        while len(edge)>0:
            i+=1
            interior=edge.union(interior)
            newEdge=set()
            for node in edge:
                for neighbor in net[node].iterOut():
                    if neighbor not in interior:
                        newEdge.add(neighbor)
                        pathlengths[neighbor]=i
            edge=newEdge
        return pathlengths

def getMeanPathLength(net,maxSamples=1000):
    """
    Returns the mean path length of a network. If maxSample is not negative
    only at maxSample number of nodes is used as a starting point for finding
    paths instead of exhaustively going through all the paths.
    """
    #First check if we can use the c++-implementation
    #if net.__class__ == pynet.LCELibSparseSymmNet:
    #    return pynet._cnet.meanPathLength(net._net,maxSamples)
    #else:
    #
    ##this cannot be done as the no unweighted pathlengths implemented in c++

    nodes=list(net)
    if len(net)>maxSamples and maxSamples>0:
        random.shuffle(nodes)
        nodes=nodes[:maxSamples]
    m=0
    for node in nodes:
        m+=numpy.mean(getPathLengths(net,node).values())
    return float(m)/float(len(nodes))


def getBetweennessCentrality(net,edgeBC=False):
    """
    Returns a map from each node to its unweighted betweenness centrality.

    Note: this function needs some more testing.
    """
    #Implementation of the algorithm found in this paper:
    #www.inf.uni-konstanz.de/algo/publications/b-fabc-01.pdf
    cb={}
    for node in net:
        cb[node]=0
    if edgeBC:
        bcNet=pynet.SymmNet()
        
    for node in net:
        st=[]
        p={}
        sigma={}
        d={}
        delta={}
        for t in net:
            p[t]=[]
            sigma[t]=0
            d[t]=-1
            delta[t]=0
        sigma[node]=1
        d[node]=0
        q=[node]
        while len(q)>0:
            v=q.pop(0)
            st.append(v)
            for w in net[v]:
                if d[w]<0:
                    q.append(w)
                    d[w]=d[v]+1
                if d[w]==d[v]+1:
                    sigma[w]+=sigma[v]
                    p[w].append(v)
        while len(st)>0:
            w=st.pop()
            for v in p[w]:
                partialDelta=float(sigma[v])/float(sigma[w])*(1+delta[w])
                delta[v]+=partialDelta
                if edgeBC:
                    bcNet[v,w]=bcNet[v,w]+partialDelta
            if w!=node:
                cb[w]+=delta[w]

    for node in cb:
        cb[node]=cb[node]/2.0

    if edgeBC:
        for e in bcNet.edges:
            bcNet[e[0],e[1]]=e[2]/2.0
        return cb,bcNet
    else:
        return cb

