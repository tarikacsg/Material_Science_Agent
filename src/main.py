import sys

from agent import run_agent
from state import STATE

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if __name__ == "__main__":

    request = "Create a 2x2x2 supercell for CH3NH3PbI3 and save POSCAR"

    result = run_agent(request)

    print("\nFINAL OUTPUT:")
    print(result)

    print("\nTOOL HISTORY:")
    for step in STATE["history"]:
        print(step)
