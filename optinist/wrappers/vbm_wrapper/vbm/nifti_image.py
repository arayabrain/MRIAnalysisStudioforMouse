import math

import numpy as np


class NiftiImage:
    """
    Handle a NIfTI1-format image data.
    """

    def __init__(self, image_file_path: str):
        """
        [arguments]
        file_path: NIfTI1-format image file path.
        """

        from nibabel import load

        self.image_file_path = image_file_path

        # Create the NIfTI image object from the file.
        self.img = load(image_file_path)

    @property
    def image_data(self):
        """
        Return the raw image data without affine transformation.
        """
        return self.img.get_fdata()

    def update_affine_matrix(self, alignment_params, save_file_path: str = None):
        """
        Calculate a new affine transformation matrix with alignment parameters,
        and update the NIfTI image object with the matrix.
        """

        from nibabel import Nifti1Image

        # Calculate a new affine transformation matrix.
        current_matrix = self.__create_affine_matrix_from_params(alignment_params)
        new_affine_matrix = np.dot(current_matrix, self.img.affine)

        # Update the NIfTI image object with the new matrix.
        self.img = Nifti1Image(self.img.get_fdata(), new_affine_matrix, self.img.header)

    def __create_affine_matrix_from_params(self, params):
        """
        Create an affine transformation matrix from the following alignment parameters:
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

    def save(self, save_file_path: str = None):

        from nibabel import save

        # Overwrite the NIfTI file if save_file_path is not specified.
        if save_file_path is None:
            save_file_path = self.image_file_path

        save(self.img, save_file_path)
