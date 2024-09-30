import os
from pathlib import Path
from talon import Context, Module
from typing import Literal

from talon import Context, Module, fs, resource

mod = Module()
ctx = Context()
mod.tag("gpt_beta", desc="Tag for enabling beta GPT commands")
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.list("customPrompt", desc="Custom user-defined GPT prompts")
# mod.list("longPrompt", desc="Custom user-defined GPT prompts contained in text files")
mod.list("modelPrompt", desc="GPT Prompts")
mod.list("model", desc="The name of the model")
mod.list("modelDestination", desc="What to do after returning the model response")
mod.list("modelSource", desc="Where to get the text from for the GPT")

# ------------------------------LONG PROMPTS------------------------------------------
mod.list("longPrompt", desc="Custom user-defined GPT prompts contained in text files")

LONG_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "GPT", "lists", "long-prompts")

def read_text_file(filepath):
    base_name = os.path.basename(filepath)
    key, _ = os.path.splitext(base_name)
    key = key.replace("-", " ")
    print("importing " + key)

    with open(filepath, 'r', encoding='utf-8') as file:
        file_contents = file.read()
    return {key: file_contents}

def update_long_prompts(folder_path):
    """Read all long prompt text files and add to dict with filename as key"""
    prompt_list = {}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            full_path = os.path.join(folder_path, filename)
            next_prompt = read_text_file(filepath=full_path)
            prompt_list.update(next_prompt)
    
    ctx.lists['self.longPrompt'] = prompt_list

# # do on initial load
update_long_prompts(LONG_PROMPT_DIR)

def on_change(path, flags):
    """Actions to perform when prompts change"""
    update_long_prompts(LONG_PROMPT_DIR)

# register file watch
fs.watch(LONG_PROMPT_DIR, on_change)

#---------------------------------------------------------------------------------

# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(
    rule="{user.staticPrompt} | {user.customPrompt} | {user.longPrompt} | (please <user.text>) | (ask <user.text>)"
)
def modelPrompt(matched_prompt) -> str:
    return str(matched_prompt)


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="{user.staticPrompt} | {user.customPrompt}")
def modelSimplePrompt(matched_prompt) -> str:
    return str(matched_prompt)


mod.setting(
    "openai_model",
    type=Literal["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"],  # type: ignore
    default="gpt-4o-mini",
)

mod.setting(
    "model_temperature",
    type=float,
    default=0.6,
    desc="The temperature of the model. Higher values make the model more creative.",
)

mod.setting(
    "model_default_destination",
    type=str,
    default="paste",
    desc="The default insertion destination. This can be overridden contextually to provide application level defaults.",
)

mod.setting(
    "model_endpoint",
    type=str,
    default="https://api.openai.com/v1/chat/completions",
    desc="The endpoint to send the model requests to",
)

mod.setting(
    "model_system_prompt",
    type=str,
    default="You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested. If the user requests code generation, output just code and not additional natural language explanation.",
    desc="The default system prompt that informs the way the model should behave at a high level",
)


mod.setting(
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands",
)

mod.setting(
    "model_window_width",
    type=int,
    default=160,
    desc="The default width for the window destination",
)
