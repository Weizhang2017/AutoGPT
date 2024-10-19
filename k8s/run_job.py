from pv import PV
from pod import Pod

import argparse

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="A simple script using argparse")

    # Add arguments
    parser.add_argument(
        '--agent', 
        type=str, 
        required=True, 
        help='agent name'
    )
    
    parser.add_argument(
        '--pvc', 
        type=str, 
        required=True, 
        help='pvc name'
    )

    parser.add_argument(
    '--ns', 
    type=str, 
    required=True, 
    help='namespace'
    )
    
    parser.add_argument(
    '--pod', 
    type=str, 
    required=True, 
    help='pod name'
    )

    
    # Parse the arguments
    args = parser.parse_args()

    pv = PV(args.pvc, args.ns)
    pv.create_pv()
    pod = Pod(args.pvc, args.pod, args.ns)
    pod.create_pod()

    print(f"create pod with pv {args.pvc} in namespace {args.ns}")

if __name__ == "__main__":
    main()
