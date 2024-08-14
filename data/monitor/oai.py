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
	try:
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
	except Exception as e:
		print(f"Error processing image: {e}")
		return None  

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
                     tiled=False,            # True is the API Reference method
                     detail_threshold=700):  # any images below this get 512px "low" mode

    if not file_path_list:  # no files, no tiles
        tiled = False

    base64_images = [process_image(path, max_size_px) for path in file_path_list]
    base64_images = [image for image in base64_images if image]  # remove None results

    uploaded_images_text = ""

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





def oai(image_paths, extra_prompt):

	print(f'oai({image_paths})')

	system_msg = """
	""".strip()
	
	# The user message
	# 	Describe the quality.
	# 	Repeat back the file names sent.
	user_msg = ("""
	Respond in JSON format:

	How many images were received?
	Describe the contents in field named "image_contents".
	Describe the contents in czech language in "image_contents_localized".	
	
	"emergency" is defined as a situation that poses an immediate threat to the life or health of a person or people, or property, and requires urgent intervention to prevent a worsening of the situation.
	Include a field named "emergency", containing one of possible values:
	"fallen_person", "fire", "medical_emergency", "other", "none". Use "none" if the image seems to depict a situation that is not an immediate emergency.
	
	An elderly person fallen on the floor, not moving or unable to get up, is an example of "fallen_person" emergency.
	An image of a person on fire is an example of "fire" emergency.
	An image of a person with a visible injury or life-threatening medical condition is an example of "medical_emergency".
	A child falling on the floor but getting back up unharmed is an example of "none".
	A candle burning in a room safely is an example of "none".
	An apparent accident or crime scene with no visible injuries or immediate threats is an example of "other".
	
	If "emergency" is not "none", include "explanation" field with a detailed explanation.
	
	Use field "help_needed" to indicate if the situation calls for immediate attention or intervention from an observer. "help_needed" is false if the people in the image are not in immediate danger or appear to be handling the situation themselves.
	
	If you had a robotic arm that could reach the location, what would you do to help solve or improve the situation? Answer in JSON format, field "action".

	""" + extra_prompt).strip()
	
	# user images file list, and max dimension limit
	max_size = 1024  # downsizes if any dimension above this
	
	#true_files = ["real file name 1.png", "real file name 2.jpg"]
	true_files = None  # you can give real names if using temp upload locations
	
	
	# Assemble the request parameters (all are dictionaries)
	system = set_system_message(system_msg)
	chat_hist = []  # list of more user/assistant items
	user = set_user_message(user_msg, image_paths, max_size)
	
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