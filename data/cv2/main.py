import mlx.core as mx
import torch
from transformers import AutoProcessor
from mlx_vlm import VLMForCausalLM

def main():
    # Load the model and processor
    model_path = "HuggingFaceTB/SmolVLM-500M-Instruct"
    processor = AutoProcessor.from_pretrained(model_path)
    model = VLMForCausalLM.from_pretrained(model_path)

    # Prepare input
    image_url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    prompt = "Describe this image."

    try:
        # Process the image and text
        inputs = processor(
            text=prompt,
            images=image_url,
            return_tensors="pt"
        )

        # Generate the response
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            image_features=inputs["image_features"],
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7
        )

        # Decode and print the response
        response = processor.decode(outputs[0], skip_special_tokens=True)
        print(f"Model response: {response}")

    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()