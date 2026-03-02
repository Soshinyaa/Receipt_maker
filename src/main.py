from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from tempfile import NamedTemporaryFile
from funcs import *
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Модели для входных данных
class PaymentData(BaseModel):
    Payer: str
    PayerAddress: Optional[str] = ""
    Purpose: str
    PayerInn: Optional[str] = ""
    SumPayment: int
    SumService: int
    SumTotal: int
    Date: Optional[str] = ""
    QrCodeText: str

class GroupData(BaseModel):
    Group: str
    Data: List[PaymentData]

class InputData(BaseModel):
    Filename: Optional[str] = ""
    BankTitle: str
    Org: str
    OrgInn: str
    AccNumb: str
    Bankname: str
    BankBic: str
    Data: List[GroupData]

def _cleanup_file(path: str) -> None:
    """Удаление временного файла PDF."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Файл {path} удален.")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {path}: {e}")


# Эндпоинт для обработки POST-запроса
# Поддерживаем оба варианта пути: со слэшем и без
@app.post("/create_receipt")
@app.post("/create_receipt/")
async def calculate(data: InputData, background_tasks: BackgroundTasks):
    try:
        # Создаем временный файл для PDF
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            temp_filename = tmp.name

        # Генерируем квитанции.
        # ВАЖНО: create_receipt может перезаписать FilePDF на основе поля Filename
        # во входном JSON и возвращает фактический путь к созданному файлу.
        pdf_path = create_receipt(data.model_dump(), FilePDF=temp_filename)

        if not isinstance(pdf_path, str) or not os.path.exists(pdf_path):
            # create_receipt может вернуть строку-ошибку вместо пути
            logger.error(f"PDF файл не был создан: {pdf_path!r}")
            raise HTTPException(
                status_code=400,
                detail=f"Не удалось сформировать квитанции: {pdf_path}",
            )

        # Удаляем фактический файл после отправки ответа
        background_tasks.add_task(_cleanup_file, pdf_path)
        # Если create_receipt вернул другой путь (из Filename), то удаляем и исходный temp-файл
        if os.path.abspath(pdf_path) != os.path.abspath(temp_filename):
            background_tasks.add_task(_cleanup_file, temp_filename)

        return StreamingResponse(
            open(pdf_path, "rb"),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename=\"receipt.pdf\"'},
            background=background_tasks,
        )

    except HTTPException:
        # Уже подготовленный HTTPException пробрасываем как есть
        raise
    except Exception as e:
        logger.exception("Ошибка при формировании квитанций")
        raise HTTPException(status_code=400, detail=str(e))

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)