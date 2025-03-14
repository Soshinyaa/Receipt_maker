from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from tempfile import NamedTemporaryFile
from funcs import *
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

# Эндпоинт для обработки POST-запроса
@app.post("/create_receipt/")
async def calculate(data: InputData):
    try:
        # Создаем временный файл
        with NamedTemporaryFile(delete=False, suffix=".pdf"):
            temp_filename = create_receipt(data.model_dump())  # Создаем PDF во временном файле

        # Отправляем файл и удаляем его после отправки
        async def cleanup():
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    logger.info(f"Файл {temp_filename} удален.")
            except Exception as e:
                logger.error(f"Ошибка при удалении файла: {e}")

        return StreamingResponse(
            open(temp_filename, "rb"),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={temp_filename}"},
            background=cleanup
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)