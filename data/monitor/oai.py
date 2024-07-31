#!/usr/bin/env python3


## supporting functions
import base64, textwrap, time, openai, os, io, json
from PIL import Image  # Pillow image library

def resize_image(image, max_dimension):
    width, height = image.size

    # Check if the image has a palette and convert it to true color mode
    if image.mode == "P":
        if "transparency" in image.info:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        timestamp = time.time()

    return image

def convert_to_png(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()

def process_image(path, max_size):
    with Image.open(path) as image:
        width, height = image.size
        mimetype = image.get_format_mimetype()
        if mimetype == "image/png" and width <= max_size and height <= max_size:
            with open(path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
                return (encoded_image, max(width, height))  # returns a tuple consistently
        else:
            resized_image = resize_image(image, max_size)
            png_image = convert_to_png(resized_image)
            return (base64.b64encode(png_image).decode('utf-8'),
                    max(width, height)  # same tuple metadata
                   )  

def create_image_content(image, maxdim, detail_threshold):
    detail = "low" if maxdim < detail_threshold else "high"
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": detail}
    }

def set_system_message(sysmsg):
    return [{
        "role": "system",
        "content": sysmsg
    }]
    
    

## user message with images function
def set_user_message(user_msg_str,
                     file_path_list=[],      # A list of file paths to images.
                     max_size_px=1024,       # Shrink images for lower expense
                     file_names_list=None,   # You can set original upload names to show AI
                     tiled=False,            # True is the API Reference method
                     detail_threshold=700):  # any images below this get 512px "low" mode

    if not isinstance(file_path_list, list):  # create empty list for weird input
        file_path_list = []

    if not file_path_list:  # no files, no tiles
        tiled = False

    if file_names_list and len(file_names_list) == len(file_path_list):
        file_names = file_names_list
    else:
        file_names = [os.path.basename(path) for path in file_path_list]

    base64_images = [process_image(path, max_size_px) for path in file_path_list]

    uploaded_images_text = ""
    if file_names:
        uploaded_images_text = "\n\n---\n\nUploaded images:\n" + '\n'.join(file_names)

    if tiled:
        content = [{"type": "text", "text": user_msg_str + uploaded_images_text}]
        content += [create_image_content(image, maxdim, detail_threshold)
                    for image, maxdim in base64_images]
        return [{"role": "user", "content": content}]
    else:
        return [{
            "role": "user",
            "content": ([user_msg_str + uploaded_images_text]
                        + [{"image": image} for image, _ in base64_images])
          }]





def oai(image_paths):

	print(f'oai({image_paths})')

	system_msg = """
	You are VisionPal, an AI assistant powered by GPT-4 with computer vision.
	AI knowledge cutoff: April 2023
	
	Built-in vision capabilities:
	- extract text from image
	- describe images
	- analyze image contents
	- logical problem-solving requiring machine vision
	""".strip()
	
	# The user message
	# 	Describe the quality.
	# 	Repeat back the file names sent.
	user_msg = """
	How many images were received?
	Describe the contents.
	Respond in JSON format.
	Include field named "image_contents".
	Include a field named "emergency", containing one of possible values:
	"fallen_person", "fire", "medical_emergency", "other", "none". Use "none" if the image seems to depict a situation that is not an actual emergency, use appropriate value otherwise.
	If "emergency" is not "none", include "explanation" field with a detailed explanation.
	
	""".strip()
	
	# user images file list, and max dimension limit
	max_size = 1024  # downsizes if any dimension above this
	
	#true_files = ["real file name 1.png", "real file name 2.jpg"]
	true_files = None  # you can give real names if using temp upload locations
	
	
	# Assemble the request parameters (all are dictionaries)
	system = set_system_message(system_msg)
	chat_hist = []  # list of more user/assistant items
	user = set_user_message(user_msg, image_paths, max_size, file_names_list=true_files)
	
	params = {  # dictionary format for ** unpacking
	  "model": "gpt-4o-mini", "temperature": 0.0, "user": "my_customer",
	  "max_tokens": 500, "top_p": 0.5, "stream": True,
	  "messages": system + chat_hist + user,
	  'response_format': { "type": "json_object" },
	
	}
	
	start = time.perf_counter()
	try:
		client = openai.Client(timeout=111)
		response = client.chat.completions.with_raw_response.create(**params)
		headers_dict = response.headers.items().mapping.copy()
		for key, value in headers_dict.items():  # set a variable for each header
			locals()[f'headers_{key.replace("-", "_")}'] = value
	except Exception as e:
		print(f"Error during API call: {e}")
		response = None
	
	if response is not None:
		try:
			reply = ""
			print(f"---\nSENT:\n{user[0]['content'][0]}\n---")
			for chunk_no, chunk in enumerate(response.parse()):
				if chunk.choices[0].delta.content:
					reply += chunk.choices[0].delta.content
					print(chunk.choices[0].delta.content, end="")
		except Exception as e:
			print(f"Error during receive/parsing: {e}")
	
	print(f"\n[elapsed: {time.perf_counter()-start:.2f} seconds]")
	
	try:
		j = json.loads(reply)
	except Exception as e:
		print(f"Error during JSON parsing: {e}")
		j = None
	
	return j




if __name__ == '__main__':
	#oai(["/home/koom/Downloads/young-man-fallen-ladder-lying-260nw-1889074375.webp"])
	oai(["/home/koom/upland.png"])	