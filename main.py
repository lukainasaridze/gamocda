import csv
import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn  
#
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def is_valid(pl: str) -> bool:
    plate = pl.strip()
    if not len(plate) == 9:
        return False
    if not (plate[:2].isalpha() and plate[7:].isalpha()):
        return False
    if not (plate[:2].isupper() and plate[7:].isupper()):
        return False
    if not (plate[2] == '-' and plate[6] == '-'):
        return False
    if not plate[3:6].isdigit():
        return False
    return True

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/validate-plates/")
async def validate_plates(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="ფაილი უნდა იყოს CSV")
    content = await file.read()
    try:
        csv_input = io.StringIO(content.decode('utf-8'))
        reader = csv.reader(csv_input)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['plate', 'status'])
        for row in reader:
            if row:  
                plate = row[0].strip()
                status = 'Valid' if is_valid(plate) else 'Invalid'
                writer.writerow([plate, status])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=validated_plates.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ფაილის დამუშავების შეცდომა: {str(e)}")


