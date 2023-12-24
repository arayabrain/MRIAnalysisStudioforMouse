import datetime
import os
import pandas as pd

from glob import glob
from typing import Optional, Dict, List
from fastapi import APIRouter, status
from fastapi.responses import FileResponse, JSONResponse
import img2pdf
from PIL import Image
from optinist.api.dir_path import DIRPATH

from optinist.api.utils.check_path_format import check_path_format
from optinist.api.utils.json_writer import JsonWriter, save_tiff2json
from optinist.api.utils.filepath_creater import create_directory, join_filepath
from optinist.routers.const import ACCEPT_TIFF_EXT
from optinist.routers.experiment import get_last_experiment
from optinist.routers.fileIO.file_reader import JsonReader, Reader
from optinist.routers.model import JsonTimeSeriesData, OutputData, ImageCreationParams
from optinist.wrappers.vbm_wrapper.vbm_stats_visualization import vbm_stats_thresholding, create_stats_analysis_plot
import optinist.wrappers.vbm_wrapper.vbm.utils as utils

router = APIRouter()


@router.get("/outputs/inittimedata/{dirpath:path}", response_model=JsonTimeSeriesData, tags=['outputs'])
async def get_inittimedata(dirpath: str):
    file_numbers = sorted([
        os.path.splitext(os.path.basename(x))[0]
        for x in glob(join_filepath([dirpath, '*.json']))
    ])

    index = file_numbers[0]
    str_index = str(index)

    json_data = JsonReader.read_as_timeseries(
        join_filepath([dirpath, f'{str(index)}.json'])
    )

    return_data = JsonTimeSeriesData(
        xrange=[],
        data={},
        std={},
    )

    data = {
        str(i): {
            json_data.xrange[0]: json_data.data[json_data.xrange[0]]
        }
        for i in file_numbers
    }

    if json_data.std is not None:
        std = {
            str(i): {
                json_data.xrange[0]: json_data.data[json_data.xrange[0]]
            }
            for i in file_numbers
        }

    return_data = JsonTimeSeriesData(
        xrange=json_data.xrange,
        data=data,
        std=std if json_data.std is not None else {},
    )

    return_data.data[str_index] = json_data.data
    if json_data.std is not None:
        return_data.std[str_index] = json_data.std

    return return_data


@router.get("/outputs/timedata/{dirpath:path}", response_model=JsonTimeSeriesData, tags=['outputs'])
async def get_timedata(dirpath: str, index: int):
    json_data = JsonReader.read_as_timeseries(
        join_filepath([
            dirpath,
            f'{str(index)}.json'
        ])
    )

    return_data = JsonTimeSeriesData(
        xrange=[],
        data={},
        std={},
    )

    str_index = str(index)
    return_data.data[str_index] = json_data.data
    if json_data.std is not None:
        return_data.std[str_index] = json_data.std

    return return_data


@router.get("/outputs/alltimedata/{dirpath:path}", response_model=JsonTimeSeriesData, tags=['outputs'])
async def get_alltimedata(dirpath: str):
    return_data = JsonTimeSeriesData(
        xrange=[],
        data={},
        std={},
    )

    for i, path in enumerate(glob(join_filepath([dirpath, '*.json']))):
        str_idx = str(os.path.splitext(os.path.basename(path))[0])
        json_data = JsonReader.read_as_timeseries(path)
        if i == 0:
            return_data.xrange = json_data.xrange

        return_data.data[str_idx] = json_data.data
        if json_data.std is not None:
            return_data.std[str_idx] = json_data.std

    return return_data


@router.get("/outputs/data/{filepath:path}", response_model=OutputData, tags=['outputs'])
async def get_file(filepath: str):
    return JsonReader.read_as_output(filepath)


@router.get("/outputs/html/{filepath:path}", response_model=OutputData, tags=['outputs'])
async def get_html(filepath: str):
    return Reader.read_as_output(filepath)


@router.get("/outputs/image/{filepath:path}", response_model=OutputData, tags=['outputs'])
async def get_image(
    filepath: str,
    start_index: Optional[int] = 0,
    end_index: Optional[int] = 1
):
    filename, ext = os.path.splitext(os.path.basename(filepath))
    if ext in ACCEPT_TIFF_EXT:
        filepath = join_filepath([DIRPATH.INPUT_DIR, filepath])
        save_dirpath = join_filepath([
            os.path.dirname(filepath),
            filename,
        ])
        json_filepath = join_filepath([
            save_dirpath,
            f'{filename}_{str(start_index)}_{str(end_index)}.json'
        ])
        if not os.path.exists(json_filepath):
            save_tiff2json(filepath, save_dirpath, start_index, end_index)
    else:
        json_filepath = filepath

    return JsonReader.read_as_output(json_filepath)


@router.get("/outputs/csv/{filepath:path}", response_model=OutputData, tags=['outputs'])
async def get_csv(filepath: str):
    filepath = join_filepath([DIRPATH.INPUT_DIR, filepath])

    filename, _ = os.path.splitext(os.path.basename(filepath))
    save_dirpath = join_filepath([
        os.path.dirname(filepath),
        filename
    ])
    create_directory(save_dirpath)
    json_filepath = join_filepath([
        save_dirpath,
        f'{filename}.json'
    ])

    JsonWriter.write_as_split(
        json_filepath,
        pd.read_csv(filepath, header=None)
    )
    return JsonReader.read_as_output(json_filepath)


@router.get('/outputs/nifti_image/{path:path}', response_class=FileResponse, tags=['outputs'])
async def get_nifti_image(path: str):
    """ Send a NIfTI image file.

    Parameters
        ----------
        path : str
            Path to the NIfTi file.
    """

    # Set the path of the NIfTI image file.
    file_path = check_path_format('/' + path)

    if not os.path.isfile(file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'NIfTI image file cannot be found. {os.path.basename(file_path)}'}
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='image/nifti'
    )


@router.get('/outputs/png_image/{path:path}', response_class=FileResponse, tags=['outputs'])
async def get_png_image(path: str):
    """ Send a PNG image file.

    Parameters
        ----------
        path : str
            Path to the PNG file.
    """

    # Set the path of the NIfTI image file.
    file_path = check_path_format('/' + path)

    if not os.path.isfile(file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'PNG image file cannot be found. {os.path.basename(file_path)}'}
        )

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='image/png'
    )


def create_stats_analysis_plots(project_id: str, image_creation_params: ImageCreationParams):
    """ Create and save statistical analysis plots based on the image creation parameters.

    Parameters
        ----------
        project_id : str
        image_creation_params : ImageCreationParams
            Parameters to generate plots of the statistical analysis results.
            threshold : float, None, or 'auto'
                Applied to the threshold parameter of Nilearn's plot_stat_map() function.
                float: It is used to threshold the image.
                    values below the threshold (in absolute value) are plotted as transparent.
                None: The image is not thresholded.
                'auto': The threshold is determined magically by analysis of the image. Default is 1e-6.
            cut_coords : list[list[float], list[float], list[float]]
                A list of the coordinate list with which the cut is performed in the averaged brain images
                for the following three directions:
                [0] Coronal, [1] Sagittal, [2] Horizontal

    Returns
        ----------
        plot_file_path_dict : dict[str, list[str]]
            Key: Contrast pair name
            Value: A path list of the statistical analysis plots image files.
    """

    # Get the analysis ID from the latest ExptConfig data.
    last_expt_config = get_last_experiment(project_id)
    analysis_id = last_expt_config.unique_id

    # Threshold the statistical analysis results performed by the vbm_stats_analysis node.
    vbm_config = utils.load_config()
    p_val = vbm_config['stats_visualization']['p_value']
    thresholded_file_path_list = vbm_stats_thresholding(int(project_id), analysis_id, p_val)

    # Set sagittal, coronal, and horizontal directions.
    display_mode_list = ['y', 'x', 'z']

    project_name = utils.get_project_name(int(project_id))
    plot_file_path_dict = {}
    for thresholded_file_path in thresholded_file_path_list:
        output_dir_path = os.path.dirname(thresholded_file_path)
        contrasts_name = os.path.basename(output_dir_path)
        analysis_info_str = f'Project: {project_name}, Contrast: {contrasts_name}, P value: {p_val}, ' \
                            f'Creation date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        # Create plots at the specified coordinates in the cutting direction.
        plot_file_path_list = []
        for display_mode, cut_coords in zip(display_mode_list, image_creation_params.cut_coords):
            plot_title = analysis_info_str if display_mode == 'y' else None
            # Create and save a statistical analysis plot.
            plot_file_path = create_stats_analysis_plot(thresholded_file_path, display_mode,
                                                        image_creation_params.threshold[0], cut_coords, vbm_config,
                                                        plot_title, output_dir_path)
            plot_file_path_list.append(plot_file_path)
        plot_file_path_dict[contrasts_name] = plot_file_path_list

    return plot_file_path_dict


@router.post('/visualize/generate/{project_id}', response_model=Dict[str, List[str]], tags=['visualize'])
async def generate_stats_images(project_id: str, image_creation_params: ImageCreationParams):
    """ Send URLs of the statistical analysis plots image files.
    Plots were created based on the image creation parameters.

    Parameters
        ----------
        project_id : str
        image_creation_params : ImageCreationParams

    Returns
        ----------
        image_urls : list[str]
            A URL list of the statistical analysis plots image files.
    """

    VISUALIZE_GENERATE_API = '/visualize/generate/'

    # Create and save statistical analysis plots based on the image creation parameters.
    plot_file_path_dict = create_stats_analysis_plots(project_id, image_creation_params)

    # Set the corresponding URL list.
    image_urls = []
    for plot_file_path_list in plot_file_path_dict.values():
        image_urls += [VISUALIZE_GENERATE_API + plot_file_path for plot_file_path in plot_file_path_list]

    return {'image_urls': image_urls}


@router.post('/visualize/download/{project_id}', response_class=FileResponse, tags=['visualize'])
async def download_stats_report(project_id: str, image_creation_params: ImageCreationParams):
    """ Send a report PDF of the statistical analysis result plots.
    Plots were created based on the image creation parameters.

    Parameters
        ----------
        project_id : str
        image_creation_params : ImageCreationParams
    """

    VISUALIZE_DOWNLOAD_API = '/visualize/download/'
    PDF_FILE_NAME = 'stats_analysis_report.pdf'

    # Create and save statistical analysis plots based on the image creation parameters.
    plot_file_path_dict = create_stats_analysis_plots(project_id, image_creation_params)

    # Concatenate the plot images in each contrast pair.
    image_file_path_list = []
    for contrasts_name, plot_file_path_list in plot_file_path_dict.items():
        # Get the size of the concatenated image.
        image_width = 0
        image_height = 0
        for plot_file_path in plot_file_path_list:
            plot_image = Image.open(plot_file_path)
            if plot_image.width > image_width:
                image_width = plot_image.width
            image_height += plot_image.height

        # Paste each plot image.
        concatenated_image = Image.new('RGB', (image_width, image_height))
        y_pos = 0
        for plot_file_path in plot_file_path_list:
            plot_image = Image.open(plot_file_path)
            concatenated_image.paste(plot_image, (0, y_pos))
            y_pos += plot_image.height

        # Save the concatenated image.
        file_path = join_filepath([os.path.dirname(plot_file_path_list[0]), contrasts_name + '.png'])
        concatenated_image.save(file_path)
        image_file_path_list.append(file_path)

    # Save the concatenated images in a PDF.
    pdf_file_path = join_filepath([os.path.dirname(os.path.dirname(image_file_path_list[0])), PDF_FILE_NAME])
    with open(pdf_file_path, 'wb') as file:
        file.write(img2pdf.convert(image_file_path_list))

    if not os.path.isfile(pdf_file_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': f'Report file cannot be found. {os.path.basename(pdf_file_path)}'}
        )

    return FileResponse(
        path=VISUALIZE_DOWNLOAD_API + pdf_file_path,
        filename=os.path.basename(pdf_file_path),
        media_type='application/pdf'
    )
