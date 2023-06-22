from .suite2p_wrapper import suite2p_wrapper_dict
from .vbm_wrapper import vbm_wrapper_dict

wrapper_dict = {}
wrapper_dict.update(**suite2p_wrapper_dict)
wrapper_dict.update(**vbm_wrapper_dict)
