import os
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths
from comfy.cli_args import args
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype

fundamental_classes = []
fundamental_node = node_wrapper(fundamental_classes)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
ext_path = os.path.dirname(os.path.realpath(__file__))
url = 'https://api.txt2any.com/v1/images'

def read_apikey():
    try:
        f = open(f"{ext_path}/txt2any.ini", "r")
        return f.read()
    except Exception:
        return ''

@fundamental_node
class SaveImageToT2A:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"images": ("IMAGE", ),
                     "filename_prefix": ("STRING", {"default": "txt2any"})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ()
    FUNCTION = "save_images_to_txt2any"

    OUTPUT_NODE = True

    CATEGORY = "image"
    custom_name = "Save image to txt2any"

    def save_images_to_txt2any(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        multiple_files = []
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            file_upload = ('files', (file, open(os.path.join(full_output_folder, file), 'rb'), 'image/png'))
            multiple_files.append(file_upload)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        headers = {
            'Authorization': f'Bearer {read_apikey()}'
            }
        r = requests.post(url, files=multiple_files, headers=headers, verify=False)
        return { "ui": { "images": results } }

WEB_DIRECTORY = "./js"
CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(fundamental_classes)
validate(fundamental_classes)
