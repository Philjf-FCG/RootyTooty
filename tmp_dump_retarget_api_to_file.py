import unreal
import json

out = {}
out['unreal_symbols'] = sorted([n for n in dir(unreal) if 'retarget' in n.lower() or 'ikrig' in n.lower() or 'ik_' in n.lower()])
for cls in ['AnimationLibrary', 'IKRigDefinition', 'IKRetargeter', 'IKRigController', 'IKRetargeterController']:
    obj = getattr(unreal, cls, None)
    if obj is None:
        out[cls] = None
    else:
        out[cls] = sorted([n for n in dir(obj) if 'retarget' in n.lower() or 'ik' in n.lower() or 'rig' in n.lower() or 'chain' in n.lower()])

path = r'C:/Unreal Projects/rooty/RootyTooty/retarget_api_dump.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
