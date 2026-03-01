import os
import tempfile
import polars as pl
from uuid import uuid4

class CsvRepository:
    def __init__(self, file_path: str, schema: dict):
        self.file_path = file_path
        self.schema = schema
        self._ensure_directory()
        self._initialize_file()

    def _ensure_directory(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _initialize_file(self):
        if not os.path.exists(self.file_path):
            df = pl.DataFrame(schema=self.schema)
            df.write_csv(self.file_path)

    def get_all(self) -> pl.DataFrame:
        try:
            return pl.read_csv(self.file_path, schema=self.schema)
        except Exception as e:
            raise RuntimeError(f"Read error {self.file_path}: {str(e)}")

    def save(self, df: pl.DataFrame):
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(self.file_path))
        try:
            with os.fdopen(fd, 'wb') as f:
                df.write_csv(f)
            os.replace(temp_path, self.file_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise RuntimeError(f"Save error {self.file_path}: {str(e)}")

    def append(self, record: dict):
        try:
            record["ID"] = str(uuid4())
            new_df = pl.DataFrame([record], schema=self.schema)
            current_df = self.get_all()
            updated_df = pl.concat([current_df, new_df], how="vertical")
            self.save(updated_df)
        except Exception as e:
            raise RuntimeError(f"Append error: {str(e)}")