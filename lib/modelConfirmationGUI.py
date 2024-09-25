from talon import Context, Module, actions, clip, imgui, settings
from .modelHelpers import GPTState, extract_message, notify

mod = Module()
ctx = Context()

class ConfirmationGUIState:
    display_thread = False
    last_item_text = ""

    @classmethod
    def update(cls):
        cls.display_thread = "USER" in GPTState.text_to_confirm and "GPT" in GPTState.text_to_confirm
        if not GPTState.thread:
            cls.last_item_text = ""
            return

        last_message_item = GPTState.thread[-1]["content"][0]
        cls.last_item_text = last_message_item.get("text", "")

@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()

    ConfirmationGUIState.update()

    max_width = settings.get("user.model_window_width")
    wrapped_text = wrap_text(GPTState.text_to_confirm, max_width)
    
    for line in wrapped_text.split("\n"):
        gui.text(line)

    gui.spacer()
    buttons = [
        ("Chain response", actions.user.confirmation_gui_paste),
        ("Pass response to context", actions.user.confirmation_gui_pass_context),
        ("Pass response to thread", actions.user.confirmation_gui_pass_thread),
        ("Copy response", actions.user.confirmation_gui_copy),
        ("Paste response", actions.user.confirmation_gui_paste),
        ("Discard response", actions.user.confirmation_gui_close)
    ]

    for label, action in buttons:
        gui.spacer()
        if gui.button(label):
            action()

def wrap_text(text, width):
    """Wrap text to fit within a specified width."""
    wrapped_lines = []
    for line in text.split('\n'):
        while len(line) > width:
            split_index = line.rfind(' ', 0, width)
            if split_index == -1:  # No spaces found, force split
                split_index = width
            wrapped_lines.append(line[:split_index])
            line = line[split_index:].lstrip()
        wrapped_lines.append(line)
    return '\n'.join(wrapped_lines)

@mod.action_class
class UserActions:
    def confirmation_gui_append(model_output: str):
        """Add text to the confirmation gui"""
        ctx.tags = ["user.model_window_open"]
        GPTState.text_to_confirm = model_output
        confirmation_gui.show()

    def confirmation_gui_close():
        """Close the model output without pasting it"""
        GPTState.text_to_confirm = ""
        confirmation_gui.hide()
        ctx.tags = []

    def confirmation_gui_pass_context():
        """Add the model output to the context"""
        actions.user.gpt_push_context(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_pass_thread():
        """Add the model output to the thread"""
        actions.user.gpt_push_thread(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_copy():
        """Copy the model output to the clipboard"""
        text_to_set = GPTState.text_to_confirm if not ConfirmationGUIState.display_thread else ConfirmationGUIState.last_item_text
        clip.set_text(text_to_set)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_paste():
        """Paste the model output"""
        text_to_set = GPTState.text_to_confirm if not ConfirmationGUIState.display_thread else ConfirmationGUIState.last_item_text
        if not text_to_set:
            notify("GPT error: No text in confirmation GUI to paste")
        else:
            actions.user.paste(text_to_set)
            GPTState.last_response = text_to_set
            GPTState.last_was_pasted = True
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_refresh_thread(force_open: bool = False):
        """Refresh the threading output in the confirmation GUI"""
        formatted_output = "\n".join(
            f"{'GPT' if msg['role'] == 'assistant' else 'USER'}: {extract_message(item)}"
            for msg in GPTState.thread for item in msg["content"]
        )
        GPTState.text_to_confirm = formatted_output
        ctx.tags = ["user.model_window_open"]
        if confirmation_gui.showing or force_open:
            confirmation_gui.show()
