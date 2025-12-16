import os
import shutil
import tempfile
from typing import Optional
from fastapi import HTTPException, File, UploadFile, Form, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from ..database import *
from ..images import object_detection

router = APIRouter(prefix="/meal", tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get('/')
async def home(request: Request, db: Session = Depends(get_db)):
    meals = db.query(Meals).filter(Meals.user_id == 1).all()
    return templates.TemplateResponse("meals.html", {"request": request, "meals": meals})


@router.get("/add_meal")
async def add_meal(
        request: Request,
        meal_name: Optional[str] = "",
        pic_url: Optional[str] = "",
        file_type: Optional[str] = "",
        file_name: Optional[str] = "",
        kcal_val: Optional[str] = "",
        weight_val: Optional[str] = "",
        protein_val: Optional[str] = "",
        fat_val: Optional[str] = "",
        carb_val: Optional[str] = "",
    ):

    meal_name = meal_name
    pic_url = pic_url
    file_type = file_type
    file_name = file_name
    kcal_val = kcal_val
    weight_val = weight_val
    protein_val = protein_val
    fat_val = fat_val
    carb_val = carb_val

    meal = {
        "meal_name": meal_name,
        "pic_url": pic_url,
        "file_type": file_type,
        "file_name": file_name,
        "kcal_val": kcal_val,
        "weight_val": weight_val,
        "protein_val": protein_val,
        "fat_val": fat_val,
        "carb_val": carb_val,
    }
    return templates.TemplateResponse("add_meal.html", {"request": request, "meal": meal})


@router.get("/log_meal")
# async def insert_meal(data: MealData = Depends(MealData), session: Session = Depends(get_session)):
async def insert_meal(
        meal_name: str,
        pic_url: str,
        file_type: str,
        file_name: str,
        weight_val: str,
        kcal_val: str,
        protein_val: str,
        fat_val: str,
        carb_val: str,
        db: Session = Depends(get_db)
    ):

    data = {}
    data["user_id"] = 1
    data["meal_name"] = str(meal_name)
    data["pic_url"] = pic_url
    data["file_type"] = file_type
    data["file_name"] = file_name
    data["weight_val"] = int(weight_val)
    data["kcal_val"] = int(kcal_val)
    data["protein_val"] = float(protein_val)
    data["fat_val"] = float(fat_val)
    data["carb_val"] = float(carb_val)
    print(data)
    meal_log = insert_meal_(data, db)
    return RedirectResponse(url='/meal')


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), weight: str = Form(...)):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # print(temp_file.name)
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # upload_result = imagekit.upload_file(
        #     file=open(temp_file_path, "rb"),
        #     filename=file.filename,
        #     options=UploadFileRequestOptions(use_unique_file_name=True, tags=['backend-upload'])
        # )

        # if upload_result.response_metadata.http_status_code == 200:
        #     print(upload_result.response.http_status_code)
        # print(upload_result.response.http_status_code)
        print('Image Uploaded Successfully', temp_file_path)

        detected_objects = object_detection(temp_file_path)

        # size = 150
        size = float(weight)

        nutri_values = {}
        for i in detected_objects:
            nutri_values[i] = {}
            nutri_values[i]["pic_url"] = str(temp_file_path)
            nutri_values[i]["file_type"] = str(temp_file_path)
            nutri_values[i]["file_name"] = str(temp_file_path)
            nutri_values[i]["weight_val"] = int(size)
            nutri_values[i]["kcal_val"] = int(size * 3.6)
            nutri_values[i]["protein_val"] = round(float(size / 37), 1)
            nutri_values[i]["fat_val"] = round(float(size * 0.01), 1)
            nutri_values[i]["carb_val"] = round(float(size / 28), 1)

        # print({"Objects": nutri_values})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # pass
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        file.file.close()

    url = "/meal/add_meal?"
    for name in nutri_values.keys():
        url = url + f"meal_name={name}"
        for key, val in nutri_values[name].items():
            url = url + f"&{key}={val}"
    # print(url)
    return RedirectResponse(url=url, status_code=302)


@router.get("/edit/{meal_id}")
async def edit_meal(meal_id: str, request: Request, db: Session = Depends(get_db)):
    meal_id = uuid.UUID(meal_id)
    meal = db.query(Meals).filter(Meals.id == meal_id).offset(0).limit(1).first()
    print(meal)
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    return templates.TemplateResponse("edit_meal.html", {"request": request, "meal": meal})


@router.post("/edit/{meal_id}")
async def update_meal(
    meal_id: str,
    meal_name: str = Form(...),
    weight_val: str = Form(...),
    kcal_val: int = Form(...),
    protein_val: float = Form(...),
    fat_val: float = Form(...),
    carb_val: float = Form(...),
    db: Session = Depends(get_db),
):
    meal_id = uuid.UUID(meal_id)
    meal = db.query(Meals).filter(Meals.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    meal.meal_name = meal_name
    meal.kcal_val = kcal_val
    meal.weight_val = weight_val
    meal.protein_val = protein_val
    meal.fat_val = fat_val
    meal.carb_val = carb_val
    db.commit()

    return RedirectResponse(url="/meal", status_code=302)


@router.get("/delete/{meal_id}")
async def delete_meal(meal_id: str, db: Session = Depends(get_db)):
    meal_id = uuid.UUID(meal_id)
    meal = db.query(Meals).filter(Meals.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    db.delete(meal)
    db.commit()

    return RedirectResponse(url="/meal", status_code=302)
