import os
import pytest

os.environ.setdefault("DB_NAME", "cinema_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key")