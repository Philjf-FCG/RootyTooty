import unreal

out_path = r'C:/Unreal Projects/rooty/RootyTooty/ik_method_docs.txt'
lines = []

def add_docs(obj, methods):
    lines.append(f'OBJECT {obj}')
    for m in methods:
        fn = getattr(obj, m, None)
        lines.append(f'METHOD {m}: {fn}')
        if fn is not None:
            try:
                lines.append(str(fn.__doc__))
            except Exception as e:
                lines.append(f'DOC_ERROR {e}')
        lines.append('---')

add_docs(unreal.IKRigController, [
    'get_controller', 'set_skeletal_mesh', 'apply_auto_generated_retarget_definition',
    'set_retarget_root', 'add_retarget_chain', 'get_retarget_chains'
])

add_docs(unreal.IKRetargeterController, [
    'get_controller', 'set_ik_rig', 'auto_map_chains', 'get_ik_rig', 'set_preview_mesh',
    'auto_align_all_bones', 'set_source_chain', 'set_current_retarget_pose', 'get_all_chain_settings'
])

add_docs(unreal.IKRetargetBatchOperation, ['duplicate_and_retarget'])

with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('WROTE', out_path)
