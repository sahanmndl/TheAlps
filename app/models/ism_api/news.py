from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime

class ISMNewsArticle(BaseModel):
    title: str
    summary: str
    url: HttpUrl
    image_url: Optional[HttpUrl]
    pub_date: datetime
    source: str
    topics: List[str] = Field(default_factory=list)

    @field_validator('pub_date', mode='before')
    @classmethod
    def parse_pub_date(cls, v):
        """Parse the pub_date string to datetime object"""
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if 'url' in data:
            data['url'] = str(data['url'])
        if 'image_url' in data and data['image_url'] is not None:
            data['image_url'] = str(data['image_url'])
        if 'pub_date' in data and data['pub_date'] is not None:
            data['pub_date'] = data['pub_date'].isoformat()
        return data
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            HttpUrl: str
        }