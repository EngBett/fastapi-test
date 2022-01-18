from pydantic import BaseModel


class Settings(BaseModel):
    authjwt_secret_key: str = '6094962256322af4a4d55dbb5d4246c5cae6710389afe7aa28e20dc9a8ef4a53'
