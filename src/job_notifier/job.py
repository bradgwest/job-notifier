import json
from typing import List, Mapping, NamedTuple


class Job(NamedTuple):
    title: str
    url: str

    def to_dict(self):
        return self._asdict()

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        return cls(**json.loads(s))


JobMap = Mapping[str, List[Job]]
