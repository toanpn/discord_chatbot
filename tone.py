class PromptBase:
    base_instruction = "Bạn là trợ lý AI nói tiếng Việt. Hãy trả lời ngắn gọn và hữu ích."
    def get_prompt(self) -> str:
        return f"{self.base_instruction}\n{self.tone_instruction()}"
    def tone_instruction(self) -> str:
        return ""

class VeryFlatteryPrompt(PromptBase):
    def tone_instruction(self) -> str:
        return "Bạn phải hết sức nịnh nọt, khen ngợi người dùng bằng lời lẽ nhiệt tình thái quá."

class FlatteryPrompt(PromptBase):
    def tone_instruction(self) -> str:
        return "Bạn nên khen ngợi nhẹ nhàng và giữ thái độ tích cực."

class NeuterPrompt(PromptBase):
    def tone_instruction(self) -> str:
        return "Bạn trả lời trung tính, không bộc lộ cảm xúc."

class ElegantPrompt(PromptBase):
    def tone_instruction(self) -> str:
        return "Bạn trả lời lịch thiệp, tinh tế và có tính thẩm mỹ."

class NoblePrompt(PromptBase):
    def tone_instruction(self) -> str:
        return "Bạn sử dụng phong cách trang trọng và triết lý cao quý."

tone_strategies = {
    1: VeryFlatteryPrompt(),
    2: FlatteryPrompt(),
    3: NeuterPrompt(),
    4: ElegantPrompt(),
    5: NoblePrompt(),
}

tone_names = {
    1: "Very Flattery",
    2: "Flattery",
    3: "Neuter",
    4: "Elegant",
    5: "Noble",
}

def get_prompt(level: int) -> str:
    strategy = tone_strategies.get(level, NeuterPrompt())
    return strategy.get_prompt()
