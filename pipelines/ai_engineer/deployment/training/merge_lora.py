import torch
import gc
import time
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# CONFIGURATION
BASE_MODEL_ID = "Nanbeige/Nanbeige4.1-3B"
LORA_PATH = "./lora_adapter"
OUTPUT_DIR = "./nanbeige-merge-prod"

# Set the device globally
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create function to merge LoRA and save the merged model
def merge_and_save():
    print(f"Loading base model: {BASE_MODEL_ID} on {DEVICE}...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=torch.float16,
        device_map={"": DEVICE},
        trust_remote_code=True
    )

    print("📎 Attaching LoRA Adapter...")
    model = PeftModel.from_pretrained(base_model, LORA_PATH)

    model = model.to("cpu")  # Ensure model is on the correct device

    # Immedtiately clear the mac CPU cache after moving
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
        gc.collect()

    print("🔗 Merging LoRA weights into the base model...")
    start_time = time.time()
    model = model.merge_and_unload()
    print(f"✅ Merge and save completed in {time.time() - start_time:.2f} seconds.")

    print(f"Saving merged model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)

    # Save the tokenizer as well
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL_ID,
        trust_remote_code=True
    )
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("✅ Model and tokenizer saved successfully.")

    return model.to(DEVICE), tokenizer

# Create function to test the merged model
def run_test_inference(model, tokenizer):
    print("\n🔍 Running test inference on the merged model...")

    messages = [
        {"role": "system", "content": "You are a professional Business Analyst specializing in E-commerce and Deep Learning."},
        {"role": "user", "content": "What's business analyst strategy to increase sales and profit in e-commerce using LSTM?"},
        {"role": "user", "content": "What are the key factors affecting revenue growth?"}
    ]

    # Nanbeige uses a specific chat template format
    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )

    inputs = tokenizer(prompt,
                       add_special_token=False,
                       return_tensors='pt').to(model.device)
    
    # Generate with Nanbeige recommended settings
    output_ids = model.generate(
        **inputs,
        max_new_tokens=1024,
        temperature=0.6,
        eos_token_id=166101 # Nanbeige stop token
    )

    response = tokenizer.decode(output_ids[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
    print(f"\nAI Response:\n{'-'*20}\n{response}\n{'-'*20}")

# Usage
if __name__ == "__main__":
    # 1. Perform the merge
    merged_model, merged_tokenizer = merge_and_save()

    # 2. Test it immediately
    run_test_inference(merged_model, merged_tokenizer)

    # 3. Clean up memory
    del merged_model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    print("✅ Process completed. Merged model is ready for deployment.")