from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from tempfile import NamedTemporaryFile
from funcs import *
import os
import seqlog
import logging

seqlog.log_to_seq(
   server_url=f"http://{os.environ['ip']}:5341/",
   api_key=os.environ['log_token'],
   level=logging.INFO,
   batch_size=10,
   auto_flush_timeout=10,  # seconds
   override_root_logger=True,
   json_encoder_class=json.encoder.JSONEncoder,  # Optional; only specify this if you want to use a custom JSON encoder
   support_extra_properties=True # Optional; only specify this if you want to pass additional log record properties via the "extra" argument.
)

seqlog.set_global_log_properties(
    App=os.environ['App']
)

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
        logging.info("Получен post запрос", data=data)
        # Создаем временный файл
        with NamedTemporaryFile(delete=False, suffix=".pdf"):
            temp_filename = create_receipt(data.model_dump())  # Создаем PDF во временном файле

        # Отправляем файл и удаляем его после отправки
        async def cleanup():
            try:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    logging.info("Файл {temp_filename} удален.", temp_filename=temp_filename)
            except Exception as error:
                logging.error("Ошибка при удалении файла: {error}", error=error)

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