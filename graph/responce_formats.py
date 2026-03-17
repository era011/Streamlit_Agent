from pydantic import BaseModel

class planner_response(BaseModel):
    route: str
    plan: list[str]

class evaluator_response(BaseModel):
    evaluation: bool    