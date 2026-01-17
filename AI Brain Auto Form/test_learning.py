from learning_core import SemanticLearner

def test_learning():
    learner = SemanticLearner(n_clusters=3)
    
    # 1. Feed Training Data (Mixed Categories)
    print("Feeding data...")
    data = [
        "Python", "Java", "C++", "Coding",     # Tech
        "Tree", "Flower", "River", "Nature",   # Nature
        "Bitcoin", "Ethereum", "Crypto", "Money" # Finance
    ]
    learner.feed_data(data)
    learner.train_model()
    
    # 2. Test Prediction
    test_words = ["Ruby", "Forest", "Dogecoin"]
    print("\n--- Predictions ---")
    for word in test_words:
        cid = learner.predict_category(word)
        print(f"'{word}' belongs to Cluster {cid}")
        
        # Check logic (Simulated Association)
        similar = learner.get_similar_items(word)
        print(f"   -> AI thinks needed context is like: {similar}")

if __name__ == "__main__":
    test_learning()
