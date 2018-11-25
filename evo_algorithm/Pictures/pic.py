import cv2  # Not actually necessary if you just want to create an image.
import numpy as np



def images(blue, green, red):
    blank_image = np.zeros((512,512,3), np.uint8)

    blank_image[:,:,0] = np.ones((512,512), np.uint8)*blue #Blauwert
    blank_image[:,:,1] = np.ones((512,512), np.uint8)*green #Gruenwert
    blank_image[:,:,2] = np.ones((512,512), np.uint8)*red #Rotwert


    #cv2.imwrite('out.png', blank_image)
    

    return blank_image

def main():
    blue1=0
    blue2=255
    green1=0
    green2=255
    red1=0
    red2=255

    vis1=np.concatenate((images(blue1, green1, red1),images(blue2, green2, red2)), axis=0)
    vis2=np.concatenate((images(blue2, green2, red2),images(blue2, green2, red2)), axis=0)
    vis=np.concatenate((vis1,vis2), axis=1)
    
    cv2.imshow('Bild', vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()