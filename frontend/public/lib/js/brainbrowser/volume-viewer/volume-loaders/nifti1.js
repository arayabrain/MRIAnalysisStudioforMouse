/* eslint-disable no-extend-native */
/*
 * window.BrainBrowser: Web-based Neurological Visualization Tools
 * (https://window.BrainBrowser.cbrain.mcgill.ca)
 *
 * Copyright (C) 2011-2014
 * The Royal Institution for the Advancement of Learning
 * McGill University
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * Author: Nicolas Kassis
 * Author: Tarek Sherif <tsherif@gmail.com> (http://tareksherif.ca/)
 * Author: Robert D. Vincent <robert.d.vincent@mcgill.ca>
 *
 * Loads NIfTI-1 files for volume viewer. For details on the NIfTI-1 format,
 * see: http://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields
 */

;(function () {
  'use strict'

  Array.range = function (n) {
    return Array.apply(null, Array(n)).map((x, i) => i)
  }
  Object.defineProperty(Array.prototype, 'chunk', {
    value: function (n) {
      return Array.range(Math.ceil(this.length / n)).map((_x, i) =>
        this.slice(i * n, i * n + n),
      )
    },
  })

  var VolumeViewer = window.BrainBrowser.VolumeViewer

  VolumeViewer.volume_loaders.nifti1 = function (description, callback) {
    var error_message
    if (description.nii_url) {
      window.BrainBrowser.loader.loadFromURL(
        description.nii_url,
        function (nii_data) {
          parseNifti1Header(nii_data, function (header) {
            createNifti1Volume(header, nii_data, callback)
          })
        },
        { result_type: 'arraybuffer' },
      )
    } else if (description.nii_file) {
      window.BrainBrowser.loader.loadFromFile(
        description.nii_file,
        function (nii_data) {
          parseNifti1Header(nii_data, function (header) {
            createNifti1Volume(header, nii_data, callback)
          })
        },
        { result_type: 'arraybuffer' },
      )
    } else if (description.nii_source) {
      parseNifti1Header(description.nii_source, function (header) {
        createNifti1Volume(header, description.nii_source, callback)
      })
    } else {
      error_message =
        'invalid volume description.\n' +
        "Description must contain the property 'nii_url' or 'nii_file' or 'nii_source'."

      window.BrainBrowser.events.triggerEvent('error', {
        message: error_message,
      })
      throw new Error(error_message)
    }
  }

  VolumeViewer.utils.transformToMinc = function (transform, header) {
    var x_dir_cosines = []
    var y_dir_cosines = []
    var z_dir_cosines = []

    // A tiny helper function to calculate the magnitude of the rotational
    // part of the transform.
    //
    function magnitude(v) {
      var dotprod = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]
      if (dotprod <= 0) {
        dotprod = 1.0
      }
      return Math.sqrt(dotprod)
    }

    // Calculate the determinant of a 3x3 matrix, from:
    // http://www.mathworks.com/help/aeroblks/determinantof3x3matrix.html
    //
    // det(A) = A_{11} (A_{22}A_{33} - A_{23}A_{32}) -
    //          A_{12} (A_{21}A_{33} - A_{23}A_{31}) +
    //          A_{13} (A_{21}A_{32} - A_{22}A_{31})
    //
    // Of course, I had to change the indices from 1-based to 0-based.
    //
    function determinant(c0, c1, c2) {
      return (
        c0[0] * (c1[1] * c2[2] - c1[2] * c2[1]) -
        c0[1] * (c1[0] * c2[2] - c1[2] * c2[0]) +
        c0[2] * (c1[0] * c2[1] - c1[1] * c2[0])
      )
    }

    // Now that we have the transform, need to convert it to MINC-like
    // steps and direction_cosines.
    var xstep = 1
    var ystep = 1
    var zstep = 1

    if (header.xspace.step) {
      xstep = header.xspace.step
    }

    if (header.yspace.step) {
      ystep = header.yspace.step
    }
    if (header.zspace.step) {
      zstep = header.zspace.step
    }

    for (var i = 0; i < 3; i++) {
      x_dir_cosines[i] = transform[i][0] / xstep
      y_dir_cosines[i] = transform[i][1] / ystep
      z_dir_cosines[i] = transform[i][2] / zstep
    }

    header.xspace.step = xstep
    header.yspace.step = ystep
    header.zspace.step = zstep

    // Calculate the corrected start values.
    var starts = [transform[0][3], transform[1][3], transform[2][3]]

    // (bert): I believe that the determinant of the direction
    // cosines should always work out to 1, so the calculation of
    // this value should not be needed. But I have no idea if NIfTI
    // enforces this when sform transforms are written.
    var denom = determinant(x_dir_cosines, y_dir_cosines, z_dir_cosines)
    var xstart = determinant(starts, y_dir_cosines, z_dir_cosines)
    var ystart = determinant(x_dir_cosines, starts, z_dir_cosines)
    var zstart = determinant(x_dir_cosines, y_dir_cosines, starts)

    header.xspace.start = xstart / denom
    header.yspace.start = ystart / denom
    header.zspace.start = zstart / denom

    header.xspace.direction_cosines = x_dir_cosines
    header.yspace.direction_cosines = y_dir_cosines
    header.zspace.direction_cosines = z_dir_cosines
  }

  function parseNifti1Header(raw_data, callback) {
    var header = {
      order: [],
      xspace: {},
      yspace: {},
      zspace: {},
    }
    var error_message
    var dview = new DataView(raw_data, 0, 348)
    var bytes = new Uint8Array(raw_data, 0, 348)
    var littleEndian = true

    var sizeof_hdr = dview.getUint32(0, true)
    if (sizeof_hdr === 0x0000015c) {
      littleEndian = true
    } else if (sizeof_hdr === 0x5c010000) {
      littleEndian = false
    } else {
      error_message = 'This does not look like a NIfTI-1 file.'
    }

    var ndims = dview.getUint16(40, littleEndian)
    if (ndims < 3 || ndims > 4) {
      error_message = 'Cannot handle ' + ndims + '-dimensional images yet.'
    }

    var magic = String.fromCharCode.apply(null, bytes.subarray(344, 348))
    if (magic !== 'n+1\0') {
      error_message = "Bad magic number: '" + magic + "'"
    }

    if (error_message !== undefined) {
      window.BrainBrowser.events.triggerEvent('error', {
        message: error_message,
      })
      throw new Error(error_message)
    }

    var tlength = dview.getUint16(48, littleEndian)

    var datatype = dview.getUint16(70, littleEndian)
    var bitpix = dview.getUint16(72, littleEndian)

    var tstep = dview.getFloat32(92, littleEndian)

    var vox_offset = dview.getFloat32(108, littleEndian)
    if (vox_offset < 352) {
      vox_offset = 352
    }

    var scl_slope = dview.getFloat32(112, littleEndian)
    var scl_inter = dview.getFloat32(116, littleEndian)

    if (tlength >= 1) {
      header.time = {}
      header.time.space_length = tlength
      header.time.step = tstep
      header.time.start = 0
      header.time.name = 'time'
    }

    /* Record the number of bytes per voxel, and note whether we need
     * to swap bytes in the voxel data.
     */
    header.bytes_per_voxel = bitpix / 8
    header.must_swap_data = !littleEndian && header.bytes_per_voxel > 1

    function matrixTransform() {
      var nifti_xfm = niftiQuaternToMat44(header)
      header.xspace.reload = true
      header.yspace.reload = true
      header.zspace.reload = true
      var i, j
      var axis_index_from_file = [0, 1, 2]
      var transform = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
      ]

      for (i = 0; i < 3; i++) {
        var c_x = Math.abs(nifti_xfm[0][i])
        var c_y = Math.abs(nifti_xfm[1][i])
        var c_z = Math.abs(nifti_xfm[2][i])

        if (c_x > c_y && c_x > c_z) {
          header.order[2 - i] = 'xspace'
          axis_index_from_file[i] = 0
        } else if (c_y > c_x && c_y > c_z) {
          header.order[2 - i] = 'yspace'
          axis_index_from_file[i] = 1
        } else {
          header.order[2 - i] = 'zspace'
          axis_index_from_file[i] = 2
        }
      }

      for (i = 0; i < 3; i++) {
        for (j = 0; j < 4; j++) {
          var volume_axis = j
          if (j < 3) {
            volume_axis = axis_index_from_file[j]
          }
          transform[i][volume_axis] = nifti_xfm[i][j]
        }
      }
      VolumeViewer.utils.transformToMinc(transform, header)
    }

    matrixTransform()

    header[header.order[2]].space_length = dview.getUint16(42, littleEndian)
    header[header.order[1]].space_length = dview.getUint16(44, littleEndian)
    header[header.order[0]].space_length = dview.getUint16(46, littleEndian)

    if (tlength >= 1) {
      header.order.unshift('time')
    }

    header.datatype = datatype
    header.vox_offset = vox_offset
    header.scl_slope = scl_slope
    header.scl_inter = scl_inter
    header.update = matrixTransform
    if (window.BrainBrowser.utils.isFunction(callback)) {
      callback(header)
    }
  }

  /* This function is a direct translation of the identical function
   * found in the standard NIfTI-1 library (nifti1_io.c).
   */
  function niftiQuaternToMat44(header) {
    let mx = new window.THREE.Matrix4()
    mx.set(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    let my = mx.clone(mx)
    let mz = mx.clone(mx)

    if (typeof header.xspace.radian !== 'number') {
      header.xspace.radian = 0
    }

    if (typeof header.yspace.radian !== 'number') {
      header.yspace.radian = 0
    }
    if (typeof header.zspace.radian !== 'number') {
      header.zspace.radian = 0
    }

    mx.makeRotationX(header.xspace.radian)
    my.makeRotationY(header.yspace.radian)
    mz.makeRotationZ(header.zspace.radian)
    const m = mx.multiply(my).multiply(mz)

    header.matrix44 = m.elements

    return m.elements.chunk(4)
  }

  function createNifti1Volume(header, raw_data, callback) {
    var volume = VolumeViewer.createVolume(
      header,
      createNifti1Data(header, raw_data),
    )
    volume.type = 'nifti'
    volume.intensity_min = volume.header.voxel_min
    volume.intensity_max = volume.header.voxel_max
    volume.saveOriginAndTransform(header)
    if (window.BrainBrowser.utils.isFunction(callback)) {
      callback(volume)
    }
  }

  VolumeViewer.utils.swapn = function (byte_data, n_per_item) {
    for (var d = 0; d < byte_data.length; d += n_per_item) {
      var hi_offset = n_per_item - 1
      var lo_offset = 0
      while (hi_offset > lo_offset) {
        var tmp = byte_data[d + hi_offset]
        byte_data[d + hi_offset] = byte_data[d + lo_offset]
        byte_data[d + lo_offset] = tmp
        hi_offset--
        lo_offset++
      }
    }
  }

  function createNifti1Data(header, raw_data) {
    var native_data = null

    if (header.must_swap_data) {
      VolumeViewer.utils.swapn(
        new Uint8Array(raw_data, header.vox_offset),
        header.bytes_per_voxel,
      )
    }

    switch (header.datatype) {
      case 2: // DT_UNSIGNED_CHAR
        // no translation necessary; could optimize this out.
        native_data = new Uint8Array(raw_data, header.vox_offset)
        break
      case 4: // DT_SIGNED_SHORT
        native_data = new Int16Array(raw_data, header.vox_offset)
        break
      case 8: // DT_SIGNED_INT
        native_data = new Int32Array(raw_data, header.vox_offset)
        break
      case 16: // DT_FLOAT
        native_data = new Float32Array(raw_data, header.vox_offset)
        break
      case 64: // DT_DOUBLE
        native_data = new Float64Array(raw_data, header.vox_offset)
        break
      // Values above 256 are NIfTI-specific, and rarely used.
      case 256: // DT_INT8
        native_data = new Int8Array(raw_data, header.vox_offset)
        break
      case 512: // DT_UINT16
        native_data = new Uint16Array(raw_data, header.vox_offset)
        break
      case 768: // DT_UINT32
        native_data = new Uint32Array(raw_data, header.vox_offset)
        break
      default:
        // We don't yet support 64-bit, complex, RGB, and float 128 types.
        var error_message = 'Unsupported data type: ' + header.datatype
        window.BrainBrowser.events.triggerEvent('error', {
          message: error_message,
        })
        throw new Error(error_message)
    }

    var d = 0 // Generic loop counter.
    var slope = header.scl_slope
    var inter = header.scl_inter

    // According to the NIfTI specification, a slope value of zero means
    // that the data should _not_ be scaled. Otherwise, every voxel is
    // transformed according to value = value * slope + inter
    //
    if (slope !== 0.0) {
      var float_data = new Float32Array(native_data.length)

      for (d = 0; d < native_data.length; d++) {
        float_data[d] = native_data[d] * slope + inter
      }
      native_data = float_data // Return the new float buffer.
    }

    VolumeViewer.utils.scanDataRange(native_data, header)

    if (header.order.length === 4) {
      header.order = header.order.slice(1)
    }

    // Incrementation offsets for each dimension of the volume.
    header[header.order[0]].offset =
      header[header.order[1]].space_length *
      header[header.order[2]].space_length
    header[header.order[1]].offset = header[header.order[2]].space_length
    header[header.order[2]].offset = 1

    if (header.time) {
      header.time.offset =
        header.xspace.space_length *
        header.yspace.space_length *
        header.zspace.space_length
    }

    return native_data
  }
})()
