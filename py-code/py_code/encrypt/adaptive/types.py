from dataclasses import dataclass

from pydantic import BaseModel, model_validator


@dataclass
class AdaptiveCipherParams:
    # p, q, r here represents the byte to be taken from the float32
    p: int
    q: int
    r: int

    @model_validator(mode="before")
    def validate_fields(self):
        assert len(set([self.p, self.q, self.r])) == 3  # check p, q, r are distinct
        assert (
            self.p > self.q > self.r
        )  # r must be least significant byte of the 3, p the most significant


class SBlocks(BaseModel):
    s1: bytes
    s2: bytes
    s3: bytes
