import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
} from '@mui/material';
import { useQuery } from 'react-query';
import { format } from 'date-fns';
import { Helmet } from 'react-helmet-async';
import { useNavigate } from 'react-router-dom';

import { apiService } from '../services/api';
import { Post, PaginatedResponse } from '../types';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const { data: postsData, isLoading, error } = useQuery<PaginatedResponse<Post>>(
    'published-posts',
    () => apiService.get('/posts/?status=published').then(res => res.data),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  const posts = postsData?.results || [];

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <Typography>Loading posts...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <Typography color="error">Error loading posts</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>Blog CMS - Latest Posts</title>
        <meta name="description" content="Latest blog posts from our content management system with automated web crawling" />
      </Helmet>
      
      <Container maxWidth="lg">
        <Box mb={4}>
          <Typography variant="h2" component="h1" gutterBottom>
            Latest Posts
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Discover the latest content from our blog and curated sources
          </Typography>
        </Box>

        {posts.length === 0 ? (
          <Box textAlign="center" py={8}>
            <Typography variant="h5" gutterBottom>
              No posts available yet
            </Typography>
            <Typography color="text.secondary">
              Check back later for new content!
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {posts.map((post) => (
              <Grid item xs={12} md={6} lg={4} key={post.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {post.featured_image && (
                    <Box
                      component="img"
                      src={post.featured_image}
                      alt={post.title}
                      sx={{
                        height: 200,
                        objectFit: 'cover',
                      }}
                    />
                  )}
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {post.title}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {post.excerpt || post.content.substring(0, 150) + '...'}
                    </Typography>

                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      <Avatar
                        src={post.author.avatar}
                        alt={post.author.full_name}
                        sx={{ width: 24, height: 24 }}
                      >
                        {post.author.first_name?.[0]}
                      </Avatar>
                      <Typography variant="body2" color="text.secondary">
                        {post.source_type === 'crawled' && post.original_author
                          ? post.original_author
                          : post.author.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        •
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {format(new Date(post.created_at), 'MMM dd, yyyy')}
                      </Typography>
                    </Box>

                    <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
                      {post.category && (
                        <Chip
                          label={post.category.name}
                          size="small"
                          sx={{ backgroundColor: post.category.color, color: 'white' }}
                        />
                      )}
                      {post.source_type === 'crawled' && (
                        <Chip label="Curated" size="small" variant="outlined" />
                      )}
                      {post.tags.slice(0, 2).map((tag) => (
                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                      ))}
                    </Box>

                    <Typography variant="body2" color="text.secondary">
                      {post.reading_time} min read
                    </Typography>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => navigate(`/posts/${post.slug}`)}
                    >
                      Read More
                    </Button>
                    {post.source_type === 'crawled' && post.original_url && (
                      <Button
                        size="small"
                        href={post.original_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Original Source
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {postsData && postsData.next && (
          <Box display="flex" justifyContent="center" mt={4}>
            <Button variant="outlined" size="large">
              Load More Posts
            </Button>
          </Box>
        )}
      </Container>
    </>
  );
};

export default HomePage;
