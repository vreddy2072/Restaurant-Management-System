from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = data['updated_at'].isoformat()
        return data 