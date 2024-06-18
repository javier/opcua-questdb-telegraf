# OPC UA QuestDB Telegraf Integration


This project provides a setup to read data from an OPC UA server, process it using Telegraf, and store it in QuestDB.
The default configuration uses the public Milo OPC UA demo server at `opc.tcp://milo.digitalpetri.com:62541/milo`, but
you can also run a local instance of the Milo server following the instructions in the
[Milo OPC UA Demo Server](https://github.com/digitalpetri/opc-ua-demo-server) repository.



## Components

This repository has two main parts:

* Telegraf configuration file, at `telegraf_opcua_milo_server.conf`, which sets up input from the OPC UA server, collects
and transform the source data, and output to QuestDB.
* Auxiliary Python scripts: In case you want to interactively explore the metrics available at the OPC UA Server to
extend the existing telegraf config.


## Getting Started

### Prerequisites

- Python 3.8+
- Telegraf
- QuestDB

### Setup

1. **Clone the repository**:
   ```sh
   git clone https://github.com/javier/opcua-questdb-telegraf.git
   cd opcua-questdb-telegraf
   ```

2. **Set up environment variables**:

The behaviour of this integration can be configured via environment variables that are referenced at the telegraf
configuration file. To make things easier, this repository provides a `telegraf_env` with sensible default values.

```
export OPCUA_ENDPOINT="opc.tcp://milo.digitalpetri.com:62541/milo"
# Uncomment to use your own local Milo server
# export OPCUA_ENDPOINT="opc.tcp://127.0.0.1:62541/milo"
export TELEGRAF_LOG_FILE="/tmp/telegraf.log"
export RANDOM_METRICS_TABLE_NAME="opcua_metrics"
export SERVER_METRICS_TABLE_NAME="opcua_server_metrics"
export QUESTDB_HTTP_ENDPOINT="http://127.0.0.1:9000"
export QUESTDB_HTTP_TOKEN=""
export QUESTDB_SKIP_TLS_VERIFICATION=true
```

If you want to apply those defaults, or change anything you need and then apply the changes, just execute

   ```sh
   . ./telegraf_env
   ```

3. ** (optional) Install Python dependencies (only if using the auxiliary python scripts)**:

   ```sh
   pip install -r requirements.txt
   ```

### Start Collecting Data with Telegraf and QuestDB

If no environment variables were set, the defaults will be used. By default, the telegraf logs will be just to the standard
output. Please make sure QuestDB is up and running before starting Telegraf.

   ```sh
   telegraf --config telegraf_opcua_milo_server.conf
   ```

Telegraf will start and will connect to the server. You should see in the logs that metrics are collected every few seconds
and are flushed a few times a minute. Once you start metrics behind flushed, you can connect to the QuestDB web console,
which defaults to http://localhost:9000, and issue queries like:

```sql
SELECT * from opcua_metrics;

SELECT * from opcua_server_metrics;
```

### The metrics being collected

The Milo demo server exposes several metrics. I choose some metrics from a namespace registered as "Dynamic" on the Milo OPC UA server, which just generate random integer and float numbers, and a few metrics from a namespace called "ServerStatus".

Since metrics come from the server in a sparse formar (each value comes as a different item), I am using some telegraf processors to pre-process the metrics, and then a telegraf aggregator to produce dense rows, with several metrics for the
same timestamp in a single row. Please refer to the comments in the `telegraf_opcua_milo_server.conf ` to learn more about this.

If you want to explore which other metrics are available in the server, or you want to connect to a different OPC UA server, you will need an OPC UA explorer to find the relevant metrics, or you can use the auxiliary Python scripts to explore the entities available in your server.


### Python Scripts

- **`discover_nodes.py`**: This script browses the OPC UA server and lists the available nodes. It can output the results to a JSON file. By default it will connect to the online Milo server and will output only to standard output, but it can be controlledlike this
```sh
python discover_nodes.py --server-url opc.tcp://127.0.0.1:62541/milo --output-file remote-nodes.json
```

- **`dynamic_values_opcua.py`**: This script subscribes to the same nodes we are using in the telegraf config file and outputs its values to standard output.

```sh
python dynamic_values_opcua.py --server-url opc.tcp://127.0.0.1:62541/milo
```

- **`nodes_info.py`**: This script provides node IDs for the nodes in the UPC UA server, to identify which are the node names we would need to use in the telegraf
config file if we want to collect extra metrics. It outputs to standard output, but since output can be large, it is advisable to redirect to a file.

```sh
python nodes_info.py > out.txt
```











