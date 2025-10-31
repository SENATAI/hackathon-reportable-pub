import os
import pandas as pd
import json
import io
import asyncio
from openai import AsyncOpenAI
from fastapi import UploadFile
from datetime import datetime, timezone
from typing import Protocol
from typing_extensions import Self


class AnalyzerServiceProtocol(Protocol):
    async def analyze(self: Self, content: bytes) -> dict:
        """
        Передаётся файл как UploadFile, прочитать можно как await file.read(), если нужно именно такое, 
        то давайте поменяем входные данные и будет не UploadFile, а bytes, потому что такая же операция проводится в другом сервисе.
        
        Обратно ожидается dict в виде таблице вида: 
        {
        "колонка1": [значение1, значение2, ...], 
        "колонка2": [значение1, значение2, ...]
        } 

        колонка1 должна иметь название такое же, как в выводящей таблице 
        """
        ...

class ExampleAnalyzerService(AnalyzerServiceProtocol):
    """
    Если __init__ будешь менять, то в depends.py тоже нужно будет поменять
    """
    async def analyze(self: Self, content: bytes) -> dict:
        return {
            "column1": ["value1", "value2"],
            "column2": ["value3", "value4"]
        }

class AnalyzerService(AnalyzerServiceProtocol):
    """
    Сервис анализа Excel-файлов с отчётами по скважинам.
    Реализует интерфейс AnalyzerServiceProtocol.
    """

    def __init__(self, api_key: str, model_url: str, prompts_path: str, schema_path: str):
        # Используем AsyncOpenAI для параллельных запросов
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://llm.api.cloud.yandex.net/v1")
        self.model_url = model_url

        # Загружаем системный промпт и JSON Schema
        with open(prompts_path, "r", encoding="utf-8") as f:
            self.prompts = json.load(f)
        self.system_prompt = self.prompts["system_prompt"]

        with open(schema_path, "r", encoding="utf-8") as f:
            self.json_schema = json.load(f)


    async def analyze(self: Self, content: bytes) -> dict:
        """
        Анализирует Excel-файл с отчётами.
        Возвращает таблицу в виде dict для вывода в интерфейсе.
        """
        # Читаем файл в байтах и создаём ExcelFile из потока
        excel = pd.ExcelFile(io.BytesIO(content))

        # --- 1️⃣ Извлекаем отчёты по датам ---
        reports = self._extract_reports(excel)

        # --- 2️⃣ Анализируем все отчёты ПАРАЛЛЕЛЬНО через LLM ---
        tasks = []
        dates_list = list(reports.keys())
        
        for date, text in reports.items():
            task = self._process_single_report(date, text)
            tasks.append(task)
        
        # Запускаем все задачи параллельно
        print(f"[INFO] Запуск параллельной обработки {len(tasks)} отчётов...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # --- 3️⃣ Собираем результаты в словарь {дата: данные} ---
        result_data = {}
        
        for i, result in enumerate(results):
            date = dates_list[i]
            
            if isinstance(result, Exception):
                print(f"[ERROR] Ошибка обработки отчёта для даты {date}: {result}")
                continue
            
            if result is not None:
                # Получаем дату начала мероприятия из результата или используем текущую
                start_event = result.get("Начало мероприятия")
                if not start_event:
                    start_event = str(datetime.now(timezone.utc).date())
                
                result_data[start_event] = result
                print(f"[SUCCESS] Отчёт для даты {date} обработан успешно")

        # Проверяем, что есть хотя бы один успешный результат
        if not result_data:
            raise ValueError("Не удалось обработать ни один отчёт из файла")

        print(f"[INFO] Успешно обработано {len(result_data)} отчётов из {len(reports)}")
        return result_data

    # -------------------------------
    # Вспомогательные методы
    # -------------------------------

    async def _process_single_report(self, date: str, text: str) -> dict | None:
        """
        Обрабатывает один отчёт. Возвращает dict или None в случае ошибки.
        """
        try:
            user_prompt = self._create_prompt(text)
            llm_response = await self._analyze_with_llm(user_prompt)
            
            try:
                data = json.loads(llm_response)
                return data
            except json.JSONDecodeError as e:
                print(f"[WARNING] Ошибка парсинга JSON для даты {date}: {e}")
                print(f"[DEBUG] Ответ LLM (первые 500 символов): {llm_response[:500]}")
                return None
        except Exception as e:
            print(f"[ERROR] Ошибка обработки отчёта для даты {date}: {e}")
            return None

    def _extract_reports(self, excel: pd.ExcelFile) -> dict[str, str]:
        sheets = excel.sheet_names
        if len(sheets) < 3:
            raise ValueError("Файл должен содержать минимум 3 листа: текущая, сводка и отчёты по датам")

        summary_df = pd.read_excel(excel, sheet_name=sheets[1], header=None)
        summary_data = {}

        # Сводка
        for _, row in summary_df.iterrows():
            if pd.notna(row[0]) and pd.notna(row[3]):
                try:
                    date = pd.to_datetime(row[0], dayfirst=True).strftime("%d.%m.%Y")
                    summary_data[date] = str(row[3]).strip()
                except Exception:
                    continue

        # Отчёты по датам
        reports = {}
        for sheet in sheets[2:]:
            df = pd.read_excel(excel, sheet_name=sheet, header=None)
            text = "\n".join(
                str(v).strip()
                for v in df.fillna("").values.flatten()
                if isinstance(v, str) and v.strip()
            )
            try:
                date = pd.to_datetime(sheet, dayfirst=True).strftime("%d.%m.%Y")
            except Exception:
                continue

            combined_text = (summary_data.get(date, "") + "\n" + text).strip()
            reports[date] = combined_text

        return reports

    def _create_prompt(self, text: str) -> str:
        return f"""
        Ниже приведён текстовый отчёт о скважине.  
        Проанализируй его и заполни все поля JSON-схемы в соответствии с данными, найденными в тексте.  
        Если какие-то данные отсутствуют — ставь пустую строку "".  
        Помни: вывод должен строго соответствовать JSON Schema и быть корректным JSON-объектом.
        
        Текст отчёта:
        {text}
        """

    async def _analyze_with_llm(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_url,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=16384,
            stream=False,
            response_format={"type": "json_schema", "json_schema": self.json_schema}
        )
        return response.choices[0].message.content