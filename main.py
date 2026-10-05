from fastapi import FastAPI,Path,HTTPException,Query 
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Literal,Annotated,Optional
import json


app = FastAPI()


class updataPatient(BaseModel):
    
    name:Annotated[Optional[str],Field(default=None)]
    
    city:Annotated[Optional[str],Field(default=None)]
    
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    
    gender:Annotated[Optional[Literal['male','female']],Field(default=None)]
    
    height:Annotated[Optional[float],Field(default=None,gt=1.0)]
    
    weight:Annotated[Optional[float],Field(default=None,gt=10)]



class Patient(BaseModel):
    
    id:Annotated[str,Field(...,description='id of the patient',examples=["p001"])]

    name:Annotated[str,Field(...,description="this is a patient name")]
    city:Annotated[str,Field(...,description="this is a city name")]
    age:Annotated[int,Field(...,gt=0,it=120,description="this is a patient age")]
    gender :Annotated[Literal["male",'female','other'],Field(...,description="this is a gender")]
    hight :Annotated[float,Field(...,gt=0.0,it=7.0,description="give me a hight in the meter")]
    weight:Annotated[float,Field(...,gt=0,it=7.0,description="give me a weight in kgs")]

@computed_field
@property
def bmi(self)->float:
    bmi=round(self.weight/self.hight**2,3)
    return bmi  

@computed_field
@property
def verdict(self)->str:


    if self.bmi<18.5 :
        return "Underweight"

    elif self.bmi<25 :
        return "Normal"

    else :
        return 'obese'


@app.post("/create")
def create(object:Patient):
    
    data=data_load()
    
    
    if object.id in data:
        raise HTTPException(status_code=404,detail="the user is alredy exist")
    
    
    
    data[object.id]=object.model_dump(exclude=['id'])

    data_save(data)

    return JSONResponse(status_code=201,content={'massage':"patient created succefully"})

@app.delete("/delete/{patient_id}")

def deletepaitent(patient_id:str=Path(...,description="please enter dele id")):
    data= data_load()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found")
    del data[patient_id]
    data_save(data)
    return JSONResponse(status_code=200,content={"message":"patient deleted"})
    

@app.put("/edit/{patient_id}")
def edit(patient_id:str,update_obj_data:updataPatient):
    
    data=data_load()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="user not found")
    update_info=update_obj_data.module_dump(exclude_unset=True)
    
    existing_data=data[patient_id]

    for key,value in update_info:
        existing_data[key]=value

    existing_data['id']=patient_id
    
    update_object=Patient(**existing_data)    

    existing_object=update_object.model_dump(exclude="id")

    data[patient_id]=existing_object

    data_save(data)

    return JSONResponse(status_code=200,contant={'massage':"data is update is sucessfully"})



def data_load():
    with open('patients.json','r') as f:
        data=  json.load(f) 
    return data

def data_save(data):
    with open("patients.json","w") as f:
        json.dump(data,f)


@app.get("/")
def hello():
    return{'massage':'patient Mangement System API'}


@app.get("/about")
def about():
    return{'message':'A fully function API to manage your patient records'}

@app.get("/view")
def view():
    data=data_load()

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str=Path(...,description="id of the patient is the db ",examples="P001")):


    data=data_load()
    
    if patient_id in data:
    
        return data[patient_id]
    raise HTTPException(status_code=404,detail="patient not found")


@app.get("/sort")
def sort_patients(sort_by:str=Query(...,description="Sort on the basis of height or bmi"),order:str=Query('asc',description='sort in asc or desc order')):

    valid_fields=['height',"weight","bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'invalid field select form {valid_fields}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='invalid order select between asc and desc')


    data=data_load()

    sort_order=True if order=="desc" else False
    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)

    return sorted_data 

