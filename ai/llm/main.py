# import openai

# messages = [
#     {"role": "system", "content": "Ты — помощник, отвечай развернуто и вежливо."}
# ]


# # Функция для отправки пользовательского сообщения и получения ответа
# def send_message(user_input):
#     # Добавляем сообщение пользователя в историю
#     messages.append({"role": "user", "content": user_input})

#     # Вызываем OpenAI ChatCompletion с полной историей
#     completion = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)

#     # Извлекаем ответ ассистента
#     assistant_reply = completion.choices[0].message.content

#     # Добавляем ответ ассистента в историю, чтобы сохранить контекст
#     messages.append({"role": "assistant", "content": assistant_reply})
#     return assistant_reply


# # Пример диалога
# print("Assistant:", send_message("Привет! Меня зовут Александр"))
# print("Assistant:", send_message("Как меня зовут?"))


OPENAI_KEY = ""

import os
import sqlite3
import json
from typing import List, Dict, Any

from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate


class TaskManager:
    def __init__(self, db_path: str = "tasks.db", llm=None):
        # Initialize DB for dev tasks
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        # Ensure API key
        api_key = OPENAI_KEY
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        # LLM setup
        self.llm = llm or OpenAI(openai_api_key=api_key, temperature=0)
        # Prompt: include CEO/business text, existing dev tasks, and new task
        self.prompt = PromptTemplate(
            input_variables=["biz_text", "tasks_json", "new_task"],
            template=(
                "CEO/business priorities:\n"
                "{biz_text}\n"
                "Existing development tasks:\n"
                "{tasks_json}\n"
                "A new dev task arrives: '{new_task}'.\n"
                "Reorder all dev tasks by business priority (1 = highest).\n"
                "Return strictly valid JSON array of objects sorted by priority. Example:\n"
                '[{{"description": "task1", "priority": 1}}, {{"description": "task2", "priority": 2}}]'
            ),
        )

    def _init_db(self) -> None:
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    priority INTEGER NOT NULL
                );
                """
            )

    def get_tasks(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, description, priority FROM tasks ORDER BY priority;")
        rows = cur.fetchall()
        return [{"id": r[0], "description": r[1], "priority": r[2]} for r in rows]

    def add_and_reprioritize(self, biz_text: str, description: str) -> Dict[str, Any]:
        """
        Add a new dev task and reprioritize all tasks based on biz_text.
        Returns {'tasks': [...], 'new_task_priority': int}.
        """
        # Fetch existing descriptions
        tasks = self.get_tasks()
        descriptions = [t["description"] for t in tasks]
        tasks_json = json.dumps(descriptions, ensure_ascii=False)
        # Call LLM with new syntax
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        resp = chain.run(biz_text=biz_text, tasks_json=tasks_json, new_task=description)
        # Parse JSON
        try:
            ordered = json.loads(resp)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM: {resp}")
        # Persist new ordering
        with self.conn:
            self.conn.execute("DELETE FROM tasks;")
            new_priority = None
            for item in ordered:
                desc = item["description"]
                pr = item["priority"]
                self.conn.execute(
                    "INSERT INTO tasks (description, priority) VALUES (?, ?);",
                    (desc, pr),
                )
                if desc == description:
                    new_priority = pr
        return {"tasks": ordered, "new_task_priority": new_priority}


if __name__ == "__main__":
    mgr = TaskManager()

    speech = """
Нам сначала сделать гостевой продукт, потом обеспечить формальности для хостов
"""
    print(
        mgr.add_and_reprioritize(
            speech, "Добавить раздел промокодов в модуле бронирования"
        )
    )
    print(
        mgr.add_and_reprioritize(
            speech,
            "Отображать отчёты доходности для хостов в интерфейсе на русском языке",
        )
    )
    print(mgr.add_and_reprioritize(speech, "Сделать лендинг – точку входа на сайт"))
