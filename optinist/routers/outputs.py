import os

from typing import Dict, List
from fastapi import APIRouter, status
from fastapi.responses import FileResponse, JSONResponse
from optinist.api.dir_path import DIRPATH

from optinist.routers.model import ImageCreationParams
from optinist.api.dataclass.utils import check_path_format

router = APIRouter()


@router.get('/outputs/nifti_image/{path:path}', response_class=FileResponse, tags=['outputs'])
async def get_nifti_image(path: str):
    """
    Get the image data saved in an NIfTI file.
    """

    # TODO: Get the project path.
    # project_path = get_project_path()
    # Dummy
    project_path = os.path.join(DIRPATH.ROOT_DIR, r'../sample_data/cjs/1')
    file_path = check_path_format(os.path.join(project_path, 'derivatives', path))

    if not os.path.isfile(file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'Image file cannot be found. {file_path}'},
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='image/nifti'
    )


@router.get('/outputs/png_image/{path:path}', response_class=FileResponse, tags=['outputs'])
async def get_png_image(path: str):
    """
    Get the image data saved in a PNG file.
    """

    # TODO: Get the project path.
    # project_path = get_project_path()
    # Dummy
    project_path = os.path.join(DIRPATH.ROOT_DIR, r'../sample_data/cjs/1')
    file_path = check_path_format(os.path.join(project_path, 'derivatives', path))

    if not os.path.isfile(file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Image file cannot be found.'},
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='image/png'
    )


@router.post('/visualize/generate/{project_id}', response_model=Dict[str, List[str]], tags=['visualize'])
async def generate_stats_images(project_id: str, image_creation_params: ImageCreationParams):
    """
    Send URLs of statistical analysis image files, which were created with the image creation parameters.
    """

    GET_PNG_IMAGE_API = '/outputs/png_image/'

    # TODO: Create a statistical analysis images, and get a list of those URLs. How to get the analysis ID?
    # image_urls = vbm_visualization.create_stats_images(project_id, analysis_id, image_creation_params)
    # Dummy
    dir_path = '3a55fa37/stats_results/'
    file_names = ['Figure_1.png', 'Figure_2.png', 'Figure_3.png']
    image_urls = []
    for file_name in file_names:
        image_urls.append((GET_PNG_IMAGE_API + dir_path + file_name))

    return {'image_urls': image_urls}


@router.post('/visualize/download/{project_id}', response_class=FileResponse, tags=['visualize'])
async def download_stats_report(project_id: str, image_creation_params: ImageCreationParams):
    """
    Send a statistical analysis report saved in the PDF.
    """

    # TODO: Create a statistical analysis report PDF, and get its file path. How to get the analysis ID?
    # file_path = vbm_visualization.create_stats_report_pdf(project_id, analysis_id, image_creation_params)
    # Dummy
    project_path = os.path.join(DIRPATH.ROOT_DIR, r'../sample_data/cjs/1')
    dir_path = 'derivatives/3a55fa37/stats_results/'
    file_name = 'stats_report-1.pdf'
    file_path = check_path_format(os.path.join(project_path, dir_path, file_name))
    # file_path = os.path.join(DIRPATH.ROOT_DIR, r'../sample_data/cjs/1/derivatives/3a55fa37/stats_results/stats_report-1.pdf')

    if not os.path.isfile(file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'Report file cannot be found. {file_path}'},
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/pdf'
    )
