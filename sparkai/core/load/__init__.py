"""Serialization and deserialization."""
from sparkai.core.load.dump import dumpd, dumps
from sparkai.core.load.load import load, loads
from sparkai.core.load.serializable import Serializable

__all__ = ["dumpd", "dumps", "load", "loads", "Serializable"]
