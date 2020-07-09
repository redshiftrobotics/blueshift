'''
One of the challenges in the MATE 2020 Game was to follow two parallel lines on the ground
This script handles detecting both lines, calculating the average angle between the, and calculating the distance between them
'''

# Import necessary libraries
import cv2
import numpy as np

# Computer Vision Settings
lower_blue = np.array([70,119,87])
upper_blue = np.array([109,255,225])
kernel = np.ones((3,3), np.uint8)
min_countour_area = 20000.0

# Line Following Settings
percent_of_image_blue_lines_should_fill = 0.75 # Equal to (total_width - blue_to_red_dist) / total_width
target_angle = 90.0

def point_slope_line(pt, sl, num, given_axis):
    '''
    Calcualates a where a line intersects an input point

    The line is defined in point slope form (https://www.mathsisfun.com/algebra/line-equation-point-slope.html)
    The input number represents a horizontal or vertical line
    The goal of this function is to calculate where the two lines intersect

    Arguments:
        pt: The point that defines the line
        sl: The slope that defines the line
        num: The x OR y coordinate to intersect the line
        given_axis: Whether num is an x or y value
    
    Returns:
        The coordinate of itersection between the two lines
    '''
    if given_axis == "x":
        return (num, int(sl*(num-pt[0]) + pt[1]))
    elif given_axis == "y":
        return (int((num-pt[1])/sl + pt[0]), num)

def detectLines(img, debug=False):
    '''
    Detects two parallel lines in an image, and gets the distance between them and average angle

    Arguments:
        img: The image to detect lines in
        debug (optional): Whether to log debug information
    '''
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    filtered = cv2.erode(mask, kernel, iterations=1)
    filtered = cv2.dilate(filtered, kernel, iterations=15)
    filtered = cv2.erode(filtered, kernel, iterations=9)

    contours, hierarchy = cv2.findContours(filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # This will contain points on each line in the format: start, end, middle, and slope
    lines = []

    if len(contours) > 0:
        for contour in contours:
            if cv2.contourArea(contour) > min_countour_area:
                # Fit a line to the contour
                vx,vy,x,y = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)
                vx,vy,x,y = vx[0],vy[0],x[0],y[0]
                slope = vy/vx

                # Calculate where the line intersects the top and bottom of the image
                height = img.shape[1]
                line_top = point_slope_line((x,y),slope,0,"y")
                line_bottom = point_slope_line((x,y), slope, height, "y")

                if debug:
                    # Draw the line on the image
                    cv2.line(img, line_top,line_bottom, (0,0,0) ,5)
                    # Draw the center on the image
                    cv2.line(img,(x,y),(x,y),(0,255,0),10)

                # Append the start, end, middle, and slope of each line to the array
                lines.append([np.array(line_top), np.array(line_bottom), np.array([x,y]), slope])
        
        # Display images for debugging
        if debug:
            cv2.imshow("Input", img)
            cv2.moveWindow("Input", 50,50)

            cv2.imshow("Mask", filtered)
            cv2.moveWindow("Mask", 500,50)

            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Find the distance between the centers of both lines
        line_dist = np.linalg.norm(lines[0][2]-lines[1][2])

        # Calculate the angle of each line based on it's slope
        line_a_angle = np.degrees(np.arctan(lines[0][3]))
        line_b_angle = np.degrees(np.arctan(lines[1][3]))

        # Fix negative Angles
        if line_a_angle < 0:
            line_a_angle += 180
        if line_b_angle < 0:
            line_b_angle += 180

        # Average the angles for a more accurate result
        avg_angle = (line_a_angle+line_b_angle)/2
            
        return line_dist, avg_angle
    return None

img1 = cv2.imread("TL_1.png")
img2 = cv2.imread("TL_2.png")
img1_uw = cv2.imread("TL_1_UW.png")
img2_uw = cv2.imread("TL_2_UW.png")

print(detectLines(img1))
print(detectLines(img1_uw))
print(detectLines(img2))
print(detectLines(img2_uw, debug=True))
