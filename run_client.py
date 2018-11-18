from client.pi3.JPCClient import JPCClient
import argparse
import os
import sys

path = os.path.dirname(__file__)
sys.path.append(path)

def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, help="server ip address")
    return parser.parse_args()


if __name__ == '__main__':
    args = handle_args()
    client = JPCClient(args.ip)
    client.run()
