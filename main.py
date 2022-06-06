import math
from math import cos, sin, atan, sqrt, radians, acos, degrees, asin

import cv2
from PIL import Image
from PIL import ImageTk
import imutils
from tkinter import Tk, Label, StringVar, Button, ttk, IntVar, Canvas, PhotoImage
import tkinter.filedialog

input_dir_path = 'input'
output_dir_path = 'output'


def convert_image_to_tk(cv2_image):
    blue, green, red, alpha = cv2.split(cv2_image)
    merged_img = cv2.merge((red, green, blue, alpha))
    image_array = Image.fromarray(merged_img)
    tk_image = ImageTk.PhotoImage(image=image_array)
    return tk_image


def save_img_to_file(name, img):
    cv2.imwrite('output/' + name + '.png', img)


class ImageEditor:
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

    def load_image(self, path):
        image = cv2.imread(path, self.load_method)
        return image

    def rotate_image(self, image, deg, scale=None):
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

    def resize(self, image, scale_factor, interpolation):
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=interpolation)
        return resized

    def pixel_friendly_rotates(self, img, mirror=True, selected_px=[0, 0]):
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

            x1 = abs(math.sin(math.radians(angle))*origin_dim_x)
            x2 = abs(math.cos(math.radians(angle))*origin_dim_y)
            y1 = abs(math.cos(math.radians(angle))*origin_dim_x)
            y2 = abs(math.sin(math.radians(angle))*origin_dim_y)
            new_height = int(x1 + x2)
            new_width = int(y1 + y2)

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
                ax = origin_dim_x
                bx = origin_dim_y - selected_y
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
                    marked_image[grip_y-1+v, grip_x-1+h] = (0, 0, 0, 255)
            marked_image[grip_y, grip_x] = (255, 255, 255, 0)

            image_list_cv2.append(rotated_image)
            converted_img = convert_image_to_tk(marked_image)
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
                converted_img = convert_image_to_tk(mirrored_image)
                image_list_tk.append(converted_img)
                string = str(i+40).zfill(2) + '_' + str(angle) + "°" + "_mir"
                angle_list.append(string)

        return image_list_cv2, image_list_tk, angle_list, grip_list


class App:
    def __init__(self):
        self.gui = Tk(className='Python Examples - Window Size')
        self.gui.geometry("1000x800")
        self.gui.title("Welcome to SpriteRotator app")

        self.img_edit = ImageEditor()

        self.mouse_var = StringVar(value="(0,0)")
        self.image_path = StringVar()
        self.dimensions_var = StringVar()
        self.preview_scale_var = IntVar(value=4)
        self.load_scale_var = IntVar(value=1)

        self.mouse_pos = [0, 0]
        self.gui.bind("<Button 3>", self.get_mouse_click_pos)

        self.dimensions_label_info = None
        self.dimensions_label = None
        self.preview_scale_box = None
        self.load_scale_label = None
        self.preview_scale_label = None
        self.load_scale_box = None
        self.preview_canvas = None
        self.preview_image = None
        self.image_on_canvas = None
        self.preview_canvas_mouse_indicator = None
        self.info_label = None
        self.path_label = None
        self.click_pos_label = None
        self.select_button = None
        self.rotate_button = None
        self.image_data = None
        self.image_labels = []
        self.text_labels = []

        self.create_ui_elements()
        self.gui.mainloop()

    def create_ui_elements(self):
        self.dimensions_label_info = Label(self.gui, text="Dimensions:")
        self.dimensions_label = Label(self.gui, textvariable=self.dimensions_var)

        self.preview_scale_label = Label(self.gui, text="Preview scale:")
        self.preview_scale_box = ttk.Combobox(self.gui, textvariable=self.preview_scale_var, values=[1, 2, 4, 8])

        self.load_scale_label = Label(self.gui, text="Load pre-scale:")
        self.load_scale_box = ttk.Combobox(self.gui, textvariable=self.load_scale_var, values=[1, 2, 4])

        self.preview_image = PhotoImage(file=r'preview.png')
        self.preview_canvas = Canvas(self.gui, width=20, height=40)
        self.image_on_canvas = self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        self.info_label = Label(self.gui, text="Path:")
        self.path_label = Label(self.gui, textvariable=self.image_path, background='#FFFFFF')
        self.select_button = Button(self.gui, text="Select image", command=self.select_image)

        self.click_pos_label = Label(self.gui, textvariable=self.mouse_var, background='#FFFFFF')
        self.rotate_button = Button(self.gui, text="Rotate!", command=self.show_rotated_images)

        self.organize_ui()

    def organize_ui(self):
        self.dimensions_var.set("Load image first, please!")
        self.image_path.set("Load image first, please!")

        self.info_label.grid(column=0, row=0)
        self.path_label.grid(column=1, row=0)
        self.select_button.grid(column=0, row=1)
        self.preview_canvas.grid(column=1, row=1)

        self.click_pos_label.grid(column=0, row=2)
        self.rotate_button.grid(column=1, row=2)

        self.dimensions_label_info.grid(column=0, row=3)
        self.dimensions_label.grid(column=1, row=3)

        self.preview_scale_label.grid(column=0, row=4)
        self.preview_scale_box.grid(column=1, row=4)
        self.preview_scale_box.bind('<<ComboboxSelected>>', self.refresh_preview_img)

        self.load_scale_label.grid(column=0, row=5)
        self.load_scale_box.grid(column=1, row=5)

    def select_image(self):
        path = tkinter.filedialog.askopenfilename()
        self.image_path.set("..." + path[-16:])
        self.img_edit.input_path = path
        self.image_data = self.img_edit.load_image(path)
        if self.load_scale_var.get() != 1:
            self.image_data = self.img_edit.resize(self.image_data, self.load_scale_var.get(), self.img_edit.scale_default_method)
        self.refresh_preview_img()

    def refresh_preview_img(self, *args):
        if self.image_data is not None:
            if self.preview_scale_var.get() != 1:
                new_image = self.img_edit.resize(self.image_data, self.preview_scale_var.get(), self.img_edit.scale_default_method)
                new_image = convert_image_to_tk(new_image)
            else:
                new_image = convert_image_to_tk(self.image_data)
            self.preview_image = new_image  # GC prevention!
            self.preview_canvas.itemconfigure(self.image_on_canvas, image=new_image)
            self.preview_canvas.config(width=new_image.width(), height=new_image.height())
            dimension_string = str(len(self.image_data[0])) + "x" + str(len(self.image_data)) + \
                "(Preview:" + str(new_image.width()) + "x" + str(new_image.height()) + ")"
            self.dimensions_var.set(dimension_string)

    def create_empty_labels(self):
        if not self.image_labels:
            for i in range(80):
                label = Label(self.gui, text="img")
                text = Label(self.gui, text="txt")
                label.grid(column=i - int(i / 10) * 10 + 2, row=int(i / 10) * 2 + 1)
                text.grid(column=i - int(i / 10) * 10 + 2, row=int(i / 10) * 2 + 2)
                self.image_labels.append(label)
                self.text_labels.append(text)

    def show_rotated_images(self):
        if self.image_data is not None:
            self.create_empty_labels()
            mouse_scaled = [0, 0]
            mouse_scaled[0] = self.mouse_pos[0] // self.preview_scale_var.get()
            mouse_scaled[1] = self.mouse_pos[1] // self.preview_scale_var.get()
            rotated_lists = self.img_edit.pixel_friendly_rotates(self.image_data, selected_px=mouse_scaled)
            cv2_list = rotated_lists[0]
            tk_list = rotated_lists[1]
            txt_list = rotated_lists[2]
            grip_list = rotated_lists[3]
            for i in range(len(cv2_list)):
                self.image_labels[i].configure(image=tk_list[i])
                self.image_labels[i].image = tk_list[i]
                self.text_labels[i].configure(text=txt_list[i])
                save_img_to_file(txt_list[i][:2], cv2_list[i])
            for i in range(len(cv2_list)-40):
                self.image_labels[i+40].configure(image=tk_list[i+40])
                self.image_labels[i+40].image = tk_list[i+40]
                self.text_labels[i+40].configure(text=txt_list[i+40])
                save_img_to_file(txt_list[i+40][:2], cv2_list[i+40])

            with open("output/grip_list.txt", "w") as f:
                for grip in grip_list:
                    f.write(str(grip) + "\n")
            f.close()

    def get_mouse_click_pos(self, event_origin):
        self.mouse_pos[0] = int(event_origin.x)
        self.mouse_pos[1] = int(event_origin.y)
        scale = self.preview_scale_var.get()
        if self.preview_canvas_mouse_indicator is not None:
            self.preview_canvas.delete(self.preview_canvas_mouse_indicator)
        mouse_scaled = [0, 0]
        mouse_scaled[0] = self.mouse_pos[0] // scale
        mouse_scaled[1] = self.mouse_pos[1] // scale
        self.preview_canvas_mouse_indicator = self.preview_canvas.create_rectangle(
            (mouse_scaled[0] * scale,
             mouse_scaled[1] * scale,
             mouse_scaled[0] * scale + scale,
             mouse_scaled[1] * scale + scale),
            fill='white')
        self.mouse_var.set("Pointer:" + str(mouse_scaled))


app = App()

"""# 26.57

rotated = pixel_rotater.rotate_image(preview_image, 63.43, 16)
cv2.imshow('original Image', img)
cv2.imshow('bulky Image', bulky)
cv2.imshow('Rotated Image', rotated)
cv2.imshow('rotated_shrunk Image', rotated_shrunk)
cv2.imwrite('output/123.png', rotated)
gui.mainloop()
cv2.waitKey(0)
cv2.destroyAllWindows()"""
