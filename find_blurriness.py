# import the necessary packages
from imutils import paths
import argparse
import cv2
import matplotlib.pyplot as plt
import numpy as np

variances_baseline = []
variances_double_warp = []
image_num = []
texts_baseline = []
texts_double_warp = []

def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i",
                "--images_baseline",
                required=True,
                help="path to input directory of baseline images")
ap.add_argument("-i2",
                "--images_double_warp",
                required=True,
                help="path to input directory of double warp images")

ap.add_argument(
    "-t",
    "--threshold",
    type=float,
    default=100.0,
    help="focus measures that fall below this value will be considered 'blurry'"
)
args = vars(ap.parse_args())

count = 0
# loop over the input images
for imagePath in paths.list_images(args["images_baseline"]):
    # load the image, convert it to grayscale, and compute the
    # focus measure of the image using the Variance of Laplacian
    # method
    image_num.append(count)
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    variances_baseline.append(fm)
    text = "Not Blurry"
    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    if fm < args["threshold"]:
        text = "Blurry"
    texts_baseline.append(text)
    # show the image
    # cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
    # cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
    # if count < 3:
    # cv2.imshow("Image", image)
    # key = cv2.waitKey(0)
    count += 1

count = 0
# loop over the input images
for imagePath in paths.list_images(args["images_double_warp"]):
    # load the image, convert it to grayscale, and compute the
    # focus measure of the image using the Variance of Laplacian
    # method
    # image_num.append(count)
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    variances_double_warp.append(fm)
    text = "Not Blurry"
    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    if fm < args["threshold"]:
        text = "Blurry"
    texts_double_warp.append(text)
    # show the image
    # cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
    # cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
    # if count < 3:
    # cv2.imshow("Image", image)
    # key = cv2.waitKey(0)
    count += 1


percents = []
#TODO: take the difference between variance for each frame and divide it by the variance for the baseline frame
# this means that the variance factor for the double warp frame is x% higher than for the baseline frame
# and plot this number across all frames
for i in range(0, len(variances_double_warp)):
    diff = variances_double_warp[i] - variances_baseline[i]
    percent = diff / variances_baseline[i]
    percent = percent*100
    percents.append(percent)


print("This is the text for baseline:", texts_baseline)
print("This is the text for double warp:", texts_double_warp)

# Create data
red = (255, 0, 0)
blue = (0,0,255)
area = np.pi * 3
image_num_x = np.asarray(image_num)
variances_baseline_y = np.asarray(variances_baseline)
variances_double_warp_y = np.asarray(variances_double_warp)
percents_y = np.asarray(percents)

# Plot
plt.plot(image_num_x, variances_double_warp_y, label="Double Warp")
plt.plot(image_num_x, variances_baseline_y, label="Baseline")
plt.title('Variance in double warp vs. baseline over the frames in the frog video')
plt.xlabel('Frame number')
plt.ylabel('Variance')
plt.legend(loc='best')
plt.show()
