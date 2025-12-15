import os
import shutil
import tempfile
from typing import Optional
from fastapi import HTTPException, File, UploadFile, Form, APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from ..database import *
from ..images import object_detection

router = APIRouter(prefix="/meal", tags=["Dashboard"])


@router.get('/')
async def home():
    return HTMLResponse("""<a href="/meal/add_meal"> Go to add Meal! </a>""")


@router.get("/add_meal")
async def add_meal(
        meal_name: Optional[str] = "",
        pic_url: Optional[str] = "",
        file_type: Optional[str] = "",
        file_name: Optional[str] = "",
        weight_val: Optional[str] = "",
        kcal_val: Optional[str] = "",
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

    html = f"""
    <html>
    <body>
        <h2>User Form</h2>
        <form action="/meal/log_meal" method="get">
            Name: <input type="text" name="meal_name" value="{meal_name}" required><br>
            pic_url: <input type="text" name="pic_url" value="{pic_url}"><br>
            file_type: <input type="text" name="file_type" value="{file_type}"><br>
            file_name: <input type="text" name="file_name" value="{file_name}"><br>
            Calories: <input type="text" name="kcal_val" value="{kcal_val}" required><br>
            Weight: <input type="text" name="weight_val" value="{weight_val}" required><br>
            Protein: <input type="text" name="protein_val" value="{protein_val}"><br>
            Fat: <input type="text" name="fat_val" value="{fat_val}"><br>
            Carbs: <input type="text" name="carb_val" value="{carb_val}"><br>
            <button type="submit">Submit</button>
        </form>

        <h2>Upload Image</h2>
        <form action="/meal/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required><br>
            Weight: <input type="text" name="weight" value="" required><br>
            <button type="submit">Process Image</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(html)


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
    # data["user_id"] = 1
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

