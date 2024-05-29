from opcua import Client

def main():
    # Define the OPC UA server URL
    server_url = "opc.tcp://127.0.0.1:62541/milo"
    
    # Connect to the OPC UA server
    client = Client(server_url)
    client.connect()
    
    try:
        # Browse the root objects
        root = client.get_root_node()
        objects = root.get_child(["0:Objects"])
        
        # Function to recursively browse nodes
        def browse_node(node, level=0):
            node_name = node.get_browse_name().to_string()
            node_id = node.nodeid.to_string()
            print("  " * level + f"{node_name} ({node_id})")
            for child in node.get_children():
                browse_node(child, level + 1)
        
        # Start browsing from the Objects node
        browse_node(objects)
    
    finally:
        # Disconnect from the server
        client.disconnect()

if __name__ == "__main__":
    main()

