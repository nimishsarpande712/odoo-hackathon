// Performance Cache Manager
class CacheManager {
  constructor() {
    this.cache = new Map();
    this.expiry = new Map();
    this.defaultTTL = 5 * 60 * 1000; // 5 minutes
  }

  set(key, value, ttl = this.defaultTTL) {
    this.cache.set(key, value);
    this.expiry.set(key, Date.now() + ttl);
    
    // Auto cleanup
    setTimeout(() => this.delete(key), ttl);
  }

  get(key) {
    if (!this.cache.has(key)) return null;
    
    if (Date.now() > this.expiry.get(key)) {
      this.delete(key);
      return null;
    }
    
    return this.cache.get(key);
  }

  delete(key) {
    this.cache.delete(key);
    this.expiry.delete(key);
  }

  clear() {
    this.cache.clear();
    this.expiry.clear();
  }
}

export const cache = new CacheManager();

// API Client with caching and error handling
export class ApiClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.retryCount = 3;
    this.retryDelay = 1000;
  }

  async request(endpoint, options = {}) {
    const cacheKey = `${options.method || 'GET'}_${endpoint}`;
    
    // Check cache for GET requests
    if (!options.method || options.method === 'GET') {
      const cached = cache.get(cacheKey);
      if (cached) return cached;
    }

    const url = `${this.baseURL}${endpoint}`;
    const config = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    for (let i = 0; i < this.retryCount; i++) {
      try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Cache successful GET requests
        if (!options.method || options.method === 'GET') {
          cache.set(cacheKey, data);
        }

        return data;
      } catch (error) {
        if (i === this.retryCount - 1) {
          throw new Error(`Request failed after ${this.retryCount} attempts: ${error.message}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, this.retryDelay * (i + 1)));
      }
    }
  }

  async get(endpoint) {
    return this.request(endpoint);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }
}

export const api = new ApiClient();
