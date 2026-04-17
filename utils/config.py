import os


class Settings:
	"""Central application settings."""

	APP_NAME = os.getenv("APP_NAME", "SwachhSaathi AI")
	DEBUG = os.getenv("DEBUG", "true").lower() == "true"
	SECRET_KEY = os.getenv("SECRET_KEY", "swachh_saathi_secret")

	MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
	MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "swachh_saathi")
	COMPLAINTS_COLLECTION = os.getenv("COMPLAINTS_COLLECTION", "complaints")
	USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

	UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
	TF_MODEL_PATH = os.getenv("TF_MODEL_PATH", "artifacts/waste_classifier.keras")
	BIN_FILL_MODEL_PATH = os.getenv("BIN_FILL_MODEL_PATH", "artifacts/bin_fill_model.joblib")

	DEFAULT_CONTACT = os.getenv("DEFAULT_CONTACT", "anonymous")
	DEFAULT_STATUS = os.getenv("DEFAULT_STATUS", "new")


settings = Settings()


def ensure_runtime_directories() -> None:
	os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
	os.makedirs(os.path.dirname(settings.TF_MODEL_PATH) or ".", exist_ok=True)