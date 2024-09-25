# This is an example settings file.
# To make changes, copy this into your user directory and remove the .example extension

settings():
    
    # Works with any API with the same schema as OpenAI's (i.e. Azure, llamafiles, etc.)
    user.model_endpoint = "https://od232800-openai-dev.openai.azure.com/openai/deployments/omni/chat/completions?api-version=2024-02-15-preview"
    user.openai_model = 'gpt-4o'
    user.model_temperature = 0.1
    user.model_system_prompt = "You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested."
    user.model_shell_default = 'cmd'
    user.model_window_width = 160
    user.model_default_destination = "window"

# Only uncomment the line below if you want experimental behavior to parse Talon files
# tag(): user.gpt_beta

# Use codeium instead of Github Copilot
# tag(): user.codeium
