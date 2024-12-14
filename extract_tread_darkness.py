from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

Constant = 0.06  # Scaling factor

def preprocess_image(image_path):
    """
    Preprocess the image: Convert to grayscale, apply median blur and thresholding.
    Args:
        image_path (str): Path to the image file.
    Returns:
        numpy array: Thresholded image.
    """
    # Load the image
    image = cv2.imread(image_path)

    # Convert to grayscale and apply smoothing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)  # Apply median filtering for noise reduction

    # Apply adaptive thresholding for better boundary detection
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    return thresh

def find_upper_border(thresh):
    """
    Find the uppermost non-zero pixels in each column using edge detection.
    Args:
        thresh (numpy array): Thresholded image.
    Returns:
        numpy array: Array of the upper border positions for each column.
    """
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
    """
    Fill gaps in the upper border with the previous non-zero value.
    Args:
        upper_border (numpy array): Array of upper border positions.
    Returns:
        numpy array: Array with gaps filled.
    """
    # Fill gaps with the same number as the previous non-zero value
    for i in range(1, len(upper_border)):
        if upper_border[i] == 0:
            upper_border[i] = upper_border[i - 1]

    return upper_border

def truncate_data(upper_border, start=200, end=1400):
    """
    Truncate the data for the specified x-axis range.
    Args:
        upper_border (numpy array): Array representing the upper border.
        start (int): Start index for truncation.
        end (int): End index for truncation.
    Returns:
        numpy array: Truncated upper border.
    """
    return upper_border[start:end]

def smooth_and_plot_truncated_with_zero(upper_border, start=200, end=1400, scale=0.096):
    """
    Smooth the truncated upper border, scale it, and shift the central dip to 0.
    Args:
        upper_border (numpy array): Array representing the upper border.
        start (int): Start index for truncation.
        end (int): End index for truncation.
        scale (float): Scaling factor for the y-axis.
    """
    # Truncate the data
    truncated_border = truncate_data(upper_border, start, end)
    
    # Smooth the truncated data
    window_size = 5
    smoothed_truncated_border = np.convolve(truncated_border, np.ones(window_size) / window_size, mode='valid')
    
    # Scale the y-axis values
    scaled_smoothed_border = smoothed_truncated_border * scale
    
    # Shift the graph so that the central dip touches 0
    scaled_smoothed_border -= np.min(scaled_smoothed_border)
    
    # Generate x-axis values for the truncated data
    x_values = np.arange(start, start + len(scaled_smoothed_border))
    
    # Plot the truncated, smoothed, and shifted data
    plt.plot(x_values, scaled_smoothed_border, color='blue', label='Smoothed Border with Central Dip at 0')
    plt.xlabel("Column Number (Truncated)")
    plt.ylabel(f"Row Number (Scaled and Shifted)")
    plt.title(f"Smoothed Upper Border (Shifted: Central Dip at 0, Truncated: {start}-{end})")
    
    # Customize y-axis ticks to show 0.5 mm intervals
    y_min = 0
    y_max = np.ceil(np.max(scaled_smoothed_border) / 0.5) * 0.5  # Round up to the nearest 0.5
    y_ticks = np.arange(y_min, y_max + 0.5, 0.5)  # Create ticks at 0.5 mm intervals
    plt.yticks(y_ticks)
    
    plt.legend()
    plt.grid(True)
    plt.show()

def DrawGraphWithZero(image_path, start=200, end=1400, scale=0.096):
    """
    Preprocess the image, find the upper border, and plot a truncated graph with central dip touching 0.
    Args:
        image_path (str): Path to the image file.
        start (int): Start index for truncation.
        end (int): End index for truncation.
        scale (float): Scaling factor for the y-axis.
    """
    thresh = preprocess_image(image_path)
    upper_border = find_upper_border(thresh)
    upper_border_filled = fill_gaps_with_previous(upper_border)
    smooth_and_plot_truncated_with_zero(upper_border_filled, start, end, scale)

def extract_tread(imgPath):
    """
    Extract the tread from the image and save it as a grayscale image.
    Args:
        imgPath (str): Path to the input image.
    Returns:
        str: Path to the output grayscale image.
    """
    image = cv2.imread(imgPath)

    # Get the red channel
    g1 = image[:, :, 2]

    # Create a mask to identify where the green pixel value is less than 200
    mask = g1 < 200

    # Set the pixel values to (0, 0, 0) for all channels where the mask is True
    image[mask] = [0, 0, 0]
    # Convert the numpy array to an image and save it
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_PIL = Image.fromarray(gray_image)
    output_path = 'image.jpg'
    image_PIL.save(output_path)
    print("Tread Extraction From Image Completed.")
    return output_path

# Example usage
imgPath = r"captured_image_1734163333.jpg"
removedBg = extract_tread(imgPath)
DrawGraphWithZero(removedBg, start=300, end=50000, scale=Constant)
