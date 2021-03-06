from typing import List, Text, Dict, Any

from transformers import AutoTokenizer
from rasa.shared.nlu.training_data.message import Message
from rasa.nlu.tokenizers.tokenizer import Tokenizer, Token


class CustomBertTokenizer(Tokenizer):
    defaults = {
        # name of the language model to load.
        "model_name": "bert",
        # Pre-Trained weights to be loaded(string)
        "model_weights": None,
        # an optional path to a specific directory to download
        # and cache the pre-trained model weights.
        "cache_dir": None,
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        super(CustomBertTokenizer, self).__init__(component_config)
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.component_config["model_weights"], cache_dir=self.component_config.get("cache_dir"), use_fast=True
        )

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)
        encoded_input = self.tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)
        token_position_pair = zip(encoded_input.tokens(), encoded_input["offset_mapping"])

        return [Token(text=token_text, start=position[0], end=position[1])
                for token_text, position in token_position_pair]
