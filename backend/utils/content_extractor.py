import os
import io
import csv
from typing import List, Dict, Any, Optional
from docx import Document
import pandas as pd
from werkzeug.datastructures import FileStorage


class ContentExtractor:
    """Utility class for extracting text content from various file formats"""
    
    SUPPORTED_FORMATS = {'.txt', '.csv', '.docx'}
    MAX_CHUNK_SIZE = 500  # Maximum characters per chunk
    CHUNK_OVERLAP = 100    # Overlap between chunks
    
    @classmethod
    def is_supported_format(cls, filename: str) -> bool:
        """Check if the file format is supported"""
        _, ext = os.path.splitext(filename.lower())
        return ext in cls.SUPPORTED_FORMATS
    
    @classmethod 
    def extract_content(cls, file: FileStorage) -> Dict[str, Any]:
        """
        Extract content from uploaded file
        Returns: {
            'raw_text': str,
            'chunks': List[Dict],
            'metadata': Dict
        }
        """
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        filename = file.filename.lower()
        _, ext = os.path.splitext(filename)
        
        if ext not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Reset file pointer
        file.seek(0)
        
        # Extract content based on file type
        if ext == '.txt':
            return cls._extract_txt(file)
        elif ext == '.csv':
            return cls._extract_csv(file)
        elif ext == '.docx':
            return cls._extract_docx(file)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @classmethod
    def _extract_txt(cls, file: FileStorage) -> Dict[str, Any]:
        """Extract content from text file"""
        try:
            content = file.read().decode('utf-8')
            
            metadata = {
                'file_type': 'text',
                'char_count': len(content),
                'line_count': content.count('\n') + 1
            }
            
            chunks = cls._create_text_chunks(content)
            
            return {
                'raw_text': content,
                'chunks': chunks,
                'metadata': metadata
            }
        except UnicodeDecodeError:
            # Try with different encoding
            file.seek(0)
            content = file.read().decode('latin-1')
            
            metadata = {
                'file_type': 'text',
                'char_count': len(content),
                'line_count': content.count('\n') + 1,
                'encoding': 'latin-1'
            }
            
            chunks = cls._create_text_chunks(content)
            
            return {
                'raw_text': content,
                'chunks': chunks,
                'metadata': metadata
            }
    
    @classmethod
    def _extract_csv(cls, file: FileStorage) -> Dict[str, Any]:
        """Extract content from CSV file"""
        try:
            # Read CSV content
            content = file.read().decode('utf-8')
            file.seek(0)
            
            # Parse CSV using pandas for better handling
            df = pd.read_csv(io.StringIO(content))
            
            # Convert to text representation
            text_content = df.to_string(index=False)
            
            metadata = {
                'file_type': 'csv',
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'char_count': len(text_content)
            }
            
            chunks = cls._create_text_chunks(text_content)
            
            return {
                'raw_text': text_content,
                'chunks': chunks,
                'metadata': metadata
            }
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}")
    
    @classmethod
    def _extract_docx(cls, file: FileStorage) -> Dict[str, Any]:
        """Extract content from DOCX file"""
        try:
            doc = Document(file)
            
            # Extract text from paragraphs
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text.strip())
            
            content = '\n'.join(paragraphs)
            
            metadata = {
                'file_type': 'docx',
                'paragraph_count': len(paragraphs),
                'char_count': len(content)
            }
            
            chunks = cls._create_text_chunks(content)
            
            return {
                'raw_text': content,
                'chunks': chunks,
                'metadata': metadata
            }
        except Exception as e:
            raise ValueError(f"Error processing DOCX file: {str(e)}")
    
    @classmethod
    def _create_text_chunks(cls, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks for embedding"""
        if not text.strip():
            return []
        
        chunks = []
        text_len = len(text)
        
        if text_len <= cls.MAX_CHUNK_SIZE:
            # Text is small enough to be a single chunk
            chunks.append({
                'sequence': 0,
                'text': text.strip(),
                'start_pos': 0,
                'end_pos': text_len,
                'char_count': text_len
            })
        else:
            # Split into multiple chunks with overlap
            start = 0
            sequence = 0
            
            while start < text_len:
                end = min(start + cls.MAX_CHUNK_SIZE, text_len)
                
                # Try to break at word boundary
                if end < text_len:
                    # Look for the last space or punctuation within the chunk
                    last_space = text.rfind(' ', start, end)
                    last_punct = max(
                        text.rfind('.', start, end),
                        text.rfind('!', start, end),
                        text.rfind('?', start, end)
                    )
                    
                    if last_space > start + cls.MAX_CHUNK_SIZE // 2:
                        end = last_space
                    elif last_punct > start + cls.MAX_CHUNK_SIZE // 2:
                        end = last_punct + 1
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        'sequence': sequence,
                        'text': chunk_text,
                        'start_pos': start,
                        'end_pos': end,
                        'char_count': len(chunk_text)
                    })
                    sequence += 1
                
                # Move start position with overlap consideration
                start = max(start + cls.MAX_CHUNK_SIZE - cls.CHUNK_OVERLAP, end)
                
                # Prevent infinite loop
                if start >= text_len:
                    break
        
        return chunks 