import csv
import io
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
app = FastAPI(title="Student Manager API")
students = []

class StudentInput(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    age: int = Field(ge=3, le=100)
    course: str = Field(min_length=1)
    marks: float = Field(ge=0, le=100)

class GradeInput(BaseModel):
    marks: float = Field(ge=0, le=100)

def calculate_grade(marks):
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    if marks >= 50: return "D"
    return "F"

def make_student(data):
    return {"id": data.id.strip(), "name": data.name.strip(), "age": data.age,
            "course": data.course.strip(), "marks": data.marks,
            "grade": calculate_grade(data.marks)}

def find_student(student_id):
    return next((student for student in students if student["id"] == student_id), None)

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/api/students")
def list_students(search: str = ""):
    query = search.strip().lower()
    return [student for student in students if not query or query in " ".join(str(value) for value in student.values()).lower()]

@app.post("/api/students", status_code=201)
def add_student(data: StudentInput):
    if find_student(data.id.strip()):
        raise HTTPException(409, "That student ID already exists.")
    student = make_student(data)
    students.append(student)
    return student

@app.put("/api/students/{student_id}")
def update_student(student_id: str, data: StudentInput):
    student = find_student(student_id)
    if not student:
        raise HTTPException(404, "Student not found.")
    if data.id.strip() != student_id and find_student(data.id.strip()):
        raise HTTPException(409, "That student ID already exists.")
    student.update(make_student(data))
    return student

@app.delete("/api/students/{student_id}")
def delete_student(student_id: str):
    student = find_student(student_id)
    if not student:
        raise HTTPException(404, "Student not found.")
    students.remove(student)
    return {"message": "Student deleted."}

@app.post("/api/grade")
def grade(data: GradeInput):
    return {"marks": data.marks, "grade": calculate_grade(data.marks)}

@app.get("/api/reports")
def reports():
    marks = [student["marks"] for student in students]
    distribution = {}
    for student in students:
        distribution[student["grade"]] = distribution.get(student["grade"], 0) + 1
    return {"total": len(students), "average": round(sum(marks) / len(marks), 1) if marks else 0,
            "highest": max(marks, default=0), "lowest": min(marks, default=0),
            "pass_rate": round(sum(mark >= 50 for mark in marks) / len(marks) * 100, 1) if marks else 0,
            "distribution": distribution}

@app.get("/api/students.csv")
def save_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "age", "course", "marks", "grade"])
    writer.writeheader()
    writer.writerows(students)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=students.csv"})

@app.post("/api/students.csv")
async def load_csv(file: UploadFile = File(...)):
    try:
        rows = list(csv.DictReader(io.StringIO((await file.read()).decode("utf-8-sig"))))
        required = {"id", "name", "age", "course", "marks"}
        if not rows or not required.issubset(rows[0]):
            raise ValueError("CSV must contain id, name, age, course, and marks columns.")
        imported, ids = [], set()
        for row in rows:
            data = StudentInput(id=str(row["id"]).strip(), name=str(row["name"]).strip(),
                                age=int(row["age"]), course=str(row["course"]).strip(),
                                marks=float(row["marks"]))
            if data.id in ids:
                raise ValueError(f"Duplicate student ID: {data.id}")
            ids.add(data.id)
            imported.append(make_student(data))
        students.clear()
        students.extend(imported)
        return students
    except (UnicodeDecodeError, ValueError, TypeError) as error:
        raise HTTPException(400, f"Could not read CSV: {error}") from error

app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")
