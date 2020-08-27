
# main driver to parse arguements

import argparse
import homography
import utils
import os


# PUT CONFIGS HERE
BASELINE_CONFIG = "configs/o3f_hmhm2_bg_qnoise_mix4_nl_n_t_ds3.conf"
NEW_MODEL_CONFIG = "configs/rotation_displacement.conf"

def main():

    cur_dir = os.getcwd()
    
    parser = argparse.ArgumentParser(description='Video Magnification.')

    parser.add_argument('input_file', nargs='+',type=str,help='video file(s) to be magnified (.mp4)')
    parser.add_argument('-m', dest='magnification', type=int,help='magnification factor', default=10)
    parser.add_argument('-d', dest='dynamic_mode', type=str,help='dynamic mode (yes/no)', default='no')

    # new arguments! can use multiple
    # example usage: python main.py vids/frog.mp4 -w -b -a -t
    # runs all
    parser.add_argument('-w', dest='run_warp',action='store_const',const=True,default=False,help='"Double warp" approach')
    parser.add_argument('-b', dest='run_baseline',action='store_const',const=True,default=False,help='Baseline approach')
    parser.add_argument('-a', dest='run_alignment',action='store_const',const=True,default=False,help='Naive alignment approach')
    parser.add_argument('-t', dest='run_new',action='store_const',const=True,default=False,help='New model approach')
    
    parser.add_argument('-r', dest='sample_rate', type=int,help='sample rate (-1 for all)', default=-1)
    parser.add_argument('-n', dest='num_frames', type=int,help='number of frames (-1 for all)', default=-1)
    args = parser.parse_args()
    print("   Input File: " + str(args.input_file))
    print("Magnification: " + str(args.magnification)+"x")
    print(" Dynamic Mode: " + args.dynamic_mode)
    print(" Sample Rate: " + str(args.sample_rate))
    print("   NumFrames: " + str(args.num_frames))
    print("     RunWarp: " + str(args.run_warp))

    # parse flags
    rate_flag = ""
    if args.sample_rate != -1:
        rate_flag = " -r "+str(args.sample_rate)

    num_frames_flag = ""
    if args.num_frames != -1:
        rate_flag = " -vframes "+str(args.num_frames)

    vel_mag_flag = ""
    if args.dynamic_mode == "yes":
        vel_mag_flag= " --velocity_mag"

    for filename in args.input_file:

        # delete old frames
        delete_frames()

        # create new directory for output
        i = 0
        while os.path.exists("output_vids/vids%s" % i):
            i += 1
        newdir = "output_vids/vids%s" % i
        os.mkdir(newdir)

        # convert video to frames
        os.system("ffmpeg -i "+filename+" -f image2"+num_frames_flag+rate_flag+" frames/original_frames/%06d.png")

        # recombine original
        os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/original_frames/%06d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/original.mp4")

        if args.run_warp:
            # perform run_warp
            # combines align and magnify steps... not perfect, but produces interesting result
            # also warps every frame to the initial frame - as oppposed to warping to frame before it
                # consider another version which makes a compound representation of the warp to provide same result as previous homography
                    # always apply warp to align with previous warped image
            os.chdir("deep_motion_mag_tf2")    
            os.system("python main.py --config_file="+BASELINE_CONFIG+" --phase=run_warp --vid_dir=" #o3f_hmhm2_bg_qnoise_mix4_nl_n_t_ds3
                      +cur_dir+"/frames/original_frames --out_dir="
                      +cur_dir+"/frames/magnified_warp_frames"+vel_mag_flag+" --amplification_factor="+str(args.magnification))
            os.chdir("..")

            # recombine magnified
            os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/magnified_warp_frames/%06d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/mag"+str(args.magnification)+"xDoubleWarp.mp4")

        
            
        if args.run_alignment:
            # Naive approach
            # align frames
            homography.alignFrames("frames/original_frames","frames/aligned_frames")

            # recombine aligned
            os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/aligned_frames/%0d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/aligned.mp4")

            # perform aligned magnification
            os.chdir("deep_motion_mag_tf2")    
            os.system("python main.py --config_file="+BASELINE_CONFIG+" --phase=run --vid_dir="
                      +cur_dir+"/frames/aligned_frames --out_dir="
                      +cur_dir+"/frames/magnified_aligned_frames"+vel_mag_flag+" --amplification_factor="+str(args.magnification))
            os.chdir("..")

            # recombine aligned magnified
            os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/magnified_aligned_frames/%d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/mag"+str(args.magnification)+"xAligned.mp4")

        if args.run_new:
            os.chdir("deep_motion_mag_tf2")    
            os.system("python main.py --config_file="+NEW_MODEL_CONFIG+" --phase=run --model=warp --vid_dir="
                      +cur_dir+"/frames/original_frames --out_dir="
                      +cur_dir+"/frames/new_model_frames"+vel_mag_flag+" --amplification_factor="+str(args.magnification))
            os.chdir("..")

            # recombine new
            os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/new_model_frames/%06d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/mag"+str(args.magnification)+"xNewModel.mp4")

        if args.run_baseline:
            os.chdir("deep_motion_mag_tf2")    
            os.system("python main.py --config_file="+BASELINE_CONFIG+" --phase=run --vid_dir="
                      +cur_dir+"/frames/original_frames --out_dir="
                      +cur_dir+"/frames/baseline_frames"+vel_mag_flag+" --amplification_factor="+str(args.magnification))
            os.chdir("..")

            # recombine baseline
            os.system("ffmpeg -r 30 -f image2 -s 1920x1080 -i frames/baseline_frames/%06d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p "+newdir+"/mag"+str(args.magnification)+"xBaseline.mp4")

        


    

def delete_frames():
    # delete stored frames
    dirs = ["frames/aligned_frames/","frames/baseline_frames/","frames/magnified_warp_frames/","frames/original_frames/","frames/new_model_frames/","frames/magnified_aligned_frames"]
    for mydir in dirs:
        filelist = [ f for f in os.listdir(mydir) if f.endswith(".png") ]
        for f in filelist:
            os.remove(os.path.join(mydir, f))

    
if __name__ == "__main__":
    main()


