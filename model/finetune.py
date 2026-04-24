"""QLoRA fine-tuning on the Palestinian Basic Law Q&A dataset.

Requires a GPU with 8GB+ VRAM (T4 on Colab works). Example:

    python -m model.finetune \
        --base_model "Equall/Saul-7B-Instruct-v1" \
        --data "data/processed/training_qa.jsonl" \
        --output_dir "./legal-model-lora" \
        --epochs 3
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

INSTRUCTION_TEMPLATE = (
    "[INST] You are a legal aid assistant for Palestinian citizens. "
    "Answer based on the Palestinian Basic Law (2003, amended 2005).\n\n"
    "Question: {instruction}\n[/INST] {response}"
)


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", default="Equall/Saul-7B-Instruct-v1")
    parser.add_argument("--data", default="data/processed/training_qa.jsonl")
    parser.add_argument("--output_dir", default="./legal-model-lora")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--grad_accum", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--max_seq_length", type=int, default=1024)
    args = parser.parse_args()

    # Imports are gated so the module is importable on CPU-only dev boxes.
    import torch
    from datasets import Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, prepare_model_for_kbit_training
    from trl import SFTTrainer

    rows = _load_jsonl(Path(args.data))
    formatted = [{"text": INSTRUCTION_TEMPLATE.format(**row)} for row in rows]
    dataset = Dataset.from_list(formatted)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        logging_steps=10,
        save_strategy="epoch",
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        optim="paged_adamw_8bit",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        peft_config=lora_config,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        args=training_args,
    )
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"[finetune] saved adapter to {args.output_dir}")


if __name__ == "__main__":
    main()
