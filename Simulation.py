import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import os

class Electrode:
    def __init__(self, height, width, overhang_length,flag_widths, actual_ratio):
        """
        _summary_:
        Initialize the electrode simulation class

        Args:
            height (_type_): The height of the flattened electrode
            width (_type_): The width of the flattened electrode
            overhang_length (_type_): Overhang length of the electrode in mm
            flag_widths (_type_): Flag width of the electrode in mm
            actual_ratio (_type_): Actual ratio of the electrode in mm/pixel
        """
        self.height = height
        self.width = width
        self.flag_width = flag_widths
        self.overhang_length = overhang_length
        self.actual_ratio = actual_ratio
        self.color_code()

    def color_code(
            self,
            act_mat = [128,128,128],
            flag = [51, 115, 184]
                   ):
        """
        _summary_:
        Provide self.color with color code for active material and flag

        Args:
            act_mat (list, optional): a list describe color code of the active material. Defaults to [128,128,128].
            flag (list, optional): a list describe color code of the flags. Defaults to [51, 115, 184].
        """
        self.color = {
            "act_mat":act_mat,
            "flag": flag
        }

    def add_alpha_channel(self):
        """
        _summary_:
        Add alpha channel to the electrode image
        """
        b, g, r = cv2.split(self.electrode)
        
        alpha = np.where((b==0) & (g==0) & (r==0), 0, 255)
        alpha = alpha.astype(np.uint8)
        rgba_img = cv2.merge([b, g, r, alpha])
        rgba_img = rgba_img[:, :, [2, 1, 0, 3]]
        self.electrode = rgba_img

    def gen_simulation(self):
        """
        _summary_:
        Generate the electrode simulation image
        """
        h,w = int(self.height/self.actual_ratio), int(self.width/self.actual_ratio) 
        active_mat = np.ones((h,w,3),np.uint8)*np.array(self.color["act_mat"], np.uint8)
        flag_base:int = int(self.flag_width/self.actual_ratio)
        flag_top:int = int(flag_base/2)
        flag_height:int = int(flag_base*1.3)
        img_height:int = flag_height+1
        flags = np.zeros((img_height,w,3), dtype=np.uint8)
        oh_length: int = int(self.overhang_length/self.actual_ratio)
        start_x:int = oh_length
        while start_x < flags.shape[1] - flag_base:
            # Define trapezoid points
            pts = np.array([[start_x, img_height], 
                            [start_x + flag_base, img_height], 
                            [start_x + flag_base - flag_top//2, img_height - flag_height], 
                            [start_x + flag_top//2, img_height - flag_height]], np.int32)
            # Reshape points
            pts = pts.reshape((-1,1,2))
            # Fill trapezoid
            cv2.fillPoly(flags, [pts], tuple(self.color["flag"]))
            # Move start_x
            start_x += flag_base

        self. electrode = np.vstack((flags,active_mat))
        #self. add_alpha_channel()

    def defect_simulation(self):
        pass

def create_spiral(wraps, points_per_wrap, desired_total_length):
    """
    _summary_:
    Create a spiral with the specified number of wraps, points per wrap, and desired total length

    Args:
        wraps (_type_): How many wraps the spiral should have
        points_per_wrap (_type_): How many points per wrap the spiral should have
        desired_total_length (_type_): The desired total length of the spiral
    """
    # Spiral expansion factor (initial guess)
    scale = 0.04546240964121108

    # Core radius (initial guess)
    core_radius = 3.1421354330354223

    while True:
        # Create the t parameter space, adding core radius after calculating theta
        t = np.linspace(0, 2 * np.pi * wraps, points_per_wrap * wraps)
        # Create spiral coordinates
        r = scale * t + core_radius
        # Create spiral coordinates
        x = r * np.cos(t)
        y = r * np.sin(t)
        # Calculate length between points using Pythagorean theorem
        length = np.sqrt(np.diff(r)**2 + (r[:-1] * np.diff(t))**2)
        length = np.insert(length, 0, 0)

        # Calculate total length
        total_length = np.sum(length)

        # Update scale based on ratio of total length to desired total length
        scale *= desired_total_length / total_length

        # Update core radius to be 1/8 of final radius
        core_radius = r.max() / 8

        # Check if total length is close to desired total length
        if np.abs(total_length - desired_total_length) < 1e-3:
            break

    # Create dataframe
    df = pd.DataFrame({'x': x, 'y': y, 'r': r, 'theta': t, 'length': length, 'total_length': np.cumsum(length)})

    # Save to CSV
    df.to_csv('spiral.csv', index=False)

    # Plot the spiral
    plt.figure(figsize=(6,6))
    plt.plot(x, y)
    plt.gca().set_aspect('equal', adjustable='box')  # to keep the aspect ratio
    plt.show()

    print(f'Scale: {scale}, Core radius: {core_radius}, Total length: {total_length}')





if __name__ == "__main__":
    e = Electrode(70,3800,300,5,0.03)
    e.gen_simulation()
    StiImg = e.electrode
    #cv2.imwrite(r"C:\Users\Lenovo\Desktop\Personal Research\DissectionInspection\simulation\electrode.png",img)
    #create_spiral(scale=0.04546240964121108, wraps=55, points_per_wrap=100, core_radius=3.1421354330354223)
    # h,w,_ = StiImg.shape
    # width = 6000 
    # width_start = 4000
    # widthNum = np.arange(0,w,width_start)
    # for w in widthNum:
    #     img=StiImg[:,w:w+6000]
    #     #strName=str(h)+"-"+str(w)+".png"
    #     #cv2.imwrite(os.path.join(path,strName), img)
    #     white_rect = np.ones(img.shape, dtype=np.uint8) * 255
    #     res = cv2.addWeighted(img, 0.5, white_rect, 0.5, 1.0)
    #     StiImg[:,w:w+width] = res
    #     StiImg_s=cv2.resize(StiImg, (1900,50))
    #     cv2.imshow("Demo",StiImg_s)
    #     cv2.waitKey(100)