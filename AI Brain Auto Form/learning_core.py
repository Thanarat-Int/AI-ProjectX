import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pickle
import os

MODEL_PATH = "brain_model.pkl"

class SemanticLearner:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.is_trained = False
        self.memory = [] # Stores all text seen so far
        self.cluster_labels = {} # Map cluster_id -> Description (optional)
        
        # Load existing model if available
        self.load_model()

    def feed_data(self, text_list):
        """
        Add new text data to memory.
        """
        new_data = [t for t in text_list if t and isinstance(t, str) and len(t) > 2]
        self.memory.extend(new_data)
        # Remove duplicates while preserving order
        self.memory = list(dict.fromkeys(self.memory))
        
        # Auto-retrain if we have enough data
        if len(self.memory) > self.n_clusters * 2:
            self.train_model()

    def train_model(self):
        """
        Re-trains the definition of clusters based on current memory.
        """
        if not self.memory: return

        try:
            # 1. Vectorize
            X = self.vectorizer.fit_transform(self.memory)
            
            # 2. Cluster
            # Adjust clusters if data is small
            actual_k = min(self.n_clusters, len(self.memory))
            self.kmeans = KMeans(n_clusters=actual_k, random_state=42)
            self.kmeans.fit(X)
            
            self.is_trained = True
            self.save_model()
            print(f"🧠 [Brain] Learned {actual_k} concepts from {len(self.memory)} items.")
        except Exception as e:
            print(f"⚠️ [Brain] Learning Error: {e}")

    def predict_category(self, text):
        """
        Returns the cluster ID for a given text.
        """
        if not self.is_trained: return -1
        try:
            vec = self.vectorizer.transform([text])
            cluster_id = self.kmeans.predict(vec)[0]
            return int(cluster_id)
        except:
            return -1

    def get_similar_items(self, text, top_n=3):
        """
        Finds other items in memory that belong to the same cluster.
        """
        cid = self.predict_category(text)
        if cid == -1: return []
        
        # Find indices of this cluster
        labels = self.kmeans.labels_
        indices = [i for i, x in enumerate(labels) if x == cid]
        
        # Return random samples from this cluster
        matches = [self.memory[i] for i in indices if self.memory[i] != text]
        return matches[:top_n]

    def save_model(self):
        with open(MODEL_PATH, "wb") as f:
            pickle.dump((self.vectorizer, self.kmeans, self.memory), f)

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self.vectorizer, self.kmeans, self.memory = pickle.load(f)
                self.is_trained = True
            except:
                print("⚠️ Could not load existing brain model.")

# Global Instance
BRAIN_CORE = SemanticLearner()
