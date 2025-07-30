import os
import boto3
from werkzeug.utils import secure_filename
from uuid import uuid4

class StorageManager:
    def __init__(self, app=None):
        self.app = app
        self.storage_type = None
        self.s3_client = None
        self.local_path = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize storage manager"""
        self.app = app
        self.storage_type = app.config.get('STORAGE_TYPE', 'local')
        
        if self.storage_type == 's3':
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=app.config.get('S3_ACCESS_KEY'),
                aws_secret_access_key=app.config.get('S3_SECRET_KEY'),
                region_name=app.config.get('S3_REGION', 'us-east-1')
            )
        else:
            self.local_path = app.config.get('LOCAL_STORAGE_PATH', './uploads')
            os.makedirs(self.local_path, exist_ok=True)
    
    def save_file(self, file, workspace_id, filename=None):
        """Save file and return storage URL"""
        if not filename:
            filename = secure_filename(file.filename)
        
        # Generate unique filename
        file_id = str(uuid4())
        extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_filename = f"{file_id}.{extension}" if extension else file_id
        
        if self.storage_type == 's3':
            return self._save_to_s3(file, workspace_id, unique_filename)
        else:
            return self._save_to_local(file, workspace_id, unique_filename)
    
    def _save_to_s3(self, file, workspace_id, filename):
        """Save file to S3"""
        key = f"workspaces/{workspace_id}/files/{filename}"
        bucket = self.app.config['S3_BUCKET']
        
        try:
            self.s3_client.upload_fileobj(file, bucket, key)
            return f"s3://{bucket}/{key}"
        except Exception as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")
    
    def _save_to_local(self, file, workspace_id, filename):
        """Save file locally"""
        workspace_path = os.path.join(self.local_path, str(workspace_id))
        os.makedirs(workspace_path, exist_ok=True)
        
        file_path = os.path.join(workspace_path, filename)
        file.save(file_path)
        
        return f"local://{file_path}"
    
    def delete_file(self, storage_url):
        """Delete file from storage"""
        if storage_url.startswith('s3://'):
            return self._delete_from_s3(storage_url)
        else:
            return self._delete_from_local(storage_url)
    
    def _delete_from_s3(self, storage_url):
        """Delete file from S3"""
        # Extract bucket and key from s3://bucket/key format
        parts = storage_url[5:].split('/', 1)
        bucket, key = parts[0], parts[1]
        
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception:
            return False
    
    def _delete_from_local(self, storage_url):
        """Delete file from local storage"""
        file_path = storage_url.replace('local://', '')
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False

storage_manager = StorageManager()

def init_storage(app):
    """Initialize storage manager"""
    storage_manager.init_app(app) 