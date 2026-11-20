"""Approved Azure gpt-5-mini settings revision; never a frozen execution identity."""
VERSION = 'azure-gpt5mini-v5-shared-minimal-cap2000'
# Historical OpenRouter default; Azure reads its cap from the shared YAML below.
MAX_COMPLETION_TOKENS = 700


def identity_settings(model_version=None):
    from app.evaluation.simple_config import load_config
    config = load_config()
    newer_model = model_version == 'gpt-5.4-mini/2026-03-17'
    return {'configuration_version': 'azure-gpt54mini-v1-shared-none-cap2000' if newer_model else VERSION, 'temperature': 'not sent',
            'provider_seed': 'not sent', 'max_output_tokens': config['max_tokens'],
            'reasoning_effort': 'none' if newer_model else config['reasoning_effort'],
            'max_retries': 0}
