import cv2
from math import cos, sin, atan, sqrt, radians, acos, degrees, asin
import imutils
from PIL import Image
from PIL import ImageTk


class ImageManager:
    def __init__(self):
        self.rotate_scale_factor = 16
        self.load_method = cv2.IMREAD_UNCHANGED
        self.scale_up_method = cv2.INTER_NEAREST
        self.scale_down_method = cv2.INTER_AREA
        self.scale_default_method = cv2.INTER_NEAREST

        self.allowed_angles = (0,
                               11.31,  # 1/5
                               18.43,  # 1/3
                               26.57,  # 1/2
                               33.69,  # 2/3
                               )

    def rotate_image(self, image, deg, scale=None):
        """
        Rotates given image by given angle.
        Scales up image before rotate and scale down to original dimensions afterwards for better quality.
            :param image: Image in cv2 format
            :param deg: Degree of rotation.
            :param scale: The larger the scale, the slower the rotate function is.
            :return: Rotated image
        """
        if scale is None:
            scale = self.rotate_scale_factor
        if scale != 0:
            scaled_up = self.resize(image, scale, self.scale_up_method)
            rotated_image = imutils.rotate_bound(scaled_up, angle=deg)
            scaled_down = self.resize(rotated_image, 1 / scale, self.scale_down_method)
            return scaled_down
        else:
            rotated_image = imutils.rotate_bound(image, angle=deg)
            return rotated_image

    def resize(self, image, scale_factor, interpolation=None):
        """
        Resizes image with given scale factor and interpolation method.
            :param image: Image in cv2 format
            :param scale_factor: The image will be scaled by this factor.
            :param interpolation: Interpolation type, e.g.: cv2.IMREAD_UNCHANGED, cv2.INTER_NEAREST, cv2.INTER_AREA etc.
            :type scale_factor: float or int
            :return: Resized image shape.
        """
        if interpolation is None:
            interpolation = self.scale_default_method
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=interpolation)
        return resized

    def get_allowed_angles_list(self):
        """
        Creates list of allowed angles for full rotation, from 45 deg part
            :return: angle_list - Allowed angles for full rotation.
        """
        angle_list = []
        angle_amt = len(self.allowed_angles)
        for n in range(40):
            angle = self.allowed_angles[n - int(n / angle_amt) * angle_amt] + int(n / angle_amt) * 45
            angle_list.append(angle)
        return angle_list

    def load_image(self, path):
        image = cv2.imread(path, self.load_method)
        return image

    @staticmethod
    def convert_image_to_tk(cv2_image):
        blue, green, red, alpha = cv2.split(cv2_image)
        merged_img = cv2.merge((red, green, blue, alpha))
        image_array = Image.fromarray(merged_img)
        tk_image = ImageTk.PhotoImage(image=image_array)
        return tk_image

    def pixel_friendly_rotates(self, img, mirror=True, selected_px=(0, 0)):
        image_list_cv2 = []
        image_list_tk = []
        angle_list = []
        grip_list = []
        angle_amt = len(self.allowed_angles)
        image_angles = int((360 / 45) * angle_amt)

        for n in range(image_angles):
            angle = self.allowed_angles[n - int(n / angle_amt) * angle_amt] + int(n / angle_amt) * 45

            origin_dim_x = int(img.shape[1])
            origin_dim_y = int(img.shape[0])

            selected_x = selected_px[0]
            selected_y = selected_px[1]

            if angle <= 90:
                ax = selected_x
                ay = selected_x
                bx = origin_dim_y - selected_y
                by = selected_y
                beta = radians(angle)
            elif 90 < angle <= 180:
                ax = origin_dim_y - selected_y
                bx = origin_dim_x - selected_x
                ay = origin_dim_y - selected_y
                by = selected_x
                beta = radians(angle - 90)
            elif 180 < angle <= 270:
                ax = origin_dim_x - selected_x
                bx = selected_y
                ay = origin_dim_x - selected_x
                by = origin_dim_y - selected_y
                beta = radians(angle - 180)
            elif 270 < angle < 360:
                ax = selected_y
                bx = selected_x
                ay = selected_y
                by = origin_dim_x - selected_x
                beta = radians(angle - 270)
            else:
                ax = selected_x
                ay = selected_x
                bx = origin_dim_y - selected_y
                by = selected_y
                beta = radians(angle)

            cx = sqrt(ax ** 2 + bx ** 2)
            cy = sqrt(ay ** 2 + by ** 2)
            if cx == 0:
                alfa = asin(1)
            else:
                alfa = asin(ax / cx)
            omega = acos(ay / cy)
            grip_x = int(sin(alfa + beta) * cx + 0.5)
            grip_y = int(sin(omega + beta) * cy + 0.5)
            grip = (grip_x, grip_y)
            grip_list.append(grip)

            rotated_image = self.rotate_image(img, angle)

            marked_image = self.rotate_image(img, angle)
            for v in range(3):
                for h in range(3):
                    marked_image[grip_y - 1 + v, grip_x - 1 + h] = (0, 0, 0, 255)
            marked_image[grip_y, grip_x] = (255, 255, 255, 0)

            image_list_cv2.append(rotated_image)
            converted_img = self.convert_image_to_tk(marked_image)
            image_list_tk.append(converted_img)

            string = str(n).zfill(2) + '_' + str(angle) + "°"
            angle_list.append(string)

        if mirror:
            for i in range(40):
                angle = self.allowed_angles[i - int(i / angle_amt) * angle_amt] + int(i / angle_amt) * 45
                mirrored_image = cv2.flip(image_list_cv2[i], 1)
                width = int(mirrored_image.shape[1])
                mirrored_grip_x = (width - grip_list[i][0])
                mirrored_grip = (mirrored_grip_x, grip_list[i][1])
                grip_list.append(mirrored_grip)
                image_list_cv2.append(mirrored_image)
                converted_img = self.convert_image_to_tk(mirrored_image)
                image_list_tk.append(converted_img)
                string = str(i + 40).zfill(2) + '_' + str(angle) + "°" + "_mir"
                angle_list.append(string)

        return image_list_cv2, image_list_tk, angle_list, grip_list
