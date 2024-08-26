class AdaptiveBaseModel:
    """Base model for adaptive encryption/decryption model"""

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f"{cls} should not be instantiated")