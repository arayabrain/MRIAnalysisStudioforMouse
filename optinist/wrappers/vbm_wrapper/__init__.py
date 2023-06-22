from .vbm_template import vbm_template
from .alignment import align_images


vbm_wrapper_dict = {
    'vbm': {
        'vbm_template': {
            'function': vbm_template,
            # Use conda settings (optional).
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'alignment': {
            'function': align_images,
            # Use conda settings (optional).
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
    },
}
