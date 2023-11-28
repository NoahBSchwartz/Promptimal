# Promptimal

## 🗒️ Introduction
  Achieved human-level prompt writing via self-play (automated trial and error). 
  First to combine the OPRO and Promptbreeder papers with fine-tuning, diverging from reliance on a base model.
## 🔍 Overview

## 🛠 Process

  1. First, several datasets (MMLU, Alpaca, and HumanEval) were used to test the gpt-3.5-turbo model. 
  2. The hardest questions (~2500) were fed into the model again. It was asked to generate 2 improved prompts for each.
  3. For variety, 1000 responses were tested based on how well they produced open-ended answers from the model, scored with reward-deberta. The rest were scored simply on how accurately they produced multiple-choice answers.
  4. The set of scores, prompts, and answers were all fed back into gpt-3.5-turbo for 3 more rounds of incremental improvements.
  5. This final set of prompts was used to fine-tune a large language model (Llama2 7b) in Pytorch.


<img width="806" alt="Screenshot 2023-11-26 at 6 53 37 PM" src="https://github.com/NoahBSchwartz/Promptimal/assets/44248582/02414aa4-4e85-4ff5-9419-f21711e78478">



## 🎉 Result
The process achieved human-level prompt writing in greater than 90% of the generations. The project showed that it was possible to use a fine-tuned model with as few as 7 billion parameters. While the traditional OPRO and Prompt Breeder methods rely on far larger models with far more generation steps, this improved method is more scalable and cost-effective. 
Here's an excerpt from the final testing of the tool.
<img width="1052" alt="Screenshot 2023-11-27 at 9 33 16 PM" src="https://github.com/NoahBSchwartz/Promptimal/assets/44248582/c2fe65c0-f9c4-4bcb-97ba-c25a7ba47098">


## How to Use

To run inference on the final model, use [this](https://colab.research.google.com/drive/1HaIEY3PV6FnfnBAJ78L1COHrou5VrXWi#scrollTo=6F_QcoT5WOXH) google colab notebook.
To train the model on modified data, use [this](https://colab.research.google.com/drive/1B0OvnZrb7vGcmhmKFYEaY08ZuWuGFfs8) one. 

