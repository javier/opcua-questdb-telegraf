import argparse
import json
from opcua import Client

def browse_node(node, level=0, max_depth=10):
    if level > max_depth:
        return {"name": "MaxDepthReached", "node_id": ""}

    node_info = {
        "name": node.get_browse_name().to_string(),
        "node_id": node.nodeid.to_string()
    }
    children = []
    try:
        for child in node.get_children():
            children.append(browse_node(child, level + 1, max_depth))
    except Exception as e:
        node_info["error"] = str(e)

    if children:
        node_info["children"] = children
    return node_info

def main(server_url, output_file=None, max_depth=10):
    client = Client(server_url)
    client.connect()

    try:
        root = client.get_root_node()
        objects = root.get_child(["0:Objects"])
        
        nodes_info = browse_node(objects, max_depth=max_depth)

        # Print to stdout
        json_output = json.dumps(nodes_info, indent=4)
        print(json_output)

        # Also write to file if specified
        if output_file:
            with open(output_file, "w") as f:
                f.write(json_output)
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover nodes in an OPC UA server")
    parser.add_argument("--server-url", type=str, default="opc.tcp://milo.digitalpetri.com:62541/milo", help="OPC UA server URL")
    parser.add_argument("--output-file", type=str, help="File to output the nodes information")
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum depth for node browsing")

    args = parser.parse_args()
    main(args.server_url, args.output_file, args.max_depth)

