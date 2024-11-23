from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
from scipy.signal import butter, filtfilt
Constant = 0.12

def preprocess_image(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale and apply smoothing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)  # Apply median filtering for noise reduction

    # Apply adaptive thresholding for better boundary detection
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    return thresh

def find_upper_border(thresh):
    # Find the uppermost non-zero pixels in each column using Canny edge detector
    edges = cv2.Canny(thresh, 50, 150)  # Adjust the threshold values

    # Apply dilation to close small gaps
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Apply closing to fill small gaps
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Find upper border
    upper_border = np.argmax(edges, axis=0)

    return upper_border

def fill_gaps_with_previous(upper_border):
    # Fill gaps with the same number as the previous non-zero value
    for i in range(1, len(upper_border)):
        if upper_border[i] == 0:
            upper_border[i] = upper_border[i - 1]

    return upper_border

def smooth_and_plot(upper_border):
    # Smooth the upper border
    window_size = 5
    upper_border_smoothed = np.convolve(upper_border, np.ones(window_size) / window_size, mode='valid')

    # Plot the upper border
    plt.plot(upper_border_smoothed)
    plt.xlabel("Column Number")
    plt.ylabel("Row Number")
    plt.title("Smoothed Upper Border with Gaps Filled")
    plt.show()

# Load the image using OpenCV (replace 'your_image.jpg' with the path to your image)
def extract_tread(imgPath):
    image = cv2.imread(imgPath)

    # Get the red channel
    g1 = image[:, :, 2]

    # Create a mask to identify where the green pixel value is less than 200
    mask = g1 < 200

    # Set the pixel values to (0, 0, 0) for all channels where the mask is True
    image[mask] = [0, 0, 0]
    # Convert the numpy array to an image and save it
    # image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_PIL = Image.fromarray(gray_image)
    image_PIL.save('image.jpg')
    print("Tread Extraction From Image Completed.")
    return "image.jpg"
def load_binary_image(imgPath):
    """Load the binary image using OpenCV."""
    return cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)

def get_unique_pixels_coordinates(binary_image):
    """Get the coordinates of the non-zero (white) pixels in the binary image."""
    return np.where(binary_image > 100)

def spline_interpolation(x, y):
    """Perform spline interpolation."""
    f = interp1d(x, y, kind='cubic')
    return f

def apply_low_pass_filter(y_fit, window_size):
    """Apply low-pass filter (simple moving average)."""
    return np.convolve(y_fit, np.ones(window_size) / window_size, mode='same')

def find_relative_extrema(x_fit, y_smooth):
    """Find relative minima and maxima in the smoothed curve."""
    minima_indices = argrelextrema(y_smooth, np.less)
    maxima_indices = argrelextrema(y_smooth, np.greater)

    minima_x = x_fit[minima_indices]
    minima_y = y_smooth[minima_indices]

    maxima_x = x_fit[maxima_indices]
    maxima_y = y_smooth[maxima_indices]

    return minima_x, minima_y, maxima_x, maxima_y

def plot_smoothed_curve(x_fit, y_smooth):
    """Create a plot of the smoothed fitted curve."""
    plt.plot(x_fit, y_smooth, 'r-', label='Smoothed Curve', linewidth=2)

def plot_extrema(maxima_x, maxima_y, prev_x, prev_y):
    """Plot relative maxima and annotate the plot with differences."""
    for x, y in zip(maxima_x, maxima_y):
        if prev_x is not None and prev_y is not None and abs(y - prev_y) > 20:
            difference = abs(y - prev_y) * Constant
            plt.scatter(x, y, c='g', marker='o', s=100, label='Maxima')
            plt.annotate(f'Diff: {difference:.2f} mm', (x, y), textcoords="offset points", xytext=(0, -20), ha='center', fontsize=7)
            prev_x = x
            prev_y = y
        elif prev_x is None or prev_y is None:
            plt.scatter(x, y, c='g', marker='o', s=100, label='Maxima')
            plt.annotate(f'({x:.2f}, {y:.2f})', (x, y), textcoords="offset points", xytext=(0, -20), ha='center', fontsize=5)
            prev_x = x
            prev_y = y

def set_plot_properties(x_label, y_label, title):
    """Set properties for the plot."""
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)

def show_plot():
    """Show the plot."""
    plt.show()

def DrawGraph(image_path):
    thresh = preprocess_image(image_path)
    upper_border = find_upper_border(thresh)
    upper_border_filled = fill_gaps_with_previous(upper_border)
    smooth_and_plot(upper_border_filled)

imgPath = r"cop123.jpg"
removedBg = extract_tread(imgPath)
DrawGraph(removedBg)

