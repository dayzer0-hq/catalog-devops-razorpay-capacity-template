"""Razorpay settlement worker. Has a batch mode that is genuinely memory-hungry."""
import json
import os
import sys
import time

# MB to allocate per batch. The end-of-day batch is the big one, and it is real allocation,
# not a sleep: the pod will actually be killed if the limit is below this.
BATCH_MB = int(os.environ.get("BATCH_MB", "64"))
MODE = os.environ.get("MODE", "steady")


def allocate(mb):
    """Holds mb megabytes so the number shows up in `kubectl top pod` and in a limit."""
    chunk = bytearray(1024 * 1024)
    held = [bytes(chunk) for _ in range(mb)]
    return len(held)


def main():
    print(json.dumps({"mode": MODE, "batch_mb": BATCH_MB}), flush=True)
    if MODE == "eod":
        print("end-of-day batch starting", flush=True)
        held = allocate(BATCH_MB)
        print(json.dumps({"allocated_mb": held}), flush=True)
        time.sleep(30)
    else:
        for cycle in range(3):
            allocate(max(1, BATCH_MB // 8))
            print(json.dumps({"cycle": cycle, "settled": 120}), flush=True)
            time.sleep(2)
    print("done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
