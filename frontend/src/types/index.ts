// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  bio: string;
  avatar?: string;
  is_verified: boolean;
  profile?: UserProfile;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  website?: string;
  twitter?: string;
  github?: string;
  linkedin?: string;
  location?: string;
  birth_date?: string;
  email_notifications: boolean;
  newsletter_subscription: boolean;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// Blog types
export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
  post_count: number;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  author: User;
  category?: Category;
  category_id?: number;
  tags: string[];
  status: 'draft' | 'published' | 'archived' | 'pending';
  source_type: 'original' | 'crawled';
  is_featured: boolean;
  meta_title: string;
  meta_description: string;
  featured_image?: string;
  reading_time: number;
  comment_count: number;
  published_at?: string;
  created_at: string;
  updated_at: string;
  original_url?: string;
  original_author?: string;
  original_published_date?: string;
}

export interface Comment {
  id: number;
  post: number;
  author: User;
  content: string;
  parent?: number;
  replies: Comment[];
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

// Crawler types
export interface CrawlSource {
  id: number;
  name: string;
  url: string;
  description: string;
  schedule: 'manual' | 'hourly' | 'daily' | 'weekly' | 'monthly';
  is_active: boolean;
  status: 'active' | 'inactive' | 'error';
  content_selector: string;
  title_selector: string;
  author_selector: string;
  date_selector: string;
  max_pages: number;
  delay_between_requests: number;
  follow_links: boolean;
  include_patterns: string;
  exclude_patterns: string;
  include_patterns_list: string[];
  exclude_patterns_list: string[];
  created_by: User;
  created_at: string;
  updated_at: string;
  last_crawled_at?: string;
  total_crawls: number;
  successful_crawls: number;
  failed_crawls: number;
  total_posts_found: number;
  success_rate: number;
}

export interface CrawlJob {
  id: number;
  source: CrawlSource;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  started_at?: string;
  completed_at?: string;
  duration?: string;
  pages_crawled: number;
  posts_found: number;
  posts_created: number;
  posts_updated: number;
  duplicates_found: number;
  errors_count: number;
  log_data: any[];
  error_message: string;
  triggered_by?: User;
  created_at: string;
  is_running: boolean;
}

export interface CrawledContent {
  id: number;
  crawl_job: CrawlJob;
  source_url: string;
  title: string;
  content: string;
  author: string;
  published_date?: string;
  status: 'pending' | 'approved' | 'rejected' | 'processed';
  content_hash: string;
  similarity_score?: number;
  extracted_metadata: any;
  processed_by?: User;
  processed_at?: string;
  blog_post?: number;
  created_at: string;
  updated_at: string;
  is_duplicate: boolean;
}

// API response types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
}
