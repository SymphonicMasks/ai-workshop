from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List, Literal

from api.schemas import FeedbackRequest
from app.utils.prompts import FEEDBACK_PROMPT

class MusicFeedbackAgent:
    def __init__(self, llm):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self):
        prompt_template = ChatPromptTemplate.from_template(FEEDBACK_PROMPT)
        return (
                RunnablePassthrough.assign(
                    accuracy=lambda x: round((x["correct"] / x["total_notes"]) * 100),
                    error_details=lambda x: self._format_error_details(x["results"])
                )
                | prompt_template
                | self.llm
                | StrOutputParser()
        )

    def _format_error_details(self, results: FeedbackRequest) -> str:
        details = []
        for note in results.result:
            if note.status == "wrong":
                details.append(
                    f"Такт {note.tact_number}: Должна быть {note.original_note}, прозвучала {note.played_note}"
                )
            elif note.status == "skipped":
                details.append(
                    f"Такт {note.tact_number}: Пропущена нота {note.original_note}"
                )
            elif note.status == "duration+":
                details.append(
                    f"Такт {note.tact_number}: Нота {note.original_note} должна быть длиться {note.original_duration}, но звучала дольше"
                )
            elif note.status == "duration-":
                details.append(
                    f"Такт {note.tact_number}: Нота {note.original_note} должна была длиться {note.original_duration}, но звучала короче"
                )
        return "\n".join(details) if details else "Ошибок немного, это отличный результат!"

    def _calculate_stats(self, results: FeedbackRequest):
        results = results.result
        total = len(results)
        correct = sum(1 for note in results if note.status == "correct")
        wrong = sum(1 for note in results if note.status == "wrong")
        skipped = sum(1 for note in results if note.status == "skipped")
        duration_long = sum(1 for note in results if note.status == "duration+")
        duration_short = sum(1 for note in results if note.status == "duration-")
        return total, correct, wrong, skipped, duration_long, duration_short

    def generate_feedback(self, results: FeedbackRequest) -> str:
        if not results:
            return "Пока не собрано данных для анализа. Продолжай практиковаться!"

        total, correct, wrong, skipped, duration_long, duration_short = self._calculate_stats(results)
        print(total, correct, wrong, skipped, duration_long, duration_short)
        return self.chain.invoke({
            "results": results,
            "total_notes": total,
            "correct": correct,
            "wrong": wrong,
            "skipped": skipped,
            "duration_long": duration_long,
            "duration_short": duration_short
        })


# Пример использования
# if __name__ == "__main__":
#     from langchain_community.chat_models import ChatOpenAI

#     # Тестовые данные
#     test_results = [
#         ("C4", "C4", "correct", "1/4", 1, 0.0, 0.25),
#         ("D4", None, "skipped", "1/2", 1, 0.25, 0.75),
#         ("E4", "F4", "wrong", "1/8", 1, 0.75, 0.875),
#         ("F4", "F4", "correct", "1/8", 1, 0.875, 1.0),
#         # (None, "G4", "wrong"),  # Лишняя нота
#     ]

#     # Инициализация модели
#     llm = ChatOpenAI(model="gpt-4o-mini")
#     agent = MusicFeedbackAgent(llm)

#     # Генерация фидбека
#     feedback = agent.generate_feedback(test_results)
#     print(feedback)