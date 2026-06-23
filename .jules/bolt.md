## 2025-01-24 - [Vectorization of texture processing]
**Learning:** Replacing manual loops for pixel-by-pixel processing with NumPy vectorized operations (like `.reshape`, indexing with channel lists, and `np.interp`) provides a massive performance boost (60x in this case) while often making the code more concise.
**Action:** Always look for manual loops over image/vertex data and consider if they can be replaced by NumPy operations.
