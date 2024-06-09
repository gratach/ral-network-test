from ral_network import *

import json


SRF = RALFramework()
#SRF = SQLiteRALFramework("database.sqlite")
SRF.clearAllNodes()
#SRF3 = SQLiteRALFramework("database3.sqlite")



# Create a network of nodes

# A data node can be created in the following way:
tree = SRF.Node("tree")
# This uses the default format "text" for the data node.

# A data node can also be created with a specific format:
treeAgeInYears = SRF.Node("42", "int")

# Create more data nodes
hasAge = SRF.Node("has age")
isInstanceOfClass = SRF.Node("is instance of class")

# A constructed node can be created in the following way:
myTree = SRF.Node([(0, isInstanceOfClass, tree), (0, hasAge, treeAgeInYears)])
# This creates a constructed node with two connections:
#   [myTree, isInstanceOfClass, tree]
#   [myTree, hasAge, treeAgeInYears]
# The new created node is substituted for the 0.

# When a data node is created with the same data and format as another data node, they are equal.
tree2 = SRF.Node("tree")
assert tree == tree2

# When a constructed node is created with the same connections as another constructed node, they are equal.
myTree2 = SRF.Node([(0, isInstanceOfClass, tree2), (0, hasAge, treeAgeInYears)])
assert myTree == myTree2



# Save and load a network

# A network can be stored in a json object of the following form:
myJSONObject = [
    # The data concept block contains all data nodes.
    {
        # The format of the data node is the key.
        'text': {
            # Each node is stored with a unique id. The "has age" data node has the id "1".
            'has age': '1',
            'is instance of class': '3', 
            'tree': '4'
        }, 
        'int': {
            '42': '2'
        }
    }, 
    # The constructed concept block contains all constructed nodes.
    {
        # Each node is stored with a unique id. The "myTree" constructed node has the id "5".
        '5': [
            # Each connection is stored as a list of three elements.
            [0, '3', '4'], 
            [0, '1', '2'], 
            [0, '3', '4']
        ]
    }]

# An equivalent json object can be created from the network.
myJSONObject = saveRALJData([myTree], SRF)
# Eaven if only the "myTree" is mentioned, the other nodes are also stored in the json object because "myTree" depends on them.

# The json object can be loaded back into the RALFramework.
loadedNodesByTheirJsonNodeID = loadRALJData(myJSONObject, SRF)

# This loaded nodes are the same as the nodes that were created before.
for node in loadedNodesByTheirJsonNodeID.values():
    assert node in [tree, treeAgeInYears, hasAge, isInstanceOfClass, myTree]

# The nodes can also be saved and loaded from a file.
saveRALJFile([myTree], "output.ralj", SRF)
loadedNodesByTheirJsonNodeID = loadRALJFile("output.ralj", SRF)



# Manage the stored nodes

# A list of all loaded nodes can be obtained from the RALFramework.
allNodes = SRF.getAllNodes()
assert set(allNodes) == {tree, treeAgeInYears, hasAge, isInstanceOfClass, myTree}

# The nodes are stored in the RALFramework only as long as they are referenced.
temporaryNode = SRF.Node("temporary")
numberOFNodesBefore = len(SRF.getAllNodes())
temporaryNode = None
numberOFNodesAfter = len(SRF.getAllNodes())
assert numberOFNodesBefore == numberOFNodesAfter + 1

# The nodes can be remembered to prevent them from being deleted.
temporaryNode = SRF.Node("temporary")
temporaryNode.remembered = True
numberOFNodesBefore = len(SRF.getAllNodes())
temporaryNode = None
numberOFNodesAfter = len(SRF.getAllNodes())
assert numberOFNodesBefore == numberOFNodesAfter

# The temporary node can be forgotten again.
for node in SRF.getAllNodes():
    # This only deletes the temporary node, because the other nodes are still referenced.
    node.remembered = False
    node = None
assert len(SRF.getAllNodes()) == numberOFNodesBefore - 1

# A node can also be removed by force.
temporaryNode = SRF.Node("temporary")
assert temporaryNode.isDeleted == False
temporaryNode.forceDeletion()
assert temporaryNode.isDeleted == True
assert not temporaryNode in SRF.getAllNodes()

# All nodes can be removed at once.
SRF.clearAllNodes()
assert len(SRF.getAllNodes()) == 0




# Create network

tree = SRF.Node("tree")
treeAgeInYears = SRF.Node("42", "int")
hasAge = SRF.Node("has age")
isInstanceOfClass = SRF.Node("is instance of class")
myTree = SRF.Node([(0, isInstanceOfClass, tree), (0, hasAge, treeAgeInYears)])
car = SRF.Node("car")
carAgeInYears = SRF.Node("5", "int")
myCar = SRF.Node([(0, isInstanceOfClass, car), (0, hasAge, carAgeInYears)])
carWithUnknownAge = SRF.Node([(0, isInstanceOfClass, car)])
collision = SRF.Node("collision")
carCollidesWithTree = SRF.Node([(0, isInstanceOfClass, collision), (car, 0, tree)])



# Search for nodes

# The loaded nodes can be searched for by their data.
foundNodes =  [*SRF.search(triples = [["searchedNode", isInstanceOfClass, tree]])]
assert foundNodes == [{"searchedNode": myTree}]

# The search can also have multiple results
foundNodes = [*SRF.search(triples = [["searchedNode1", isInstanceOfClass, "searchedNode2"]])]
assert len(foundNodes) == 4
for foundNode in foundNodes:
    assert foundNode in [{"searchedNode1": myTree, "searchedNode2": tree}, {"searchedNode1": myCar, "searchedNode2": car}, {"searchedNode1": carWithUnknownAge, "searchedNode2": car}, {"searchedNode1": carCollidesWithTree, "searchedNode2": collision}]

# One can also seach for multiple triples at once
foundNodes = [*SRF.search(triples = [["searchedThing", isInstanceOfClass, "searchedClass"], ["searchedThing", hasAge, "searchedAge"]])]
assert len(foundNodes) == 2
for foundNode in foundNodes:
    assert foundNode in [{"searchedThing": myTree, "searchedClass": tree, "searchedAge": treeAgeInYears}, {"searchedThing": myCar, "searchedClass": car, "searchedAge": carAgeInYears}]

# It is also possible to search for nodes that are constructed in a specific way
foundNodes = [*SRF.search(constructed = {"searchedNode": [[0, isInstanceOfClass, "searchedClass"]]})]
# This returns only the nodes that have exactly one base connection with the "isInstanceOfClass" predicate.
assert foundNodes == [{"searchedNode": carWithUnknownAge, "searchedClass": car}]

# If one would allow additional base connections a "+" can be added to the searched base connections
foundNodes = [*SRF.search(constructed = {"searchedNode": [[0, isInstanceOfClass, "searchedClass"], "+"]})]
# This returns all nodes that have at least one base connection with the "isInstanceOfClass" predicate.
assert len(foundNodes) == 4
for foundNode in foundNodes:
    assert foundNode in [{"searchedNode": myTree, "searchedClass": tree}, {"searchedNode": myCar, "searchedClass": car}, {"searchedNode": carWithUnknownAge, "searchedClass": car}, {"searchedNode": carCollidesWithTree, "searchedClass": collision}]

# One can also search for data nodes
foundNodes = [*SRF.search(data = {"searchedDataNode": (["searchedData"], ["searchedFormat"])})]
# If the data and the format are search variables, they are marked by being wrapped in a list.
# This query returns all data nodes.
assert len(foundNodes) == 7
for foundNode in foundNodes:
    assert foundNode in [{"searchedDataNode": node, "searchedData": node.data, "searchedFormat": node.format} for node in [tree, treeAgeInYears, hasAge, isInstanceOfClass, car, carAgeInYears, collision]]

# It is also possible to search for data nodes with a specific format
foundNodes = [*SRF.search(data = {"searchedDataNode": (["searchedData"], "int")})]
# This query returns all data nodes with the format "int".
assert len(foundNodes) == 2
for foundNode in foundNodes:
    assert foundNode in [{"searchedDataNode": treeAgeInYears, "searchedData": "42"}, {"searchedDataNode": carAgeInYears, "searchedData": "5"}]

# It is also possible to search for data nodes with a specific data
foundNodes = [*SRF.search(data = {"searchedDataNode": ("42", ["searchedFormat"])})]
# This query returns all data nodes with the data "42".
assert len(foundNodes) == 1
for foundNode in foundNodes:
    assert foundNode in [{"searchedDataNode": treeAgeInYears, "searchedFormat": "int"}]

# One can also combine the different search options
foundNodes = [*SRF.search(
    data = {"searchedDataNode": (["searchedData"], "int")},
    constructed = {"searchedConstructedNode": [[0, hasAge, "searchedDataNode"], "+"]},
    triples = [["searchedConstructedNode", isInstanceOfClass, "searchedClass"]])]
assert len(foundNodes) == 2
for foundNode in foundNodes:
    assert foundNode in [{"searchedDataNode": treeAgeInYears, "searchedConstructedNode": myTree, "searchedClass": tree, "searchedData": "42"}, {"searchedDataNode": carAgeInYears, "searchedConstructedNode": myCar, "searchedClass": car, "searchedData": "5"}]