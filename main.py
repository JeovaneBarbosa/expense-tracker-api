from fastapi import FastAPI, Path, HTTPException
from typing import Annotated 
from starlette import status
from pydantic import BaseModel, Field
from datetime import datetime

class Expense(BaseModel):
    id: int | None = Field(default=None,
                           gt=0)
    name: str = Field(min_length=2,
                      max_length=60)
    value: float = Field(ge=0)
    portions: int = Field(default=1,
                         gt=0,
                         lt=60)
    portion_value: float | None = Field(default=None,
                                        gt=0)
    date: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples":[
                {
                    "name": "Universidade",
                    "value": 230.00,
                    "portions": 6
                },
                {
                    "name": "Conta telefone",
                    "value": 60.00,
                    "portions": 1
                }
            ]
        }
    }

app = FastAPI()
db: list[Expense] = []

@app.get("/hello/{name}", status_code = status.HTTP_200_OK)
async def hello_word(name: Annotated[str, Path(min_length=3)]) -> str:
    return f"Hello {name.capitalize()}"

@app.get("/expenses", status_code=status.HTTP_200_OK)
async def get_all_expenses() -> dict[str,list[Expense]]:
    return {"Expenses": db} 

@app.get("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def get_exepense_by_id(expense_id: Annotated[int, Path(ge=0)]) -> Expense | None:
    expense = find_expense(expense_id)
    if expense:
        return expense
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No expense found with id:{expense_id}.")

@app.post("/expenses", status_code=status.HTTP_201_CREATED)
async def create_expense(expense: Expense) :
    expense = set_id(expense)
    expense = format_values(expense)
    expense = calculate_portion_value(expense)
    expense = format_time(expense)
    db.append(expense)

@app.put("/expense/{expense_id}", status_code=status.HTTP_200_OK)
async def update_expense(expense_id: Annotated[int, Path(ge=0)], expense: Expense):
    ex = find_expense(expense_id)
    if ex:
        db.remove(ex)
        expense = set_id(expense)
        expense = format_values(expense)
        expense = calculate_portion_value(expense)
        expense = format_time(expense)
        db.append(expense)
        return
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No expense with id:{expense_id} to update was found.")


@app.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: Annotated[int, Path(ge=0)]):
    for expense in db:
        if expense.id == expense_id:
            db.remove(expense)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No expense with id:{expense_id} was found.")

#Helper Methods
def set_id(expense:Expense) -> Expense:
    if len(db) == 0:
        expense.id = 1
    else:
        expense.id = db[-1].id + 1
    return expense

def calculate_portion_value(expense: Expense) -> Expense:
    expense.portion_value = round(expense.value / expense.portions, 2)
    return expense

def format_values(expense: Expense) -> Expense:
    expense.value = round(expense.value, 2)
    return expense

def format_time(expense: Expense) -> Expense:
    expense.date = datetime.now().strftime("%d/%m/%y")
    return expense

def find_expense(id: int) -> Expense | None:
    for x in db:
        if x.id == id:
            return x
    return None 