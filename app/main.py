from enum import Enum

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from .config import get_settings


class OpenApiTag(Enum):
    GENERATION = "Generation"


app = FastAPI(
    title="Memoire AI",
    version="0.1.0",
    openapi_tags=[
        {
            "name": OpenApiTag.GENERATION,
            "description": "주어진 문장을 개선한 새로운 문장을 생성",
        }
    ],
)

client = AsyncOpenAI(api_key=get_settings().OPENAI_API_KEY)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


class SentenceGenerationBody(BaseModel):
    sentence: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"sentence": "안녕하세요. 만나서 반갑습니다. 커피라도 한 잔 하실래요?"}
            ]
        }
    }


class SentenceGenerationResponse(BaseModel):
    result: str


class CustomError(BaseModel):
    detail: str


@app.post(
    "/new-sentence",
    tags=[OpenApiTag.GENERATION],
    response_model=SentenceGenerationResponse,
    name="표현력 개선 문장 생성",
    description="GPT-4 Turbo를 이용해 주어진 문장의 표현력을 개선한 새로운 문장을 생성합니다.",
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/json": {
                    "example": {
                        "result": "반갑습니다! 우리의 만남을 커피 한 잔으로 기념해볼까요?"
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": CustomError,
            "description": "150자를 초과하는 문장을 넣은 경우",
            "content": {
                "application/json": {
                    "example": {"detail": "150자 이하의 문장만 허용합니다."}
                }
            },
        },
    },
)
async def get_new_sentence(sentenceGenerationBody: SentenceGenerationBody):
    sentence = sentenceGenerationBody.sentence
    if len(sentence) > 150:
        raise JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CustomError(detail="150자 이하의 문장만 허용합니다."),
        )

    response = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": "당신은 주어진 문장을 개선해서 알려주는 작문 전문가입니다. 답변은 개선된 문장만 포함하면 됩니다.",
            },
            {
                "role": "user",
                "content": f"다음 문장을 표현력 측면에서 개선해 주세요: {sentence}",
            },
        ],
    )
    return SentenceGenerationResponse(result=response.choices[0].message.content)
