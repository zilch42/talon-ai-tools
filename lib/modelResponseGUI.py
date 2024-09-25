from talon import Module, actions
from .modelState import GPTState
import markdown2

mod = Module()

class ModelResponseGUI:
    def __init__(self):
        self.ui = None

    def show_response(self, response: str):
        if self.ui:
            self.ui.hide()

        gpt_state = GPTState()
        total_in_tokens = gpt_state.total_in_tokens
        total_out_tokens = gpt_state.total_out_tokens

        html_response = markdown2.markdown(response)

        ui_elements = actions.user.ui_elements(["screen", "div", "text"])
        screen_elem, div_elem, text_elem = ui_elements

        self.ui = screen_elem(id="model_response_gui", align_items="flex_start", justify_content="flex_start")[
            div_elem(padding=20, background_color="222222", width=800, border_radius=10)[
                div_elem(id="response_content", padding_bottom=10)[
                    text_elem(html_response, color="FFFFFF")
                ],
                div_elem(padding_top=10, border_top="1px solid #444444")[
                    text_elem(f"Input tokens: {total_in_tokens}", color="AAAAAA", font_size=12),
                    text_elem(f"Output tokens: {total_out_tokens}", color="AAAAAA", font_size=12),
                    text_elem(f"Total tokens: {total_in_tokens + total_out_tokens}", color="AAAAAA", font_size=12)
                ]
            ]
        ]
        self.ui.show()

    def hide(self):
        if self.ui:
            self.ui.hide()
            self.ui = None

model_response_gui = ModelResponseGUI()

@mod.action_class
class UserActions:
    def show_model_response_gui(response: str):
        """Show the model response GUI"""
        model_response_gui.show_response(response)

    def hide_model_response_gui():
        """Hide the model response GUI"""
        model_response_gui.hide()