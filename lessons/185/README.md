# What Is a Graph Database?

You can find tutorial [here](https://youtu.be/JXdM5jfQTvM).

## Commands

You need to install docker - https://docs.docker.com/engine/install/

```bash
docker run \
    --publish=7474:7474 \
    --publish=7687:7687 \
    --env=NEO4J_PLUGINS='["graph-data-science"]' \
    --env=NEO4J_AUTH=none \
    neo4j:5.15.0
```


go to - http://localhost:7474/ & click connect


```bash
MERGE (a:Location {name:"A"})
RETURN a
```


```bash
MATCH (a:Location {name:"A"})
RETURN a
```

```bash
MERGE (b:Location {name: 'B'})
```

```bash
MATCH (n)
RETURN n
```

```bash
MATCH (a:Location {name:"A"})
MATCH (b:Location {name:"B"})
MERGE (a)-[:ROAD {cost: 50}]->(b)
```

```bash
MATCH (a:Location {name:"A"})-[:ROAD]-(b:Location {name:"B"})
RETURN a, b
```

```bash
CREATE (c:Location {name: 'C'}),
       (d:Location {name: 'D'}),
       (e:Location {name: 'E'}),
       (f:Location {name: 'F'});
```

```bash
MATCH (n)
RETURN n
```

```bash
MATCH (a:Location {name:"A"})
MATCH (b:Location {name:"B"})
MATCH (c:Location {name:"C"})
MATCH (d:Location {name:"D"})
MATCH (e:Location {name:"E"})
MATCH (f:Location {name:"F"})
MERGE (a)-[:ROAD {cost: 50}]->(c)
MERGE (a)-[:ROAD {cost: 100}]->(d)
MERGE (b)-[:ROAD {cost: 40}]->(d)
MERGE (c)-[:ROAD {cost: 40}]->(d)
MERGE (c)-[:ROAD {cost: 80}]->(e)
MERGE (d)-[:ROAD {cost: 30}]->(e)
MERGE (d)-[:ROAD {cost: 80}]->(f)
MERGE (e)-[:ROAD {cost: 40}]->(f)
```

```bash
MATCH (n)
RETURN n
```

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
