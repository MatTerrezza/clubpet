import fitz  # PyMuPDF
from openai import OpenAI
import os
import numpy as np
import faiss
import pickle
from dotenv import load_dotenv

load_dotenv()

class KnowledgeBase:
    def __init__(self):
        self.documents = []
        self.index = None
        self.embeddings = []
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def load_pdf_folder(self, folder_path="knowledge_pdfs"):
        """Загружает все PDF файлы из папки"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Создана папка {folder_path}. Добавьте туда PDF файлы с книгами по кинологии.")
            return
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        for pdf_file in pdf_files:
            self._process_pdf(os.path.join(folder_path, pdf_file))
        
        if self.documents:
            self._build_index()
            print(f"Загружено {len(self.documents)} фрагментов из {len(pdf_files)} PDF файлов")
        else:
            print("Нет документов для обработки")
    
    def _process_pdf(self, file_path):
        """Обрабатывает один PDF файл"""
        try:
            doc = fitz.open(file_path)
            filename = os.path.basename(file_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Разбиваем текст на фрагменты по 500 символов
                chunk_size = 500
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size].strip()
                    if len(chunk) > 100:  # Игнорируем очень короткие фрагменты
                        self.documents.append({
                            'text': chunk,
                            'source': filename,
                            'page': page_num + 1
                        })
            
            doc.close()
        except Exception as e:
            print(f"Ошибка обработки {file_path}: {e}")
    
    def _build_index(self):
        """Строит поисковый индекс"""
        if not self.documents:
            return
        
        # Создаем эмбеддинги для всех документов
        texts = [doc['text'] for doc in self.documents]
        
        try:
            response = self.client.embeddings.create(
                input=texts,
                model="text-embedding-ada-002"
            )
            
            self.embeddings = [np.array(item.embedding) for item in response.data]
            
            # Создаем FAISS индекс
            dimension = len(self.embeddings[0])
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(self.embeddings))
            
            print(f"Индекс создан успешно. Размерность: {dimension}")
            
        except Exception as e:
            print(f"Ошибка создания индекса: {e}")
    
    def search(self, query, top_k=3):
        """Ищет наиболее релевантные фрагменты"""
        if not self.index:
            return []
        
        try:
            # Создаем эмбеддинг для запроса
            response = self.client.embeddings.create(
                input=[query],
                model="text-embedding-ada-002"
            )
            query_embedding = np.array([response.data[0].embedding])
            
            # Ищем ближайшие соседи
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    results.append({
                        'text': self.documents[idx]['text'],
                        'source': self.documents[idx]['source'],
                        'page': self.documents[idx]['page'],
                        'distance': distances[0][i]
                    })
            
            return results
            
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []

# Глобальный экземпляр базы знаний
knowledge_base = KnowledgeBase()
