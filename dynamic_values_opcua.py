import argparse
from opcua import Client, ua
from opcua.common.callback import Callback
import time

class SubHandler(object):
    def datachange_notification(self, node, val, data):
        print(f"Data change on node {node}: {val}")
        self.print_nested_attributes(val)

    def event_notification(self, event):
        print(f"Event notification: {event}")

    def print_nested_attributes(self, val, indent=0):
        if hasattr(val, "__dict__"):
            for attr, value in val.__dict__.items():
                if not attr.startswith('_'):  # Ignore private and built-in attributes
                    if hasattr(value, "__dict__"):
                        print(" " * indent + f"{attr}:")
                        self.print_nested_attributes(value, indent + 2)
                    else:
                        print(" " * indent + f"{attr}: {value}")
        else:
            print(" " * indent + str(val))

def main(server_url):
    client = Client(server_url)
    client.connect()

    try:
        root = client.get_root_node()
        objects = root.get_child(["0:Objects"])

        nodes_to_monitor = [
            "ns=2;s=Dynamic/RandomInt32",
            "ns=2;s=Dynamic/RandomInt64",
            "ns=2;s=Dynamic/RandomFloat",
            "ns=2;s=Dynamic/RandomDouble",
            "i=2256",  # ServerStatus
            "i=2275",  # ServerDiagnosticsSummary
            "i=2290",  # SubscriptionDiagnosticsArray
            "i=2294",  # ServerCapabilities
        ]

        handler = SubHandler()
        subscription = client.create_subscription(500, handler)

        for node_id in nodes_to_monitor:
            try:
                node = client.get_node(node_id)
                subscription.subscribe_data_change(node)
            except ua.UaStatusCodeError as e:
                print(f"Error subscribing to node {node_id}: {e}")

        while True:
            time.sleep(1)  # Keep the script running to receive data changes

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor server diagnostics nodes in an OPC UA server")
    parser.add_argument("--server-url", type=str, default="opc.tcp://milo.digitalpetri.com:62541/milo", help="OPC UA server URL")
    
    args = parser.parse_args()
    main(args.server_url)

