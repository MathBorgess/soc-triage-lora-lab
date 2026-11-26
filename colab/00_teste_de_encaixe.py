"""Teste de encaixe do Guardião numa GPU do Colab.

Mede se o Gemma 4 E4B cabe na GPU durante alguns passos de RL com DAPO, em quatro montagens:

- ``bf16-vllm``: treino em 16 bits e geração com vLLM na mesma GPU (modo colocate);
- ``4bit-vllm``: treino com a base em 4 bits (NF4) e geração com vLLM;
- ``bf16-hf``: treino em 16 bits e geração pelo próprio transformers, sem vLLM;
- ``4bit-hf``: base em 4 bits e geração pelo transformers, sem vLLM. É a montagem da T4.

``--precisao fp16`` serve às GPUs sem BF16, como a T4. Antes do treino, o script gera uma
resposta gulosa para conferir se a precisão escolhida não estraga a saída do modelo.

Não há ferramentas nem recompensa real: a recompensa só vale 1 quando a resposta é JSON válido.
O objetivo é medir memória, tempo e tokens, não aprender. Rode cada montagem num processo
próprio, para a memória da GPU voltar a zero entre elas. Ver ``colab/README.md``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import subprocess
import threading
import time
import traceback
from importlib import metadata
from pathlib import Path

MODELO = "google/gemma-4-E4B-it"
REVISAO = "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"
SUFIXOS_LORA = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
FORA_DO_LORA = ("vision", "audio", "embed")
PACOTES = ("torch", "transformers", "trl", "peft", "vllm", "accelerate", "datasets", "bitsandbytes")

# O vLLM em modo colocate usa o backend distribuído mesmo com um só processo.
for chave, valor in {
    "RANK": "0",
    "LOCAL_RANK": "0",
    "WORLD_SIZE": "1",
    "MASTER_ADDR": "localhost",
    "MASTER_PORT": "12355",
}.items():
    os.environ.setdefault(chave, valor)


class AmostradorDeMemoria(threading.Thread):
    """Lê a memória usada da GPU no nvidia-smi a cada meio segundo e guarda o pico."""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.pico_mib = 0
        self.total_mib = 0
        self._parar = threading.Event()

    def run(self) -> None:
        while not self._parar.is_set():
            try:
                saida = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=memory.used,memory.total",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=True,
                ).stdout.splitlines()[0]
                usada, total = (int(x) for x in saida.split(","))
                self.pico_mib = max(self.pico_mib, usada)
                self.total_mib = total
            except (subprocess.SubprocessError, ValueError, IndexError):
                pass
            self._parar.wait(0.5)

    def parar(self) -> None:
        self._parar.set()


def versoes() -> dict[str, str | None]:
    resultado: dict[str, str | None] = {"python": platform.python_version()}
    for pacote in PACOTES:
        try:
            resultado[pacote] = metadata.version(pacote)
        except metadata.PackageNotFoundError:
            resultado[pacote] = None
    return resultado


def recompensa_json(completions, **_kwargs) -> list[float]:
    """Vale 1 quando a resposta inteira é um objeto JSON; senão, 0."""
    notas = []
    for completion in completions:
        texto = completion[-1]["content"] if isinstance(completion, list) else completion
        try:
            notas.append(1.0 if isinstance(json.loads(texto.strip()), dict) else 0.0)
        except (json.JSONDecodeError, AttributeError):
            notas.append(0.0)
    return notas


def recompensa_variada(completions, **_kwargs) -> list[float]:
    """JSON válido vale mais quanto mais perto de 180 caracteres. Força variância no grupo."""
    notas = []
    for completion, valido in zip(completions, recompensa_json(completions), strict=True):
        texto = completion[-1]["content"] if isinstance(completion, list) else completion
        notas.append(valido * (1.0 - min(1.0, abs(len(texto) - 180) / 180)))
    return notas


def alvos_lora(modelo) -> list[str]:
    """Projeções de atenção e MLP do modelo de texto, sem torres de visão e áudio."""
    import torch

    nomes = []
    for nome, modulo in modelo.named_modules():
        if not nome.endswith(SUFIXOS_LORA):
            continue
        if any(parte in nome for parte in FORA_DO_LORA):
            continue
        if isinstance(modulo, torch.nn.Linear) or "Linear" in type(modulo).__name__:
            nomes.append(nome)
    return nomes


def contar_dtypes(modelo, so_treinaveis: bool) -> dict[str, int]:
    """Conta parâmetros por tipo, para achar pesos em BF16 numa GPU sem BF16."""
    contagem: dict[str, int] = {}
    for parametro in modelo.parameters():
        if so_treinaveis and not parametro.requires_grad:
            continue
        chave = str(parametro.dtype).replace("torch.", "")
        contagem[chave] = contagem.get(chave, 0) + parametro.numel()
    return contagem


def gerar_amostra(modelo, tokenizer, prompt) -> dict:
    """Gera uma resposta gulosa para conferir a saída antes do treino."""
    import torch

    entrada = tokenizer.apply_chat_template(
        prompt,
        add_generation_prompt=True,
        enable_thinking=False,
        return_tensors="pt",
        return_dict=True,
    ).to(modelo.device)
    inicio = time.monotonic()
    with torch.no_grad():
        saida = modelo.generate(**entrada, max_new_tokens=256, do_sample=False)
    segundos = time.monotonic() - inicio
    novos = saida[0, entrada["input_ids"].shape[1] :]
    texto = tokenizer.decode(novos, skip_special_tokens=True)
    return {
        "texto": texto[:800],
        "json_valido": recompensa_json([texto])[0] == 1.0,
        "tokens": int(novos.shape[0]),
        "tokens_por_segundo": round(int(novos.shape[0]) / segundos, 2),
    }


def executar(args: argparse.Namespace, relatorio: dict) -> None:
    import torch
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import GRPOConfig, GRPOTrainer

    relatorio.update({"modelo": MODELO, "revisao": REVISAO})
    relatorio["gpu"] = torch.cuda.get_device_name(0)

    linhas = [json.loads(x) for x in Path(args.dados).read_text().splitlines() if x.strip()]
    dados = Dataset.from_list([{"prompt": linha["prompt"]} for linha in linhas])
    tokenizer = AutoTokenizer.from_pretrained(MODELO, revision=REVISAO)
    tamanhos = [
        len(
            tokenizer.apply_chat_template(
                linha["prompt"],
                tokenize=True,
                add_generation_prompt=True,
                enable_thinking=False,
                return_dict=True,
            )["input_ids"]
        )
        for linha in linhas
    ]
    relatorio["tokens_do_prompt"] = {"max": max(tamanhos), "medio": sum(tamanhos) / len(tamanhos)}

    dtype = torch.bfloat16 if args.precisao == "bf16" else torch.float16
    relatorio["precisao"] = args.precisao
    relatorio["gpu_suporta_bf16"] = torch.cuda.is_bf16_supported(including_emulation=False)
    kwargs: dict = {"revision": REVISAO, "dtype": dtype}
    if args.modo.startswith("4bit"):
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        )
    inicio = time.monotonic()
    modelo = AutoModelForCausalLM.from_pretrained(MODELO, **kwargs)
    relatorio["classe_do_modelo"] = type(modelo).__name__
    relatorio["parametros_bilhoes"] = round(sum(p.numel() for p in modelo.parameters()) / 1e9, 3)
    relatorio["segundos_para_carregar"] = round(time.monotonic() - inicio, 1)
    relatorio["memoria_apos_carregar_gib"] = round(torch.cuda.memory_allocated() / 2**30, 2)
    relatorio["amostra"] = gerar_amostra(modelo, tokenizer, linhas[0]["prompt"])

    alvos = alvos_lora(modelo)
    relatorio["modulos_lora"] = len(alvos)
    peft_config = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, target_modules=alvos, task_type="CAUSAL_LM"
    )

    usa_vllm = args.modo.endswith("vllm")
    config = GRPOConfig(
        output_dir="/content/encaixe-saida",
        max_steps=args.passos,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4 * args.prompts_por_passo,
        num_generations=8,
        max_completion_length=args.max_completion,
        learning_rate=1e-5,
        lr_scheduler_type="constant",
        warmup_steps=0,
        bf16=args.precisao == "bf16",
        fp16=args.precisao == "fp16",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        logging_steps=1,
        report_to="none",
        save_strategy="no",
        seed=42,
        loss_type="dapo",
        epsilon_high=0.28,
        mask_truncated_completions=True,
        beta=0.0,
        chat_template_kwargs={"enable_thinking": False},
        use_vllm=usa_vllm,
        vllm_mode="colocate",
        vllm_gpu_memory_utilization=args.vllm_mem,
        vllm_enable_sleep_mode=True,
        vllm_max_model_length=max(tamanhos) + args.max_completion,
    )
    trainer = GRPOTrainer(
        model=modelo,
        reward_funcs=recompensa_json if args.recompensa == "json" else recompensa_variada,
        args=config,
        train_dataset=dados,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    inicio = time.monotonic()
    # O GradScaler do FP16 exige pesos treináveis em FP32, como no QLoRA.
    relatorio["dtype_treinaveis_antes"] = contar_dtypes(trainer.model, so_treinaveis=True)
    for parametro in trainer.model.parameters():
        if parametro.requires_grad and parametro.dtype != torch.float32:
            parametro.data = parametro.data.float()
    relatorio["dtype_treinaveis_depois"] = contar_dtypes(trainer.model, so_treinaveis=True)
    relatorio["dtype_todos"] = contar_dtypes(trainer.model, so_treinaveis=False)
    trainer.train()
    relatorio["segundos_de_treino"] = round(time.monotonic() - inicio, 1)
    relatorio["passos"] = args.passos
    relatorio["prompts_por_passo"] = args.prompts_por_passo
    relatorio["recompensa"] = args.recompensa
    relatorio["log"] = trainer.state.log_history
    relatorio["nan_no_log"] = any(
        isinstance(v, float) and math.isnan(v)
        for linha in trainer.state.log_history
        for v in linha.values()
    )
    relatorio["pico_torch_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--modo", choices=("bf16-vllm", "4bit-vllm", "bf16-hf", "4bit-hf"), required=True
    )
    parser.add_argument("--precisao", choices=("bf16", "fp16"), default="bf16")
    parser.add_argument("--dados", required=True, help="JSONL com um campo prompt por linha")
    parser.add_argument("--saida", required=True, help="Arquivo JSON do relatório")
    parser.add_argument("--passos", type=int, default=3)
    parser.add_argument("--max-completion", type=int, default=1024)
    parser.add_argument("--vllm-mem", type=float, default=0.3)
    parser.add_argument("--recompensa", choices=("json", "variada"), default="variada")
    parser.add_argument("--prompts-por-passo", type=int, default=1)
    args = parser.parse_args()

    amostrador = AmostradorDeMemoria()
    amostrador.start()
    relatorio: dict = {"modo": args.modo, "versoes": versoes()}
    try:
        executar(args, relatorio)
        relatorio["status"] = "ok"
    except Exception as erro:  # noqa: BLE001 - o relatório precisa registrar qualquer falha
        texto = f"{type(erro).__name__}: {erro}"
        relatorio["status"] = "sem_memoria" if "out of memory" in texto.lower() else "erro"
        relatorio["erro"] = texto[:2000]
        relatorio["traceback"] = traceback.format_exc()[-4000:]
    finally:
        amostrador.parar()
        relatorio["pico_nvidia_smi_mib"] = amostrador.pico_mib
        relatorio["memoria_total_mib"] = amostrador.total_mib
        Path(args.saida).write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2, default=str)
        )
        print(
            json.dumps(
                {k: v for k, v in relatorio.items() if k not in ("log", "traceback")},
                ensure_ascii=False,
                default=str,
            )
        )


if __name__ == "__main__":
    main()
