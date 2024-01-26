from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi.responses import FileResponse
import pandas as pd
from io import BytesIO


app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get('/')
def root():
    return ('Welcome to the Dog Service!')


@app.post('/post')
def post() -> Timestamp:
    curr_time = datetime.now().timestamp()
    time = Timestamp(id=len(post_db), timestamp=int(curr_time))
    post_db.append(time)
    return time


@app.get('/dog')
def get_dogs(kind: DogType = None) -> List[Dog]:
    if kind is None:
        return list(dogs_db.values())
    list_dogs = []
    for dog in dogs_db.values():
        if dog.kind == kind:
            list_dogs.append(dog)
    return list_dogs


@app.post('/dog')
def create_dog(dog: Dog) -> Dog:
    if dog.pk in dogs_db:
        raise HTTPException(status_code=404, detail='This dog already exists!')
    dogs_db[dog.pk] = dog
    return dog


@app.get('/dog/{pk}')
def get_dog_by_pk(pk: int) -> Dog:
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail='This pk does not exist!')
    return dogs_db[pk]


@app.patch('/dog/{pk}')
def update_dog(pk: int, dog: Dog) -> Dog:
    if pk not in dogs_db:
        raise HTTPException(status_code=404, detail='This pk does not exist!')
    if pk != dog.pk:
        raise HTTPException(status_code=404, detail='Pk does not match')
    dogs_db[pk] = dog
    return dog


@app.get('/get_csv')
def get_csv() -> FileResponse:
    dog_list = [vars(dog) for dog in dogs_db.values()]
    df = pd.DataFrame(dog_list)
    df.to_csv('all_dogs.csv')
    response = FileResponse(path='all_dogs.csv', media_type='text/csv', filename='all_dogs_download.csv')
    return response


@app.post('/upload_file')
def upload(file: UploadFile):
    return file.file.read()


@app.post('/upload_csv')
def upload_csv(file: UploadFile):
    content = file.file.read() # считываем байтовое содержимое
    buffer = BytesIO(content) # создаем буфер типа BytesIO
    df = pd.read_csv(buffer, index_col=0)
    buffer.close()
    file.close()  # закрывается именно сам файл
    # на самом деле можно не вызывать .close(), тк питон сам освобождает память при уничтожении объекта
    # но это просто хорошая практика, так гарантируется корректное освобождение ресурсов
    df.index = df.index + max(dogs_db)
    df['pk'] = df.index
    return df.to_dict(orient='index')







