from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import TrainingArguments
from transformers import BitsAndBytesConfig
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from trl import SFTConfig, SFTTrainer
from datasets import Dataset
import argparse
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from experiments.llms.oyxoy_datasets import PromptHandlerSelector

def main(args):
    prompt_handler = PromptHandlerSelector(args.dataset).create(args.prompt, args.num_shots)
    chat_sets = prompt_handler.get_chats()

    dataset_train = Dataset.from_dict(chat_sets['train'])
    if 'dev' in chat_sets:
        dataset_dev = Dataset.from_dict(chat_sets['dev'])
    
    model_id = args.model

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    tokenizer.model_max_length = 8192

    def format_chat_template(row):
        row["chat"] = tokenizer.apply_chat_template(row["chat"], tokenize=False)
        return row

    dataset_train = dataset_train.map(
        format_chat_template,
        num_proc= os.cpu_count(),
    )
    if 'dev' in chat_sets:
        dataset_dev = dataset_dev.map(
            format_chat_template,
            num_proc= os.cpu_count(),
        )


    # For 8 bit quantization
    #quantization_config = BitsAndBytesConfig(load_in_8bit=True,
    #                                        llm_int8_threshold=200.0)

    ## For 4 bit quantization
    quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,)


    trained_model_id = f"{args.model.split('/')[-1]}-{args.dataset}"
    output_dir = f'{args.output_dir_path}/{trained_model_id}'

    # based on config
    training_args = TrainingArguments(
        fp16=False, # specify bf16=True instead when training on GPUs that support bf16 else fp16
        bf16=True,
        do_eval=True,
        evaluation_strategy="no" if 'dev' not in chat_sets else "steps",
        eval_steps=None if 'dev' not in chat_sets else 500,
        gradient_accumulation_steps=1,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        learning_rate=2.0e-05,
        log_level="info",
        logging_steps=5,
        logging_strategy="steps",
        lr_scheduler_type="cosine",
        max_steps=-1,
        num_train_epochs=1,
        output_dir=output_dir,
        overwrite_output_dir=True,
        per_device_eval_batch_size=1, # originally set to 8
        per_device_train_batch_size=1, # originally set to 8
        # push_to_hub=True,
        hub_model_id=trained_model_id,
        # hub_strategy="every_save",
        # report_to="tensorboard",
        report_to="none",  # for skipping wandb logging
        save_strategy="steps",
        save_steps=500,
        save_total_limit=None,
        seed=42,
    )

    # based on config
    peft_config = LoraConfig(
            r=64,
            lora_alpha=16,
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    model_kwargs = dict(
        torch_dtype="auto",
        use_cache=False, # set to False as we're going to use gradient checkpointing
        device_map='auto',
        quantization_config=quantization_config,
    )

    trainer = SFTTrainer(
            model=model_id,
            model_init_kwargs=model_kwargs,
            args=training_args,
            train_dataset=dataset_train,
            eval_dataset=None if 'dev' not in chat_sets else dataset_dev,
            dataset_text_field="chat",
            tokenizer=tokenizer,
            # packing=True,
            peft_config=peft_config,
            max_seq_length=tokenizer.model_max_length,
            #token = args.hf_token
        )

    # To clear out cache for unsuccessful run
    torch.cuda.empty_cache()

    train_result = trainer.train()
    trainer.save_model(output_dir+'/checkpoint-end')

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', default="meta-llama/Meta-Llama-3-8B-Instruct", help="pretrained model from HF that can be used for fine tuning")
    parser.add_argument('-out', '--output_dir_path', required=True, help='Directory path where output .csv files will be stored') 
    parser.add_argument('-prompt', '--prompt', required=True, help='Prompt method from the available in `experiments/llms/prompts.py`')
    parser.add_argument('-n_tokens', '--max_new_tokens', type=int, required=False, default=4, help='Maximum number of new tokens (following prompt) to generate')
    parser.add_argument('-n_shots', '--num_shots', type=int, required=False, default=None, help='Number of examples to use for the ICL')
    parser.add_argument('-ds', '--dataset', type=str, required=False, default=None, help='Dataset on which to run the experiment')
    # parser.add_argument('-token', '--hf_token', required=True, help='HuggingFace token') 

    args = parser.parse_args()
  
    assert (('few_shot' not in args.prompt) and (args.num_shots is None)) or (('few_shot' in args.prompt) and (args.num_shots is not None)), "You selected a few-shot prompt so you should provide an integer value for `-n_shots` "
    main(args)
