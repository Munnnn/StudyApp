from pydantic import BaseModel


class MasteryDistribution(BaseModel):
    weak: int = 0
    fragile: int = 0
    developing: int = 0
    strong: int = 0


class SystemStat(BaseModel):
    system_tag: str
    total_attempts: int
    avg_typed_score: float
    recall_gap_count: int  # recognition_only attempts


class DashboardOut(BaseModel):
    total_attempts: int
    mastery_distribution: MasteryDistribution
    weakest_systems: list[SystemStat]
    weakest_topics: list[str]
    recognition_only_count: int  # typed wrong + MCQ correct
    strong_mastery_count: int
    cards_studied: int
    cards_total: int
