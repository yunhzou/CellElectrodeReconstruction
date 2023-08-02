import numpy as np
import cv2
import matplotlib.pyplot as plt
#generate Jelly roll simulation
#input parms:  Length, height
#strutural component: tabs, electrode surface
#color code: tabs: golden, cathode: dark grey, anode: balck, defects: white, golden strips


class Electrode:
    def __init__(self, height, width, overhang_length,flag_width, actual_ratio):
        "actual ratio: pixel to mm"
        self.height = height
        self.width = width
        self.flag_width = flag_width
        self.overhang_length = overhang_length
        self.actual_ratio = actual_ratio
        self.color_code()

    def color_code(
            self,
            act_mat = [128,128,128],
            flag = [51, 115, 184]
                   ):
        
        """BGR format"""
        self.color = {
            "act_mat":act_mat,
            "flag": flag
        }

    def gen_simulation(self):
        h,w = int(self.height/self.actual_ratio), int(self.width/self.actual_ratio) 
        active_mat = np.ones((h,w,3),np.uint8)*np.array(self.color["act_mat"], np.uint8)
        flag_base:int = int(self.flag_width/self.actual_ratio)
        flag_top:int = int(flag_base/2)
        flag_height:int = int(flag_base*1.3)
        img_height:int = flag_height+1
        flags = np.zeros((img_height,w,3), dtype=np.uint8)
        start_x:int = self.overhang_length
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
    def defect_simulation(self):
        pass

if __name__ == "__main__":
    e = Electrode(40,400,80,5,0.3)
    e.gen_simulation()
    img = e.electrode
    cv2.imwrite(r"C:\Users\Lenovo\Desktop\Personal Research\DissectionInspection\simulation\electrode.png",img)
    # Display image
    #cv2.imshow('Image', img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
