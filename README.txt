Video Magnification.

Example usage:
>python main.py input_file

Applies alignment and video magnification to the video at input_file
The resulting videos are stored in a new folder output_vids/vidsX

Default magnification factor is 10x
To change the magnification factor, use the -m flag.
>python main.py input_file -m 20

Default is to use the whole video at input file
If you would like to only use the first frames of input_file use -n numframes
>python main.py input_file -n numframes

You can run more than one input file like the following
>python main.py input_file1 input_file2 ...
All of the flags will be applied to both videos and the results will be stored in separate folders in vid_output

positional arguments:
  input_file        video file(s) to be magnified (.mp4)

optional arguments:
  -h, --help        show this help message and exit
  -m MAGNIFICATION  magnification factor
  -d DYNAMIC_MODE   dynamic mode (yes/no)
  -r SAMPLE_RATE    sample rate (-1 for all)
  -n NUM_FRAMES     number of frames (-1 for all)
  -w                run the 'double warp' method 


