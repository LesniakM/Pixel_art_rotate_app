import math
from math import cos, sin, atan, sqrt, radians, acos, degrees, asin

import cv2
from PIL import Image
from PIL import ImageTk
import imutils
from tkinter import Tk, Label, StringVar, Button, ttk, IntVar, Canvas, PhotoImage
import tkinter.filedialog

from image_manager import ImageManager

output_dir_path = 'output'


def convert_image_to_tk(cv2_image):
    """
    Converts cv2 BGR/BGRA image to tk RGB/RGBA image.
        :param cv2_image: a cv2 format image
        :return: Image in tk format (ImageTk.PhotoImage)
    """
    if cv2_image.shape[2] == 4:
        blue, green, red, alpha = cv2.split(cv2_image)
        merged_img = cv2.merge((red, green, blue, alpha))
    else:
        blue, green, red = cv2.split(cv2_image)
        merged_img = cv2.merge((red, green, blue))
    image_array = Image.fromarray(merged_img)
    tk_image = ImageTk.PhotoImage(image=image_array)
    return tk_image


def save_img_to_file(name, img):
    """
    Saves image to png in output folder.
        :param name: filename
        :param img: Image in cv2 image format
        :return: Nothing
        :type name: str
    """
    cv2.imwrite('output/' + name + '.png', img)


class App:
    def __init__(self):
        self.gui = Tk(className='Python Examples - Window Size')
        self.gui.geometry("1000x800")
        self.gui.title("Welcome to SpriteRotator app")

        self.img_edit = ImageManager()

        self.mouse_var = StringVar(value="(0,0)")
        self.image_path = StringVar()
        self.dimensions_var = StringVar()
        self.preview_scale_var = IntVar(value=4)
        self.load_scale_var = IntVar(value=1)

        self.mouse_pos = [0, 0]
        self.gui.bind("<Button 3>", self.get_mouse_click_pos)

        self.combo_style = None
        self.preview_canvas_mouse_indicator = None
        self.image_data = None
        self.image_labels = []
        self.text_labels = []

        self.set_color_palettes()
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
        self.path_label = Label(self.gui, textvariable=self.image_path)
        self.select_button = Button(self.gui, text="Select image", command=self.select_image)

        self.click_pos_label = Label(self.gui, textvariable=self.mouse_var)
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

    def set_color_palettes(self):
        background_color = '#3C3F41'
        foreground_color = '#CCCCCC'
        active_background_color = '#DDDDDD'
        active_foreground_color = '#222222'

        self.gui.tk_setPalette(background=background_color,
                               foreground=foreground_color,
                               activeBackground=active_background_color,
                               activeForeground=active_foreground_color)

        self.combo_style = ttk.Style()
        self.combo_style.theme_use('default')
        self.combo_style.configure("TCombobox",
                                   fieldbackground=background_color,
                                   foreground=foreground_color,
                                   background=background_color,
                                   activeBackground=active_background_color)

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
