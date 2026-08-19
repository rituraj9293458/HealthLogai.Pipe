from typing_extensions import TypedDict


class HealthState(TypedDict, total=False):
    steps: str
    screen: str
    food: str

    db_data: list

    final_analysis: str

    pdf_path: str