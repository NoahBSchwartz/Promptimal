import re
import time
import openai
import requests
import pandas as pd
import csv
import threading
import requests
import openai
import time

openai.api_key = "INSERT KEY HERE"
MAX_RETRIES = 5
RETRY_DELAY = 1
GPT_MODEL = "gpt-3.5-turbo"
MAX_RESPONSE_LENGTH = 125
x = 0

def worker(response_container, question, system, **settings):
    try:
        response = openai.ChatCompletion.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question}
            ],
            **settings
        )
        response_container.append(response['choices'][0]['message']['content'])
    except Exception as e:
        response_container.append(e)

def api_call(question, system, **settings):
    global x

    for attempt in range(MAX_RETRIES):
        response_container = []
        api_thread = threading.Thread(target=worker, args=(response_container, question, system), kwargs=settings)
        api_thread.start()

        api_thread.join(timeout=20)  # Wait for up to 20 seconds

        if api_thread.is_alive():
            print("API call timed out")
            return False

        if response_container and isinstance(response_container[0], str):  # Check if it's a successful response
            print("all good", x)
            x = x + 1
            return response_container[0]
        elif isinstance(response_container[0], requests.Timeout):
            print(f"Request timed out. Retry {attempt + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
        else:
            print(f"An error occurred: {response_container[0]}. Retry {attempt + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_DELAY)

    raise Exception("Failed after max retries")

x = 0  # Just for the sake of this example, you should have this defined somewhere

def get_word_count_estimate(bad_prompt):
    count_settings = {
        "model": GPT_MODEL,
        "temperature": 1,
        "max_tokens": 10,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }
    estimation_prompt = "Give an estimate for the number of words needed to answer the prompt completely, accurately, and specifically. Try to keep the range between 1 and 130 words. Output only a single number (e.g. '4', '123', '24')"
    answer = api_call("PROMPT: " + bad_prompt, estimation_prompt, **count_settings)
    num_str = ''.join([char for char in answer if char.isdigit()])
    actual_length = int(num_str) if num_str else MAX_RESPONSE_LENGTH
    return actual_length

def extract_prompts(question):
    """Extract the 'bad' and 'good' prompts from a given question."""
    bad_match = re.search(r'<s>\[INST\](.*?)\[/INST\]', question, re.DOTALL)
    bad_prompt = bad_match.group(1).strip() if bad_match else ""
    good_match = re.search(r'\[/INST\](.*?)</s>', question, re.DOTALL)
    good_prompt = good_match.group(1).strip() if good_match else ""
    return bad_prompt, good_prompt

def inital_openended_generator():
    with open('Final_RLHF_Training_Data.csv', 'r') as prompt_file, open('RLHF_MMLU_Training.csv', 'w') as response_file:
        prompt_reader = csv.reader(prompt_file)
        response_writer = csv.writer(response_file)
        response_writer.writerow(['Prompt', 'Length Prediction', 'Answer'])
        for row in prompt_reader:
            bad_prompt, good_prompt = extract_prompts(row[0])
            actual_length = get_word_count_estimate(bad_prompt)
            print(f"Length: {actual_length}")
            print(f"Question: {bad_prompt}")
            settings = {
                "model": GPT_MODEL,
                "temperature": 0,
                "max_tokens": min(int(actual_length * 4), MAX_RESPONSE_LENGTH),
                "top_p": 1,
                "n": 1,
                "stream": False,
                "presence_penalty": 1,
                "frequency_penalty": 1
            }
            answer = api_call(good_prompt, f"Answer the prompt in {min(actual_length, MAX_RESPONSE_LENGTH)} words or less.", **settings)
            if answer and answer != "False":
                print(f"Answer: {answer}")
                response_writer.writerow([good_prompt, actual_length, answer])

def secondary_openended_generator():
    df = pd.read_csv('Transformed_RLHF_Training_Data.csv')
    for index, row in df.iterrows():
        bad_prompt_1 = row[0]
        good_prompt_1 = row[1]
        length_1 = row[2]
        answer_1 = row[3]
        score_1 = row[4]
        try:
            length = int(length_1)
        except:
            length = 100
        try:
            score = float(score_1)
        except:
            score = 5.00
        score1 = (score + 2.9)*0.84
        score1 = int(score1)
        settings = {
            "model": GPT_MODEL,
            "temperature": 0.7,
            "max_tokens": length * 4,
            "top_p": 0.9,
            "n": 1, 
            "stream": False,
            "presence_penalty": 1.2,
            "frequency_penalty": 1.2
        }
        good_prompt_2 = api_call(f"Here is the first attempt at a rewrite of the prompt: '''{good_prompt_1}'''. However, it resulted in a score of only {score1}/10 because the chatbot gave the answer: '''{' '.join(str(answer_1).split()[:50])}...''' Can you rewrite the prompt to be better? Output ONLY your final unformatted prompt.", f"Act as a prompt engineer, taking into account all user-provided information, to rewrite the prompt to be as efficient, effective, and all-encompassing as possible when inputted into a chatbot: {bad_prompt_1}. Output ONLY your final unformatted prompt.", **settings)
        print("Good Prompt 2: ", good_prompt_2)
        if good_prompt_2 and good_prompt_2 != "False":
            settings = {
                "model": GPT_MODEL,
                "temperature": 0,
                "max_tokens": length_1 * 4,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "presence_penalty": 1,
                "frequency_penalty": 1
            }
            answer_2 = api_call(good_prompt_2, f"Answer the prompt in {length_1} words or less.", **settings)
            if answer_2 and answer_2 != "False":
                print(f"Answer: {answer_2}")
                out_df = pd.DataFrame([{'Bad Prompt': bad_prompt_1, 'Good Prompt 1': good_prompt_1, 'Length 1': length_1, 'Answer 1': answer_1, 'Score 1': score_1, 'Good Prompt 2': good_prompt_2, 'Answer 2': answer_2, 'Score 2': None}])
                header = False if index > 0 else True
                out_df.to_csv('RLHF_Open_Training(3).csv', mode='a', header=header, index=False)

def initial_multiplechoice_tester():
    df = pd.read_csv('MMLU_dataset.csv')

    settings = {
        "model": GPT_MODEL,
        "temperature": 0,
        "max_tokens": 1,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "presence_penalty": 1,
        "frequency_penalty": 1
    }

    for index, row in df.iterrows():
        bad_prompt = row[1]
        a = row[2]
        b = row[3]
        c = row[4]
        d = row[5]
        target = row[6]

        answer = api_call(f"{bad_prompt} Your choices are A: {a}, B: {b}, C: {c}, or D: {d}", 
                          f"Output a single token as your answer, either: A, B, C, or D", 
                          **settings)

        if answer and answer != "False":
            print(f"Output a single token as your answer, either: A, B, C, or D")
            print(f"{bad_prompt} Your choices are A: {a}, B: {b}, C: {c}, or D: {d}") 
            data = [{'Bad Prompt': bad_prompt, "A": a, "B": b, "C": c, "D": d, 'Answer 1': answer, 'Target': target}]
            out_df = pd.DataFrame(data)
            
            # Open the CSV file in append mode and write the result
            with open('RLHF_MMLU_Training.csv', 'a') as f:
                out_df.to_csv(f, header=not f.tell(), index=False)

def initial_multiplechoice_generator():
    df = pd.read_csv('RLHF_MMLU_Training(2000).csv')

    for index, row in df.iterrows():
        bad_prompt = row[0]
        a = row[1]
        b = row[2]
        c = row[3]
        d = row[4]
        settings = {
            "model": GPT_MODEL,
            "temperature": 0,
            "max_tokens": min(len(str(bad_prompt)) * 4, 200),
            "top_p": 1,
            "n": 1,
            "stream": False,
            "presence_penalty": 1,
            "frequency_penalty": 1
        }
        bad_answer = row[5]
        target = row[6]
        bad_answerq = ""
        targetq = ""
        if (bad_answer == "a"):
            bad_answerq = a
        if (target == "a"):
            targetq = a
        if (bad_answer == "b"):
            bad_answerq = b
        if (target == "b"):
            targetq = b
        if (bad_answer == "c"):
            bad_answerq = c
        if (target == "c"):
            targetq = c
        if (bad_answer == "d"):
            bad_answerq = d
        if (target == "d"):
            targetq = d
        good_prompt_1 = api_call(f"{bad_prompt}", 
                          f"Your goal is to act as a prompt engineer in order to rewrite the prompt given to you by the user. Try to use any techniques that you think will illicit a better response from a chatbot, outputting only the rewritten unformatted prompt. For context, the correct answer to the user's prompt is {targetq} but usually the chatbot answers with {bad_answerq}.", 
                          **settings)
        if good_prompt_1 and good_prompt_1 != "False":
            settings = {
                "model": GPT_MODEL,
                "temperature": 0,
                "max_tokens": 1,
                "top_p": 1,
                "n": 1,
                "stream": False,
                "presence_penalty": 1,
                "frequency_penalty": 1
            }
            answer_1 = api_call(f"{good_prompt_1} Your choices are A: {a}, B: {b}, C: {c}, or D: {d}", 
                                f"Output a single token as your answer, either: A, B, C, or D", 
                                **settings)
            if answer_1 and answer_1 != "False":
                if (answer_1 == target):
                    good_prompt_2 = None
                    answer_2 = None
                    good_prompt_3 = None
                    answer_3 = None
                else:
                    settings = {
                        "model": GPT_MODEL,
                        "temperature": 0.7,
                        "max_tokens": min(len(str(bad_prompt)) * 4, 200),
                        "top_p": 0.9,
                        "n": 1, 
                        "stream": False,
                        "presence_penalty": 1.2,
                        "frequency_penalty": 1.2
                    }
                    answer_1q = ""
                    if (answer_1 == "a"):
                        answer_1q = a
                    if (answer_1 == "b"):
                        answer_1q = b
                    if (answer_1 == "c"):
                        answer_1q = c 
                    if (answer_1 == "d"):
                        answer_1q = d
                    good_prompt_2 = api_call(f"Here is the first attempt at a rewrite of the prompt: '''{good_prompt_1}'''. However, it was marked incorrect because the chatbot gave the answer: '{answer_1q}' instead of: '{targetq}'  Can you rewrite the prompt to be better? Output ONLY your final unformatted prompt.", f"Act as a prompt engineer, taking into account all user-provided information, to rewrite the prompt to be as efficient, effective, and all-encompassing as possible when inputted into a chatbot: {bad_prompt}. Output ONLY your final unformatted prompt.", **settings)
                    settings = {
                        "model": GPT_MODEL,
                        "temperature": 0,
                        "max_tokens": 1,
                        "top_p": 1,
                        "n": 1,
                        "stream": False,
                        "presence_penalty": 1,
                        "frequency_penalty": 1
                    }
                    answer_2 = api_call(f"{good_prompt_2} Your choices are A: {a}, B: {b}, C: {c}, or D: {d}", 
                                        f"Output a single token as your answer, either: A, B, C, or D", 
                                        **settings)

                data = [{'Bad Prompt': bad_prompt, "A": a, "B": b, "C": c, "D": d, 'Bad Answer': bad_answer, 'Target': target, 'Prompt 1': good_prompt_1, "Answer 1": answer_1, 'Prompt 2': good_prompt_2, "Answer 2": answer_2, 'Prompt 3': None, "Answer 3": None}]
                out_df = pd.DataFrame(data)
                with open('RLHF_MMLU_Training(11).csv', 'a') as f:
                    out_df.to_csv(f, header=not f.tell(), index=False)

if __name__ == '__main__':     
    inital_openended_generator()
    secondary_openended_generator()
    initial_multiplechoice_tester()   
    initial_multiplechoice_generator()