import math
import os

import nibabel as nib
import numpy as np


class NiftiImage:
    """
    Handle a NIfTI1-format image file and its image data.
    """

    def __init__(self, file_path: str):
        """
        [arguments]
        file_path: The path of a NIfTI1-format image file.
        """

        folder_path = os.path.join(os.path.dirname(file_path), 'derivatives', 'alignment')
        self.save_file_path = os.path.join(folder_path, os.path.basename(file_path))

        # Create the image object from the NIfTI file.
        self.img = nib.load(file_path)

    @property
    def image_data(self):
        return self.img.get_fdata()

    def update_affine_matrix(self, alignment_params):
        """
        Calculate a new affine transformation matrix with alignment parameters,
        and overwrite the NIfTI file with the matrix.
        """

        # Calculate a new affine transformation matrix.
        current_matrix = self.__create_affine_matrix_from_params(alignment_params)
        previous_matrix = self.__get_affine_matrix_from_file()
        new_affine_matrix = np.dot(current_matrix, previous_matrix)

        # Update the image object with the new matrix.
        self.img = nib.Nifti1Image(self.img.get_fdata(), new_affine_matrix, self.img.header)

        # Overwrite the NIfTI file.
        nib.save(self.img, self.save_file_path)

    def __get_affine_matrix_from_file(self):
        """
        Get the affine transformation matrix from the file header.
        The implementation is based on the "mat" case in the subsref() function of SPM12.
        """

        # Correct the affine transformation matrix.
        affine_matrix = np.dot(self.img.affine, np.hstack((np.eye(4, 3), np.array([[-1, -1, -1, 1]]).T)))

        # Scale the matrix.
        xyzt_units = self.__get_scale(self.img.header['xyzt_units'] & 7)
        if xyzt_units['scale'] > 0:
            scaling_factor = np.diag(np.hstack((xyzt_units['scale'] * np.array([1, 1, 1]), 1)))
            affine_matrix = np.dot(scaling_factor, affine_matrix)

        return affine_matrix

    def __get_scale(self, xyzt_units_num):
        """
        Get a scaling factor from the file header item "xyzt_units" based on their NIfTI-format definition.
        """

        num = xyzt_units_num
        if num == 0:
            return {'name': 'UNKNOWN', 'scale': 1}
        elif num == 1:
            return {'name': 'm', 'scale': 1000}
        elif num == 2:
            return {'name': 'mm', 'scale': 1}
        elif num == 3:
            return {'name': 'um', 'scale': 1e-3}
        elif num == 8:
            return {'name': 's', 'scale': 1}
        elif num == 16:
            return {'name': 'ms', 'scale': 1e-3}
        elif num == 24:
            return {'name': 'us', 'scale': 1e-6}
        elif num == 32:
            return {'name': 'Hz', 'scale': 1}
        elif num == 40:
            return {'name': 'ppm', 'scale': 1}
        elif num == 48:
            return {'name': 'rads', 'scale': 1}

    def __create_affine_matrix_from_params(self, params):
        """
        Create an affine transformation matrix from the following parameters:
          0: X translation
          1: Y translation
          2: Z translation
          3: X rotation (pitch (radians))
          4: Y rotation (roll (radians))
          5: Z rotation (yaw (radians))
          6: X scaling
          7: Y scaling
          8: Z scaling
          9: X affine
          10: Y affine
          11: Z affine.
        The implementation is based on the spm_matrix() function of SPM12.
        """

        translation_matrix = np.array([[1, 0, 0, params[0]],
                                       [0, 1, 0, params[1]],
                                       [0, 0, 1, params[2]],
                                       [0, 0, 0, 1]])

        # Create the rotation matrix.
        rotation_matrix_1 = np.array([[1, 0, 0, 0],
                                      [0, math.cos(params[3]), math.sin(params[3]), 0],
                                      [0, -math.sin(params[3]), math.cos(params[3]), 0],
                                      [0, 0, 0, 1]])

        rotation_matrix_2 = np.array([[math.cos(params[4]), 0, math.sin(params[4]), 0],
                                      [0, 1, 0, 0],
                                      [-math.sin(params[4]), 0, math.cos(params[4]), 0],
                                      [0, 0, 0, 1]])

        rotation_matrix_3 = np.array([[math.cos(params[5]), math.sin(params[5]), 0, 0],
                                      [-math.sin(params[5]), math.cos(params[5]), 0, 0],
                                      [0, 0, 1, 0],
                                      [0, 0, 0, 1]])

        rotation_matrix = rotation_matrix_1 @ rotation_matrix_2 @ rotation_matrix_3

        scaling_matrix = np.array([[params[6], 0, 0, 0],
                                   [0, params[7], 0, 0],
                                   [0, 0, params[8], 0],
                                   [0, 0, 0, 1]])

        shear_matrix = np.array([[1, params[9], params[10], 0],
                                 [0, 1, params[11], 0],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]])

        affine_matrix = translation_matrix @ rotation_matrix @ scaling_matrix @ shear_matrix

        return affine_matrix
