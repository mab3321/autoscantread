from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
from scipy.signal import butter, filtfilt

# Load the image using OpenCV (replace 'your_image.jpg' with the path to your image)
def extract_tread(imgPath):
    image = cv2.imread(imgPath)

    # Get the red channel
    g1 = image[:, :, 2]

    # Create a mask to identify where the red pixel value is less than 200
    mask = g1 < 170

    # Set the pixel values to (0, 0, 0) for all channels where the mask is True
    image[mask] = [0, 0, 0]
    # Convert the numpy array to an image and save it
    # image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_PIL = Image.fromarray(gray_image)
    image_PIL.save('imageExplore.jpg')
    print("Tread Extraction From Image Completed.")
    return "imageExplore.jpg"
def load_binary_image(imgPath):
    """Load the binary image using OpenCV."""
    return cv2.imread(imgPath, cv2.IMREAD_GRAYSCALE)

def get_unique_pixels_coordinates(binary_image):
    """Get the coordinates of the non-zero (white) pixels in the binary image."""
    return np.where(binary_image > 230)

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
            difference = abs(y - prev_y) * 0.2462
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

def DrawGraph(imgPath):
    binary_image = load_binary_image(imgPath)
    row_indices, col_indices = get_unique_pixels_coordinates(binary_image)
    
    unique_y_values = {}
    for col, row in zip(col_indices, row_indices):
        if col not in unique_y_values:
            unique_y_values[col] = row

    unique_x = list(unique_y_values.keys())
    unique_y = list(unique_y_values.values())

    f = spline_interpolation(unique_x, unique_y)
    x_fit = np.linspace(min(unique_x), max(unique_x), num=1000)
    y_fit = f(x_fit)

    window_size = 25
    y_smooth = apply_low_pass_filter(y_fit, window_size)

    minima_x, minima_y, maxima_x, maxima_y = find_relative_extrema(x_fit, y_smooth)

    plot_smoothed_curve(x_fit, y_smooth)

    prev_x = None
    prev_y = None
    plot_extrema(maxima_x, maxima_y, prev_x, prev_y)

    set_plot_properties('X-axis (Column Index)', 'Y-axis (Row Index)', 'Smoothed Curve with Relative Minima and Maxima')
    show_plot()

imgPath = r"C:\Users\MAB\Downloads\back_right.jpg"
removedBg = extract_tread(imgPath)
DrawGraph(removedBg)

