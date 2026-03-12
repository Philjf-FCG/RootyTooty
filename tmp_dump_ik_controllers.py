import unreal

out_path = r'C:/Unreal Projects/rooty/RootyTooty/ik_controller_api_dump.txt'
lines = []

for name in ['IKRigController', 'IKRetargeterController', 'IKRetargetBatchOperation', 'IKRigDefinition', 'IKRetargeter']:
    obj = getattr(unreal, name, None)
    lines.append(f'CLASS {name}: {obj}')
    if obj:
        for m in sorted(dir(obj)):
            if m.startswith('_'):
                continue
            lines.append(f'  {m}')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('WROTE', out_path)
