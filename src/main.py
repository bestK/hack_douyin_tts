import base64
import json
from urllib.parse import unquote

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src import config
from src import utils

load_dotenv()

conf = config.TTS_CONFIG()
logger = config.get_logger()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


class TTSRequest(BaseModel):
    text: str = Query("text", description="待转换文本")
    format: str = Query("sil", description="音频格式(mp3/sil) 默认sil")
    zbid: str = Query("5ea5a236a0b67106", description="主播id默认熊二")


class TTSResponse(BaseModel):
    data: str = Query("base64", description="音频base64")
    voice_ms: int = Query(0, deprecated="音频时间 单位ms")


@app.post("/tts")
def tts(request: TTSRequest) -> TTSResponse:
    tts_resp = TTSResponse()

    if not request.text:
        raise HTTPException(status_code=400, detail="Text must not be empty")

    try:
        plaintText, body = utils.encrypted_params(
            text=request.text, zbid=request.zbid, conf=conf
        )
        logger.debug(plaintText)

        resp = fetch(conf.api_url, body=body, resp_key=conf.api_res_key)
        logger.debug(resp)

        success = resp["rc"] == "0"

        if success is False:
            raise HTTPException(400, detail="Ops! server has some error")
        else:
            model = resp["model"]
            tts_resp.voice_ms = model["ttstime"] * 1000

            tts_resp.data = fetch_to_base64(model["audiourl"])
            if request.format == "sil":
                tts_resp.data = sil_encoder(tts_resp.data)

        return tts_resp
    except Exception as e:
        logger.error(e)
        raise HTTPException(500, detail="Internal Server Error")


def fetch(url, body, resp_key):
    api = requests.post(
        url,
        data=body,
        headers={
            "content-type": "application/x-www-form-urlencoded",
            "x-forwarded-for": utils.random_ip(),
        },
    )

    res = unquote(api.text.replace("resp=", "").split("&sec")[0])
    decryptedData = utils.decrypt_aes_ecb(res, resp_key)
    return json.loads(decryptedData)


def fetch_to_base64(url) -> str:
    response = requests.get(url)

    if response.status_code == 200:
        file_content = response.content
        base64_content = base64.b64encode(file_content).decode()
        return base64_content
    else:
        print("Failed to download the file.")
        return None


def sil_encoder(file_base64) -> str:
    url = "https://tosilk.zeabur.app/v1/encoder"
    body = {"base64": file_base64}
    resp = requests.post(url, json=body)
    if resp.status_code == 200:
        return resp.json()["data"]
    return None


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    error_msg = exc.detail
    status_code = exc.status_code

    return JSONResponse(content={"error": error_msg}, status_code=status_code)
