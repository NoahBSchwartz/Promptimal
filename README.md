# Promptimal

## 🗒️ Introduction
  Language models like ChatGPT give better or worse answers based on how users prompt them. This has led to an explosion in "prompt engineering": trying to find the best possible question to ask chatbots. But what if that too could be automated?
  
## 🔍 Overview
The OPRO and Prompt-Breeder papers provided a great starting point for using language models to optimize prompts. The issue is that each one of them uses GPT-4 and over 20 generations to get a single prompt right. To keep inference costs low, my solution was to generate the best set of 1000 prompts I could and then finetune a much smaller model with it.
  
## 🛠 Process

  1. First, several datasets (MMLU, Alpaca, and HumanEval) were used to test the gpt-3.5-turbo model in order to find the hardest questions. 
  2. These complex prompts (~2500) were fed into the model again. It was asked to generate 2 improved versions of each one.
  3. For variety, 1000 of the prompt improvements were tested based on how well they produced open-ended answers from the model, scored with reward-deberta. The rest were scored simply on how accurately they produced multiple-choice answers.
  4. The set of scores, prompts, and answers were all fed back into gpt-3.5-turbo for 3 more rounds of incremental improvements.
  5. This final set of prompts was used to fine-tune a large language model (Llama2 7b) in Pytorch.


<img width="806" alt="Screenshot 2023-11-26 at 6 53 37 PM" src="https://github.com/NoahBSchwartz/Promptimal/assets/44248582/02414aa4-4e85-4ff5-9419-f21711e78478">



## 🎉 Result
The process achieved human-level prompt writing in most cases (longer, more complex prompts still need improvement). The project showed that it was possible to use a fine-tuned model with as few as 7 billion parameters. While the traditional OPRO and Prompt Breeder methods rely on far larger models with far more generation steps, this improved method is more scalable and cost-effective. 

Here's an excerpt from the final testing of the tool:
<img width="1052" alt="Screenshot 2023-11-27 at 9 33 16 PM" src="https://github.com/NoahBSchwartz/Promptimal/assets/44248582/c2fe65c0-f9c4-4bcb-97ba-c25a7ba47098">


## How to Use

To run inference on the final model, use [this](https://colab.research.google.com/drive/1HaIEY3PV6FnfnBAJ78L1COHrou5VrXWi#scrollTo=6F_QcoT5WOXH) google colab notebook.
To train the model on modified data, use [this](https://colab.research.google.com/drive/1B0OvnZrb7vGcmhmKFYEaY08ZuWuGFfs8) one. 

