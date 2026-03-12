import unreal
import inspect

out_path = r'C:/Unreal Projects/rooty/RootyTooty/ik_retarget_signature.txt'
lines = []

fn = unreal.IKRetargetBatchOperation.duplicate_and_retarget
lines.append('FUNCTION: IKRetargetBatchOperation.duplicate_and_retarget')
try:
    lines.append('SIGNATURE: ' + str(inspect.signature(fn)))
except Exception as e:
    lines.append('SIGNATURE_ERROR: ' + str(e))

try:
    lines.append('DOC: ' + str(fn.__doc__))
except Exception as e:
    lines.append('DOC_ERROR: ' + str(e))

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('WROTE', out_path)
