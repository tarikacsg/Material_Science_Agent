# Materials Science Agent

A small agentic workflow for crystal-structure tasks:

1. LLM plans tool calls from a user request.
2. Materials Project provides the base structure.
3. `pymatgen` transforms/exports the structure.
4. Outputs are saved as POSCAR/CIF for simulation workflows.

## What this repo contains

- `main.py`: example entry point that sends one request to the agent.
- `agent.py`: LLM loop, tool schemas, and tool-calling logic.
- `tools.py`: materials tools (`fetch_structure`, `make_supercell`, export, describe).
- `state.py`: in-memory shared state across tool calls.
- `CH3NH3PbI3_2x2x2_POSCAR`: sample output file.
- `requirement.txt`: Python dependencies.

## Prerequisites

- Python 3.10+ (3.11+ recommended)
- A Materials Project API key (`MP_API_KEY`)
- A Triton/OpenAI-compatible API key (`TRITON_API_KEY`)

## Setup

1. Clone the repo:

```bash
git clone <your-repo-url>
cd Material_Science
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirement.txt
```

4. Create a `.env` file in the project root:

```env
TRITON_API_KEY=your_triton_key
MP_API_KEY=your_materials_project_key
```

## Run

Run the default example:

```bash
python main.py
```

By default, `main.py` sends:
`Create a 2x2x2 supercell for CH3NH3PbI3 and save POSCAR`

To run another task, edit the `request` string in `main.py`.

## Available Tools

The agent can call these tools from `tools.py`:

1. `fetch_structure(material)`
- Fetches a structure by formula from Materials Project and stores it in memory.

2. `make_supercell(scaling)`
- Builds a supercell from the loaded structure (example: `[2, 2, 2]`).

3. `save_poscar(filename="POSCAR")`
- Writes the current structure to VASP POSCAR format.

4. `save_cif(filename="structure.cif")`
- Writes the current structure to CIF format.

5. `describe_structure()`
- Returns a quick summary (formula, atom count).

## General Workflow

1. User gives a natural-language request.
2. `run_agent()` sends the request to the model with tool schemas.
3. Model decides whether to call a tool.
4. Python executes the tool and stores output in `STATE`.
5. Tool result is returned to the model as a tool message.
6. Steps repeat until the model returns a final response.
7. `main.py` prints final output and full tool history.

## Notes for GitHub users

- Keep `.env` out of git (do not commit secrets).
- The project currently uses Triton endpoint in `agent.py`:
  `https://tritonai-api.ucsd.edu/v1`
- If you switch providers, update the `OpenAI(...)` client configuration in `agent.py`.
