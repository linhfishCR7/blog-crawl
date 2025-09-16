import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const CreatePostPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Create Post - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Create New Post
        </Typography>
        <Typography>Post creation form will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default CreatePostPage;
