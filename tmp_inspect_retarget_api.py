import unreal

names = [n for n in dir(unreal) if 'retarget' in n.lower() or 'ikrig' in n.lower() or 'ik_' in n.lower()]
unreal.log('PY_API_BEGIN')
for n in sorted(names):
    unreal.log(f'PY_API {n}')
unreal.log('PY_API_END')

for t in ['AnimationLibrary', 'IKRigDefinition', 'IKRetargeter']:
    obj = getattr(unreal, t, None)
    if obj:
        unreal.log(f'PY_CLASS_BEGIN {t}')
        for n in sorted([x for x in dir(obj) if 'retarget' in x.lower() or 'ik' in x.lower() or 'rig' in x.lower()]):
            unreal.log(f'PY_CLASS {t}.{n}')
        unreal.log(f'PY_CLASS_END {t}')
