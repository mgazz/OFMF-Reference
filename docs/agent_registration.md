# Agent registration

This document describes how Agents inform the Sunfish server of their presence on the network. 

To mock the presence of an Agent, `emulator.py` needs to be executed following:

```commandline
python emulator.py -p 5001 -redfish-path ./AgentResources
```

Where `AgentResources` contains the redfish tree representation of an NVMe-oF fabric.


The Sunfish server can be executed with the command:
```commandline
python emulator.py -redfish-path ./SunFishResources
```

Where `SunFishResources` contains an empty redfish tree with no Fabrics or AggregationSources.


### Registration steps

Create a json event for a new AggregationSource
```commandline
cat << EOF | tee aggregation_source_discovered.json
{
"@odata.type": "#Event.v1_7_0.Event",
"Id": "1",
"Name": "AggregationSourceDiscovered",
"Context": "",
"Events": [ {
  "EventType": "Other",
  "EventId": "4594",
  "Severity": "Ok",
  "Message": "A aggregation source of connection method Redfish located at http://127.0.0.1:5001 has been discovered.",
  "MessageId": "Foo.1.0.AggregationSourceDiscovered",
  "MessageArgs": [ "Redfish", "http://127.0.0.1:5001" ],
  "OriginOfCondition": {
   "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/NVMeoF"
  }
}
]}
EOF
```

Send the event to the Sunfish server
```commandline
curl -X POST \
    -H "Content-Type: application/json" \
    -d @aggregation_source_discovered.json http://127.0.0.1:5000/EventListener
```

The Sunfish server now contains a new AggregationSource representing the Agent. 

```commandline
curl http://127.0.0.1:5000//redfish/v1/AggregationService/AggregationSources
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources",
    "@odata.type": "#AggregationSourceCollection.AggregationSourceCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/AggregationService/AggregationSources/2c143081-20a4-4c8c-8843-51e0c81ccd9f"
        }
    ],
    "Members@odata.count": 1,
    "Name": "AggregationSource Collection"
}
```

Inspecting the AggregationSource we can retrieve:
- `ResourcesAccessed`: the list of resources managed by the Agent
- `ConnectionMethod`: method used to communicate to a given Agent access point

```commandline
curl http://127.0.0.1:5000//redfish/v1/AggregationService/AggregationSources/2c143081-20a4-4c8c-8843-51e0c81ccd9f
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources/2c143081-20a4-4c8c-8843-51e0c81ccd9f",
    "@odata.type": "#AggregationSource.v1_2_2c143081-20a4-4c8c-8843-51e0c81ccd9f.AggregationSource",
    "HostName": "http://127.0.0.1:5001",
    "Id": "2c143081-20a4-4c8c-8843-51e0c81ccd9f",
    "Links": {
        "ConnectionMethod": {
            "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/NVMeoF"
        },
        "ResourcesAccessed": [
            "/redfish/v1/Fabrics/NVMeoF",
            "/redfish/v1/Fabrics/Ethernet"
        ]
    },
    "Name": "Agent 2c143081-20a4-4c8c-8843-51e0c81ccd9f"
}
```

```commandline
curl http://127.0.0.1:5000//redfish/v1/AggregationService/ConnectionMethods/NVMeoF
{
    "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/NVMeoF",
    "@odata.type": "#ConnectionMethod.v1_NVMeoF_NVMeoF.ConnectionMethod",
    "ConnectionMethodType": [
        "Redfish"
    ],
    "ConnectionMethodVariant": "Contoso",
    "Id": "NVMeoF",
    "Name": "ConnectionMethod"
}
```

Register Fabric

```commandline
curl http://127.0.0.1:5000//redfish/v1/AggregationService/AggregationSources/2c143081-20a4-4c8c-8843-51e0c81ccd9f
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources/2c143081-20a4-4c8c-8843-51e0c81ccd9f",
    "@odata.type": "#AggregationSource.v1_2_2c143081-20a4-4c8c-8843-51e0c81ccd9f.AggregationSource",
    "HostName": "http://127.0.0.1:5001",
    "Id": "2c143081-20a4-4c8c-8843-51e0c81ccd9f",
    "Links": {
        "ConnectionMethod": {
            "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/NVMeoF"
        },
        "ResourcesAccessed": [
            "/redfish/v1/Fabrics/NVMeoF",
            "/redfish/v1/Fabrics/Ethernet",
            "/redfish/v1/Fabrics/NVMeoF/Endpoints/D1-E1",
            "/redfish/v1/Fabrics/NVMeoF/Endpoints/D1-E2",
            "/redfish/v1/Fabrics/NVMeoF/Endpoints/Initiator1",
            "/redfish/v1/Fabrics/NVMeoF/Endpoints/Initiator2",
            "/redfish/v1/Fabrics/NVMeoF/Endpoints",
            "/redfish/v1/Fabrics/NVMeoF/EndpointGroups/1",
            "/redfish/v1/Fabrics/NVMeoF/EndpointGroups/TargetEPs",
            "/redfish/v1/Fabrics/NVMeoF/EndpointGroups",
            "/redfish/v1/Fabrics/NVMeoF/Connections/1",
            "/redfish/v1/Fabrics/NVMeoF/Connections/3",
            "/redfish/v1/Fabrics/NVMeoF/Connections"
        ]
    },
    "Name": "Agent 2c143081-20a4-4c8c-8843-51e0c81ccd9f"
}
```

### Register a new Fabric

```commandline
cat << EOF | tee fabric_created.json
{
"@odata.type": "#Event.v1_7_0.Event",
"Id": "1",
"Name": "Fabric Created",
"Context": "",
"Events": [ {
  "EventType": "Other",
  "EventId": "4595",
  "Severity": "Ok",
  "Message": "New Fabric Created ",
  "MessageId": "Resource.1.0.ResourceCreated",
  "MessageArgs": [],
  "OriginOfCondition": {
   "@odata.id": "/redfish/v1/Fabrics/NVMeoF"
  }
}
]}
EOF
```

```commandline
curl -X POST \
    -H "Content-Type: application/json" \
    -d @fabric_created.json http://127.0.0.1:5000/EventListener
```


**TODO:** register Fabric
```commandline
curl http://127.0.0.1:5000//redfish/v1/Fabrics
{
    "@odata.type": "#FabricCollection.FabricCollection",
    "Name": "Fabric Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Fabrics"
}
```

```commandline
curl http://127.0.0.1:5000//redfish/v1/Fabrics/NVMeoF
{
    "@Redfish.ReleaseStatus": "WorkInProgress",
    "@odata.id": "/redfish/v1/Fabrics/NVMeoF",
    "@odata.type": "#Fabric.v1_2_1.Fabric",
    "Connections": {
        "@odata.id": "/redfish/v1/Fabrics/NVMeoF/Connections"
    },
    "Description": "NVMeoF Fabric for EBOF",
    "EndpointGroups": {
        "@odata.id": "/redfish/v1/Fabrics/NVMeoF/EndpointGroups"
    },
    "Endpoints": {
        "@odata.id": "/redfish/v1/Fabrics/NVMeoF/Endpoints"
    },
    "FabricType": "NVMeOverFabrics",
    "Id": "NVMeoF",
    "Name": "NVMe-oF Fabric",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}
```