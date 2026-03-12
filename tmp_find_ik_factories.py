import unreal

out_path = r'C:/Unreal Projects/rooty/RootyTooty/ik_factory_symbols.txt'
syms = sorted([n for n in dir(unreal) if ('ik' in n.lower() or 'retarget' in n.lower()) and 'factory' in n.lower()])
with open(out_path, 'w', encoding='utf-8') as f:
    for s in syms:
        f.write(s + '\n')
print('WROTE', out_path)
