# What Is a Graph Database?

You can find tutorial [here](https://youtu.be/-6Xc2_IOh-0).

## Commands from the Tutorial

```bash
docker run \
  --publish=7474:7474 \
  --publish=7687:7687 \
  --env=NEO4J_PLUGINS='["graph-data-science"]' \
  --env=NEO4J_AUTH=none \
  neo4j:5.17.0
```

```bash
open http://localhost:7474/
```

## Create a node

```bash
MERGE (a:Location {name: 'A'})
RETURN a
```

## Get a node 

```bash
MATCH (a:Location {name: 'A'})
RETURN a
```

## Create another node

```bash
MERGE (a:Location {name: 'B'})
```

## Select all nodes and relationships

```bash
MATCH (n)
RETURN n
```

## Create a relationship between A and B

```bash
MATCH (a:Location {name: 'A'})
MATCH (b:Location {name: 'B'})
MERGE (a)-[:ROAD {cost: 50}]->(b)
```

## Search these nodes

```bash
MATCH (a:Location {name: 'A'})-[:ROAD]-(b:Location {name: 'B'})
RETURN a,b
```

## Create the rest of the nodes

```bash
CREATE (c:Location {name: 'C'}),
       (d:Location {name: 'D'}),
       (e:Location {name: 'E'}),
       (f:Location {name: 'F'});
```

## Select all nodes and relationships

```bash
MATCH (n)
RETURN n
```

## Create the remaining nodes and relationships

```bash
MATCH (a:Location {name: 'A'})
MATCH (b:Location {name: 'B'})
MATCH (c:Location {name: 'C'})
MATCH (d:Location {name: 'D'})
MATCH (e:Location {name: 'E'})
MATCH (f:Location {name: 'F'})
MERGE (a)-[:ROAD {cost: 50}]->(c)
MERGE (a)-[:ROAD {cost: 100}]->(d)
MERGE (b)-[:ROAD {cost: 40}]->(d)
MERGE (c)-[:ROAD {cost: 40}]->(d)
MERGE (c)-[:ROAD {cost: 80}]->(e)
MERGE (d)-[:ROAD {cost: 30}]->(e)
MERGE (d)-[:ROAD {cost: 80}]->(f)
MERGE (e)-[:ROAD {cost: 40}]->(f)
```

## Select all nodes and relationships

```bash
MATCH (n)
RETURN n
```

## [Optional] Create nodes and relationships in one statement

```bash
CREATE (a:Location {name: 'A'}),
       (b:Location {name: 'B'}),
       (c:Location {name: 'C'}),
       (d:Location {name: 'D'}),
       (e:Location {name: 'E'}),
       (f:Location {name: 'F'}),
       (a)-[:ROAD {cost: 50}]->(b),
       (a)-[:ROAD {cost: 50}]->(c),
       (a)-[:ROAD {cost: 100}]->(d),
       (b)-[:ROAD {cost: 40}]->(d),
       (c)-[:ROAD {cost: 40}]->(d),
       (c)-[:ROAD {cost: 80}]->(e),
       (d)-[:ROAD {cost: 30}]->(e),
       (d)-[:ROAD {cost: 80}]->(f),
       (e)-[:ROAD {cost: 40}]->(f);
```

## Create index

```bash
CALL gds.graph.project(
  'myGraph',
  'Location',
  'ROAD',
  {
    relationshipProperties: 'cost'
  }
)
```

## Calculate the shortest route

```bash
MATCH (source:Location {name: 'A'}), (target:Location {name: 'F'})
CALL gds.shortestPath.dijkstra.stream('myGraph', {
  sourceNode: source,
  targetNode: target,
  relationshipWeightProperty: 'cost'
})
YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
RETURN
  index,
  gds.util.asNode(sourceNode).name AS sourceNodeName,
  gds.util.asNode(targetNode).name AS targetNodeName,
  totalCost,
  [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
  costs,
  nodes(path) as path
ORDER BY index
```