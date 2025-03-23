import os
from dotenv import load_dotenv
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from uuid import uuid4
from datetime import datetime
import shutil

load_dotenv()

class DocumentHandler:
    def __init__(self):
        """Initialize the DocumentHandler with Chroma local vector database and Hugging Face embeddings."""
        # Set persistence directory
        self.persist_directory = "./chroma_db"
        
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize Hugging Face embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder="./model_cache"  # Cache model locally to avoid repeated downloads
        )
        
        # Initialize vector store
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print(f"Initialized Chroma vector store at {self.persist_directory}")
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            self.vector_store = None
    
    def process_document(self, uploaded_file):
        """
        Process an uploaded document (PDF or DOCX) and store embeddings in Chroma.
        
        Args:
            uploaded_file: Streamlit's UploadedFile object
            
        Returns:
            tuple: (document_id, list of text chunks)
        """
        try:
            # Create a temporary file to save the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name
            
            # Extract text based on file type
            text_chunks = []
            
            if uploaded_file.name.lower().endswith('.pdf'):
                # Process PDF
                loader = PyPDFLoader(temp_path)
                pages = loader.load()
                
                # Extract text from pages
                raw_text = ""
                for page in pages:
                    raw_text += page.page_content + "\n\n"
                
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                text_chunks = text_splitter.split_text(raw_text)
                
            elif uploaded_file.name.lower().endswith(('.docx', '.doc')):
                # Process Word document
                loader = Docx2txtLoader(temp_path)
                document = loader.load()
                
                # Extract text from document
                raw_text = ""
                for doc in document:
                    raw_text += doc.page_content + "\n\n"
                
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                text_chunks = text_splitter.split_text(raw_text)
            
            # Clean up the temp file
            os.unlink(temp_path)
            
            # Store document chunks in vector DB if chunks were extracted
            document_id = None
            if text_chunks:
                document_id = self._store_document_in_chroma(
                    filename=uploaded_file.name,
                    chunks=text_chunks
                )
            
            return document_id, text_chunks
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return None, []
    
    def _store_document_in_chroma(self, filename, chunks):
        """
        Store document chunks in Chroma vector database.
        
        Args:
            filename: Name of the uploaded file
            chunks: List of text chunks from the document
            
        Returns:
            str: Document ID for retrieval
        """
        try:
            # Generate a unique document ID
            document_id = str(uuid4())
            upload_timestamp = datetime.now().isoformat()
            
            # Show progress in Streamlit
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Initialize a new Chroma collection for this document
            chroma_client = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=document_id
            )
            
            # Add documents to vector store in batches to avoid timeout
            batch_size = 20
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                batch_metadatas = []
                
                for j, chunk in enumerate(batch):
                    # Create metadata for each chunk
                    metadata = {
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": i + j,
                        "upload_timestamp": upload_timestamp,
                        "total_chunks": len(chunks),
                    }
                    batch_metadatas.append(metadata)
                
                # Add batch to Chroma
                chroma_client.add_texts(
                    texts=batch,
                    metadatas=batch_metadatas
                )
                
                # Update progress
                progress = min(100, int(((i + len(batch)) / len(chunks)) * 100))
                progress_bar.progress(progress / 100)
                progress_text.text(f"Uploaded {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")
            
            # Persist the collection
            chroma_client.persist()
            
            # Clear progress indicators
            progress_bar.empty()
            progress_text.empty()
            
            print(f"Successfully stored document '{filename}' with {len(chunks)} chunks in Chroma")
            return document_id
            
        except Exception as e:
            print(f"Error storing document in Chroma: {str(e)}")
            return None
    
    def retrieve_document_context(self, document_id, query=None, max_chunks=5):
        """
        Retrieve context from the document stored in Chroma.
        
        Args:
            document_id: ID of the document to retrieve
            query: Optional query to use for semantic search
            max_chunks: Maximum number of chunks to retrieve
            
        Returns:
            str: Document context suitable for the LLM
        """
        try:
            # Open the specific collection for this document
            chroma_client = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=document_id
            )
            
            if query and len(query.strip()) > 0:
                # For more effective topic search, expand the query
                enhanced_query = f"Information and facts about {query}"
                
                # Semantic search within the document
                results = chroma_client.similarity_search_with_relevance_scores(
                    query=enhanced_query,
                    k=max_chunks * 2  # Retrieve more results initially for filtering
                )
                
                # Extract chunks from results
                relevant_chunks = []
                for doc, score in results:
                    # Include reasonably relevant results
                    if score > 0.5:  # Lower threshold to catch more potential matches
                        relevant_chunks.append({
                            "content": doc.page_content,
                            "index": doc.metadata.get("chunk_index", 0),
                            "relevance": score
                        })
                
                # Sort by relevance score
                relevant_chunks.sort(key=lambda x: x["relevance"], reverse=True)
                
                # Take top results up to max_chunks
                chunks_to_use = relevant_chunks[:max_chunks]
                
                # If we didn't get enough relevant chunks, fall back to document order
                if len(chunks_to_use) < max_chunks:
                    print(f"Not enough relevant chunks found for query '{query}'. Adding chunks by index order.")
                    ordered_results = self._get_chunks_by_index(chroma_client, max_chunks - len(chunks_to_use))
                    
                    # Add in chunks not already included (avoiding duplicates)
                    existing_indices = [chunk["index"] for chunk in chunks_to_use]
                    for chunk in ordered_results:
                        if chunk["index"] not in existing_indices and len(chunks_to_use) < max_chunks:
                            chunks_to_use.append(chunk)
                    
                    # Re-sort by index after adding fallback chunks
                    chunks_to_use.sort(key=lambda x: x["index"])
            else:
                # Without query, get chunks in order of index
                chunks_to_use = self._get_chunks_by_index(chroma_client, max_chunks)
            
            # Format the chunks into context
            context = "Document Content:\n\n"
            
            for i, chunk in enumerate(chunks_to_use, 1):
                # Clean up the chunk and truncate if too long
                cleaned_chunk = chunk["content"].replace('\n', ' ').strip()
                if len(cleaned_chunk) > 500:
                    cleaned_chunk = cleaned_chunk[:497] + "..."
                
                # Add relevance score if from semantic search
                if query and "relevance" in chunk:
                    relevance_percent = int(chunk["relevance"] * 100)
                    context += f"Excerpt {i} (Relevance: {relevance_percent}%): {cleaned_chunk}\n\n"
                else:
                    context += f"Excerpt {i}: {cleaned_chunk}\n\n"
            
            # Add metadata about the document
            collection_count = len(self._get_all_chunk_ids(chroma_client))
            if collection_count > max_chunks:
                context += f"[Note: Document contains {collection_count - len(chunks_to_use)} more excerpts that are not shown here]\n"
            
            return context
            
        except Exception as e:
            print(f"Error retrieving document context: {str(e)}")
            return "There was an error retrieving the document content."
    
    def _get_chunks_by_index(self, chroma_client, limit=5):
        """Get document chunks in order of their index."""
        try:
            # Get all document IDs
            chunk_ids = self._get_all_chunk_ids(chroma_client)
            
            # Limit the number of IDs to retrieve
            chunk_ids = chunk_ids[:limit]
            
            # Get the documents and metadatas
            results = chroma_client.get(
                ids=chunk_ids,
                include=["metadatas", "documents"]
            )
            
            # Extract and sort chunks by index
            chunks = []
            if results and "documents" in results and results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    metadata = results["metadatas"][i] if "metadatas" in results else {}
                    chunks.append({
                        "content": doc,
                        "index": metadata.get("chunk_index", i),
                    })
                
                # Sort by chunk index
                chunks.sort(key=lambda x: x["index"])
            
            return chunks
        except Exception as e:
            print(f"Error getting chunks by index: {str(e)}")
            return []
    
    def _get_all_chunk_ids(self, chroma_client):
        """Get all document chunk IDs."""
        try:
            # Get all document IDs
            results = chroma_client.get(include=[])
            return results.get("ids", [])
        except Exception as e:
            print(f"Error getting all chunk IDs: {str(e)}")
            return []
    
    def get_document_context(self, document_id, text_chunks=None, query=None, max_chunks=5):
        """
        Get document context for tweet generation. If document_id is provided,
        retrieves from Chroma. Otherwise, uses the provided text_chunks.
        
        Args:
            document_id: ID of the document in Chroma
            text_chunks: Optional list of text chunks (used if not yet stored in Chroma)
            query: Optional query for semantic search
            max_chunks: Maximum chunks to include
            
        Returns:
            str: Formatted context for LLM consumption
        """
        if document_id:
            return self.retrieve_document_context(document_id, query, max_chunks)
        
        # Fallback to using the provided text chunks
        if not text_chunks:
            return "No document content was extracted."
        
        # Format the chunks into context
        context = "Document Content:\n\n"
        
        chunks_to_use = text_chunks[:max_chunks]
        for i, chunk in enumerate(chunks_to_use, 1):
            # Clean up the chunk and truncate if too long
            cleaned_chunk = chunk.replace('\n', ' ').strip()
            if len(cleaned_chunk) > 500:
                cleaned_chunk = cleaned_chunk[:497] + "..."
            
            context += f"Excerpt {i}: {cleaned_chunk}\n\n"
        
        if len(text_chunks) > max_chunks:
            context += f"[Note: Document contains {len(text_chunks) - max_chunks} more excerpts that are not shown here]\n"
        
        return context 