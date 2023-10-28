from transformers import AutoTokenizer
import transformers
import torch

model = "NoahBSchwartz/llama-2-7b-LLM-Link8"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

prompt = """What was the aim of the Gravity Probe B (GP-B) mission?"""
sequences = pipeline(
    f"<s>[INST] {prompt} [/INST] What",
    do_sample=True,  # (True/False) - False leads to greedy decoding, True enables stochastic sampling
    top_k=10,  # (0 to vocab size) - A lower value (e.g., 0) means no restriction, higher value narrows down the sampling pool
    top_p=0.9,  # (0.0 to 1.0) - Lower value (e.g., 0.5) narrows down the sampling pool, 1.0 considers all tokens
    temperature=1.9,  # (>0 to infinity) - Lower value (e.g., 0.7) makes output more focused and deterministic, higher values (e.g., 2.0) make it more random
    max_length=100,  # (any positive integer) - Higher values allow for longer outputs, lower values restrict the output length
    min_length=2,  # (any positive integer, typically <= max_length) - Higher values ensure longer outputs, lower values allow for shorter outputs
    num_return_sequences=1,  # (any positive integer) - Higher values return more sequences, lower values return fewer
    no_repeat_ngram_size=0,  # (0 to any positive integer) - Higher values prevent repetition of n-grams, lower values allow for more repetition
    early_stopping=False,  # (True/False) - True stops generation once eos_token is reached, False allows generation past eos_token
    eos_token_id=tokenizer.eos_token_id,  # Depends on the tokenizer; generally, it is set to the appropriate ID for the end-of-sequence token
    pad_token_id=tokenizer.pad_token_id,  # Depends on the tokenizer; generally, it is set to the appropriate ID for the padding token
    repetition_penalty=1.0,  # (>= 1.0) - Values > 1.0 discourage repetition, values < 1.0 encourage repetition (though it's unusual to use values < 1.0)
    length_penalty=2,  # (>= 0.0) - Higher values (> 1.0) encourage longer sequences, values < 1.0 encourage shorter sequences
)
for seq in sequences:
    print(f"Result: {seq['generated_text']}")
