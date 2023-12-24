from .vbm_template import vbm_template
from .vbm_alignment import vbm_alignment
from .vbm_segment1 import vbm_segment1
from .vbm_masking import vbm_masking
from .vbm_segment2 import vbm_segment2
from .vbm_dartel import vbm_dartel
from .vbm_normalization import vbm_normalization
from .vbm_smoothing import vbm_smoothing
from .vbm_total_brain_volume import vbm_total_brain_volume
from .vbm_stats_modeling import vbm_stats_modeling
from .vbm_stats_analysis import vbm_stats_analysis


vbm_wrapper_dict = {
    'vbm': {
        'vbm_alignment': {
            'function': vbm_alignment,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_segment1': {
            'function': vbm_segment1,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_masking': {
            'function': vbm_masking,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_segment2': {
            'function': vbm_segment2,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_dartel': {
            'function': vbm_dartel,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_normalization': {
            'function': vbm_normalization,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_smoothing': {
            'function': vbm_smoothing,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_total_brain_volume': {
            'function': vbm_total_brain_volume,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_stats_modeling': {
            'function': vbm_stats_modeling,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_stats_analysis': {
            'function': vbm_stats_analysis,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        },
        'vbm_template': {
            'function': vbm_template,
            'conda_name': 'vbm',
            'conda_yaml': 'vbm_env.yaml',
        }
    },
}
