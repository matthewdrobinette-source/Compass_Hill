# Compass Hill

Master plan and 3D model of the Compass Hill Estate in southwest Ohio (Warren County, about 39.4° N).

| Path | What it is |
|---|---|
| [`Compass_Hill_Master_Plan.md`](Compass_Hill_Master_Plan.md) | The plan (Revision B). The source of truth for every dimension in the model. |
| [`Compass_Hill_Master_Plan.pdf`](Compass_Hill_Master_Plan.pdf) | Printable copy of the plan. |
| [`blender/`](blender) | Python scripts that build the whole estate in Blender from the plan's dimensions. |
| [`blender/CompassHill.blend`](blender/CompassHill.blend) | The built Blender scene (open in Blender 4.2+). |
| [`renders/`](renders) | Cycles stills of the estate. |
| [`walkthrough/`](walkthrough) | Interactive walkthrough: first and third person, doors, lights, elevator, golf cart. |
| [`tools/`](tools) | Floor-plan generator, the plan's PDF renderer, and `Get-CompassHill.ps1` to clone the repo on Windows. |

## Walk the estate

Serve the `walkthrough` folder and open it in a browser (it loads three.js from a CDN, so it needs internet):

```sh
cd walkthrough && python3 -m http.server 8000
# open http://localhost:8000
```

| Key | Does |
|---|---|
| WASD, mouse | Walk and look (click the view to capture the mouse) |
| Shift / Space | Run / jump |
| E | Open doors and gates, flip light switches, call and ride the elevator, light the fireplaces, turn cistern valves, board or leave a golf cart |
| V | First or third person |
| N | Late afternoon or night |
| Esc | Menu, with a list of places to jump to |

In a golf cart: W/S throttle, A/D steer. The house cart bay (under the front door) leads down the main tunnel to the loop around the cistern and west to the garage lobby and its covered ramp.

## Rebuild the model

The build uses Blender's Python module (`pip install bpy==4.2.0`, Python 3.11) and runs headless:

```sh
python3 blender/build.py                      # builds, saves build/CompassHill.blend, exports build/CompassHill.glb
python3 blender/build.py --render final       # also renders the stills (Cycles, CPU)
cp build/CompassHill.glb walkthrough/
```

`blender/compass_hill/` holds one module per part of the plan: `site.py` (terrain and pavements), `house.py`, `court.py` (pavilion, cistern, pads, covered walk, tunnels), `entrance.py`, `garage.py`, `landscape.py`, `furnish.py`, and `textures.py`, which generates the materials procedurally (fossil limestone, Vermont green slate, weathered white oak, standing seam, exposed-aggregate paving). Interactive objects carry their behavior as custom properties, which export as glTF extras for the walkthrough to read.

Blender 2.8 removed the built-in game engine, so the walk-around runs in the browser from Blender's export. Inside Blender you can still walk the scene with View ▸ Navigation ▸ Walk Navigation.

The model shows the full build-out (all seven pads, the Phase 2 garden and trails), with the tunnels as Phase 1 leaves them: the gate tunnel is a sealed stub under the court.
