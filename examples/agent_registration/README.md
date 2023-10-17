# Agent registration

This document provides an example showcasing the registration of two Agents in Sunfish. 

We can first start an Agent exposing a mocked CXL fabric.

```commandline
python ofmf-main.py -p 5002 -redfish-path ./Resources/CXLAgent/

```

And one for a mocked NVMe-oF fabric.

```commandline
python ofmf-main.py -p 5001 -redfish-path ./Resources/NVMeoFAgent/
```

In a similar fashion we start the Sunfish server. 
```commandline
python ofmf-main.py -redfish-path ./Resources/Sunfish/
```

At this stage, Agents and Sunfish are running with a different states, represented by different Redfish resource trees.

### Service Names resolution
In a datacenter environment Sunfish and Agents will likely run on 
different machines characterized by different endpoints.
While the JSONs payloads provided with this example use naming conventions 
to target different servers hosting our services, for simplicity we run both Sunfish and Agents on the local machine.

If you want to avoid updating the json file add the following to your `/etc/hosts`

```commandline
127.0.0.1 nvmeof01.ofa.org
127.0.0.1 cxl01.ofa.org
127.0.0.1 sunfish.ofa.org
```

Otherwise, update endpoint references in the JSON payloads and `curl` command to `127.0.0.1`

### Inspect initial state

As a first step we can check the state of Sunfish and verify that it's empty

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/AggregationService/AggregationSources
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources",
    "@odata.type": "#AggregationSourceCollection.AggregationSourceCollection",
    "Members": [],
    "Members@odata.count": 0,
    "Name": "AggregationSource Collection"
}

```

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Systems
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Name": "Computer System Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Systems"
}
```

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Fabrics
{
    "@odata.type": "#FabricCollection.FabricCollection",
    "Name": "Fabric Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Fabrics"
}
```

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Storage
{
    "@odata.type": "#StorageCollection.StorageCollection",
    "Name": "Storage Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Storage"
}
```

We can also check the state of the two Agents. 

For instance, the NVMEoF Agent exposes 2 fabrics, 2 drives and 0 systems.

```commandline
curl http://nvmeof01.ofa.org:5001/redfish/v1/Fabrics
{
    "@odata.type": "#FabricCollection.FabricCollection",
    "Name": "Fabric Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Fabrics/NVMeoF"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/Ethernet"
        }
    ],
    "@odata.id": "/redfish/v1/Fabrics"
}
```

```commandline
curl http://nvmeof01.ofa.org:5001/redfish/v1/Storage
{
    "@odata.type": "#StorageCollection.StorageCollection",
    "Name": "Storage Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/IPAttachedDrive1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/IPAttachedDrive2"
        }
    ],
    "@odata.id": "/redfish/v1/Storage"
}
```

```commandline
curl http://nvmeof01.ofa.org:5000/redfish/v1/Systems
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Name": "Computer System Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Systems"
}
```

The CXL Agent exposes 1 Fabric and 1 System and 0 storage drives.

```commandline
curl http://cxl01.ofa.org:5002/redfish/v1/Fabrics
{
    "@odata.type": "#FabricCollection.FabricCollection",
    "Name": "Fabric Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Fabrics/CXL"
        }
    ],
    "@odata.id": "/redfish/v1/Fabrics"
}
```

```commandline
curl http://cxl01.ofa.org:5002/redfish/v1/Systems
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Name": "Computer System Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/CXL-System"
        }
    ],
    "@odata.id": "/redfish/v1/Systems"
}
```

```commandline
curl http://cxl01.ofa.org:5002/redfish/v1/Storage
{
    "@odata.type": "#StorageCollection.StorageCollection",
    "Name": "Storage Collection",
    "Members@odata.count": 0,
    "Members": [],
    "@odata.id": "/redfish/v1/Storage"
}
```




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



### Register CXL and  NVMEoF Agents

We can now trigger the registration of both Agents by sending events to the Sunfish server.
```commandline
└❯./register-cxl-agent
Registering CXL Agent...
└❯./register-nvmeof-agent
Registering NVMeoF Agent...
```

### Inspect Sunfish state after the registration

Now we have 2 Aggregation Sources, one for the CXL Agent and one for the NVMEoF Agent
```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/AggregationService/AggregationSources
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources",
    "@odata.type": "#AggregationSourceCollection.AggregationSourceCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/AggregationService/AggregationSources/6963d033-e516-407b-8876-e935d61a010c"
        },
        {
            "@odata.id": "/redfish/v1/AggregationService/AggregationSources/e4a08d4f-d1fd-4489-8c28-8501aa718d0d"
        }
    ],
    "Members@odata.count": 2,
    "Name": "AggregationSource Collection"
}
```


Inspecting the AggregationSource we can retrieve:
- `ResourcesAccessed`: the list of resources managed by the Agent
- `ConnectionMethod`: method used to communicate to a given Agent access point

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/AggregationService/AggregationSources/6963d033-e516-407b-8876-e935d61a010c
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources/6963d033-e516-407b-8876-e935d61a010c",
    "@odata.type": "#AggregationSource.v1_2_6963d033-e516-407b-8876-e935d61a010c.AggregationSource",
    "HostName": "http://cxl01.ofa.org:5002",
    "Id": "6963d033-e516-407b-8876-e935d61a010c",
    "Links": {
        "ConnectionMethod": {
            "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/CXL"
        },
        "ResourcesAccessed": [
            "/redfish/v1/Fabrics/CXL",
            "/redfish/v1/Fabrics/CXL/Connections",
            "/redfish/v1/Fabrics/CXL/Connections/12",
            "/redfish/v1/Chassis/PCXL2",
            ......
```

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/AggregationService/AggregationSources/e4a08d4f-d1fd-4489-8c28-8501aa718d0d
{
    "@odata.id": "/redfish/v1/AggregationService/AggregationSources/e4a08d4f-d1fd-4489-8c28-8501aa718d0d",
    "@odata.type": "#AggregationSource.v1_2_e4a08d4f-d1fd-4489-8c28-8501aa718d0d.AggregationSource",
    "HostName": "http://nvmeof01.ofa.org:5001",
    "Id": "e4a08d4f-d1fd-4489-8c28-8501aa718d0d",
    "Links": {
        "ConnectionMethod": {
            "@odata.id": "/redfish/v1/AggregationService/ConnectionMethods/NVMeoF"
        },
        "ResourcesAccessed": [
            "/redfish/v1/Fabrics/NVMeoF",
            "/redfish/v1/Fabrics/Ethernet",
            "/redfish/v1/Fabrics/NVMeoF/Connections",
            "/redfish/v1/Fabrics/NVMeoF/Connections/1",
            "/redfish/v1/Fabrics/NVMeoF/Connections/3",
            "/redfish/v1/Fabrics/NVMeoF/EndpointGroups",
            ....
```

Plus all fabric, systems and drives are not explorable directly from the Sunfish server 
without any knowledge of the underlining Agents.


```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Systems
{
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Name": "Computer System Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/CXL-System"
        }
    ],
    "@odata.id": "/redfish/v1/Systems"
}
```
```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Fabrics
{
    "@odata.type": "#FabricCollection.FabricCollection",
    "Name": "Fabric Collection",
    "Members@odata.count": 3,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Fabrics/CXL"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/NVMeoF"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/Ethernet"
        }
    ],
    "@odata.id": "/redfish/v1/Fabrics"
}
```

```commandline
curl http://sunfish.ofa.org:5000/redfish/v1/Storage
{
    "@odata.type": "#StorageCollection.StorageCollection",
    "Name": "Storage Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/IPAttachedDrive1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/IPAttachedDrive2"
        }
    ],
    "@odata.id": "/redfish/v1/Storage"
```

### Reset Sunfish server state

You can reset the state of the Redfish resources as following:

```commandline
rm -r ../../Resources/Sunfish/Chassis/
rm -r ../.../Resources/Sunfish/Fabrics/
rm -r ../../Resources/Sunfish/Storage/
rm -r ../../Resources/Sunfish/Systems/
rm -r ../../Resources/Sunfish/AggregationService/AggregationSources/
rm -r ../../Resources/Sunfish/AggregationService/ConnectionMethods/

git checkout ../../Resources/Sunfish
```
