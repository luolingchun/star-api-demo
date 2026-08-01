from typing import Any

from pydantic import BaseModel, Field
from rq.job import JobStatus

from app.schema import PageModel


class JobQuery(PageModel):
    status: JobStatus = Field(..., description="任务状态")


class JobResponse(BaseModel):
    id: str = Field(..., description="UUID")
    args: list[Any] = Field(description="参数")
    kwargs: dict[str, Any] = Field({}, description="关键字参数")
    result: Any = Field(None, description="结果")
    enqueued_at: str = Field("", description="入队时间")
    started_at: str = Field("", description="开始时间")
    ended_at: str = Field("", description="结束时间")
    exc_info: str = Field("", description="异常信息")
    origin: str = Field("", description="所在队列")
    job_status: str = Field("", description="状态")
    ttl: str = Field("", description="存活时间")
