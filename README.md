# Video-to-opticalflow

Convert videos to optical flow and visualizes them.

Inputs are video files outputs are zipped Numpy arrays with optical flow
data computed using OpenCV's Dual TV L1 algorithm
(https://docs.opencv.org/3.4/dc/d47/classcv_1_1DualTVL1OpticalFlow.html#details).

## Installation

```
git clone https://github.ibm.com/aur-bic/video-to-opticalflow
cd video-to-opticalflow
python setup.py develop
```

## Usage

To create optical flow data from input videos, run: 
`python video2flow.py config.json`

To visualize the created optical flow data, run: 
`python view_flows.py config.json`


## Configuration file

Specifies input and output folders for data, and other parameters.


`config.json`
```
{
  "videodir": "../data/in",
  "outdir": "../data/out",
  "videoext": "*.npy",
  "framerate": 0.1,
  "crop_width": 640,
  "crop_height": 1080,
  "downsample" 1.0,

  "view_mode": "arrow",
  "view_pause": 0.1,
  "view_downsample": 12
}
```

- `videodir` is path to folder with input videos in Numpy (*.npy) 
   or video formats (*.mp4)   
- `outdir` is path to folder where optical flow output will be written to.
- `videoext` file extension, `.npy` or `*.mp4`
- `framereate` rate frames are extracted from input video. Ignored if
   inputs are Numpy arrays.
- `crop_width` input is cropped to specified width.   
- `crop_height` input is cropped to specified height.  
- `downsample` input is down-sampled by with given factor (after cropping).
- `view_mode` is either 'arrow' or 'colors'. 'arrows' displays
   the optical flow as a vector field, while
- `view_pause` specifies the minimum waiting time after displaying
   an optical flow, e.g. 0.1 = 1/10 sec.
- `view_downsample` down samples the shown optical flow by the given
   factor (must be integer > 1).      

For `videoext = *.npy` input data is expected to be Numpy arrays of shape
`(T,H,W,3)`. Otherwise, video files, e.g. `*.mp4` are expected.

The frame rate parameter is ignored if the inputs are Numpy arrays
(`videoext = *.npy`). Otherwise, for a frame rate of 0, the original frame rate 
of the input video is used, e.g. 30 frames per second. A frame rate < 1 
can be specified, e.g. 0.1 is equal to 1 frame every 10 seconds.


## Example output for video conversion

```
$ python video2flow.py config.json

Processing 1 of 3 
3001_ArisingChairI_1.npy 100% (took: 0:02:08)
3001_ArisingChairI_2.npy 100% (took: 0:02:38)
3001_ArisingChairII_1.npy 100% (took: 0:03:01)
finished.
```

## Visualizing optical flow data

Run the follwing command to view the optical flow data written to
the output directory specified in `config.json`. Press `q` to stop the viewing.

```
$ python view_flows.py config.json
```




## Requirements

Will automatically be installed when running `setup.py`.  

- OpenCV: https://pypi.org/project/opencv-python/
- nuts-flow: https://maet3608.github.io/nuts-flow/
- keyboard: https://pypi.org/project/keyboard/
