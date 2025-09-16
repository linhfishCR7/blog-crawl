import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const PostsPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Posts - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Posts Management
        </Typography>
        <Typography>Posts management interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default PostsPage;
