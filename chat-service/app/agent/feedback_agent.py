from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List, Tuple


# from app.utils.prompts import FEEDBACK_PROMPT

class MusicFeedbackAgent:
    def __init__(self, llm):
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self):
        prompt_template = ChatPromptTemplate.from_template(
            """Ты - добрый и поддерживающий музыкальный преподаватель-робот. Дай фидбек ребенку по игре на инструменте.

            Статистика выполнения:
            Общее количество нот: {total_notes}
            Правильно сыгранных нот: {correct} ({accuracy}%)
            Ошибок: {wrong}
            Пропущенных нот: {skipped}

            Детали ошибок:
            {error_details}

            Начни с позитивной поддержки, затем дай конкретные советы по улучшению. 
            Используй простой язык, понятный ребенку. Избегай технических терминов.
            Сосредоточься на 2-3 самых важных улучшениях."""
        )

        return (
                RunnablePassthrough.assign(
                    accuracy=lambda x: round((x["correct"] / x["total_notes"]) * 100),
                    error_details=lambda x: self._format_error_details(x["results"])
                )
                | prompt_template
                | self.llm
                | StrOutputParser()
        )

    def _format_error_details(self, results: List[Tuple]) -> str:
        details = []
        for i, (original, played, status) in enumerate(results, 1):
            if status == 'wrong':
                details.append(f"Такт {i}: Должна быть {original}, прозвучала {played}")
            elif status == 'skipped':
                details.append(f"Такт {i}: Пропущена нота {original}")
        return "\n".join(details) if details else "Ошибок немного, это отличный результат!"

    def _calculate_stats(self, results):
        total = len(results)
        correct = sum(1 for _, _, status in results if status == 'correct')
        wrong = sum(1 for _, _, status in results if status == 'wrong')
        skipped = sum(1 for _, _, status in results if status == 'skipped')
        return total, correct, wrong, skipped

    def generate_feedback(self, results: List[Tuple]) -> str:
        if not results:
            return "Пока не собрано данных для анализа. Продолжай практиковаться!"

        total, correct, wrong, skipped = self._calculate_stats(results)

        return self.chain.invoke({
            "results": results,
            "total_notes": total,
            "correct": correct,
            "wrong": wrong,
            "skipped": skipped
        })


# Пример использования
# if __name__ == "__main__":
#     from langchain_community.chat_models import ChatOpenAI
#
#     # Тестовые данные
#     test_results = [
#         ("C4", "C4", "correct"),
#         ("D4", None, "skipped"),
#         ("E4", "F4", "wrong"),
#         ("F4", "F4", "correct"),
#         (None, "G4", "wrong"),  # Лишняя нота
#     ]
#
#     # Инициализация модели
#     llm = ChatOpenAI(model="gpt-4o-mini")
#     agent = MusicFeedbackAgent(llm)
#
#     # Генерация фидбека
#     feedback = agent.generate_feedback(test_results)
#     print(feedback)